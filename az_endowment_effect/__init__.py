from otree.api import *

doc = """
Endowment effect game with one seller and one buyer.
The seller reports a minimum willingness-to-accept (WTA) to part with the mug.
The buyer reports a maximum willingness-to-pay (WTP).
If WTP meets or exceeds WTA, the trade clears at the midpoint price.
"""


class C(BaseConstants):
    NAME_IN_URL = "endowment_effect"
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    CASH_ENDOWMENT = cu(50)
    MUG_VALUE_TO_SELLER = cu(80)
    MUG_VALUE_TO_BUYER = cu(100)
    PRICE_MIN = cu(0)
    PRICE_MAX = cu(150)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    ask_price = models.CurrencyField(
        min=C.PRICE_MIN,
        max=C.PRICE_MAX,
        label="Minimum price to sell the mug",
    )
    bid_price = models.CurrencyField(
        min=C.PRICE_MIN,
        max=C.PRICE_MAX,
        label="Maximum price to buy the mug",
    )
    trade_price = models.CurrencyField(initial=cu(0))
    traded = models.BooleanField(initial=False)


class Player(BasePlayer):
    pass


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        subsession.group_randomly()


def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.PLAYERS_PER_GROUP


class Unmatched(Page):
    template_name = "global/Unmatched.html"

    @staticmethod
    def is_displayed(player: Player):
        return is_unmatched(player) and player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(required_size=C.PLAYERS_PER_GROUP)

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return upcoming_apps[0] if upcoming_apps else None


def seller_role(player: Player):
    return "Seller" if player.id_in_group == 1 else "Buyer"


def set_payoffs(group: Group):
    seller = group.get_player_by_id(1)
    buyer = group.get_player_by_id(2)

    group.traded = group.bid_price >= group.ask_price
    group.trade_price = (group.ask_price + group.bid_price) / 2 if group.traded else cu(0)

    if group.traded:
        seller.payoff = C.CASH_ENDOWMENT + group.trade_price
        buyer.payoff = C.CASH_ENDOWMENT + C.MUG_VALUE_TO_BUYER - group.trade_price
    else:
        seller.payoff = C.CASH_ENDOWMENT + C.MUG_VALUE_TO_SELLER
        buyer.payoff = C.CASH_ENDOWMENT


class Introduction(Page):
    pass


class Ask(Page):
    form_model = "group"
    form_fields = ["ask_price"]

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            role=seller_role(player),
            page_title="Seller valuation",
            prompt="Enter the minimum price you require to give up the mug.",
            reference_value=C.MUG_VALUE_TO_SELLER,
            cash_endowment=C.CASH_ENDOWMENT,
        )

    @staticmethod
    def error_message(player: Player, values):
        if values["ask_price"] < C.PRICE_MIN or values["ask_price"] > C.PRICE_MAX:
            return "Enter a price within the allowed range."


class Bid(Page):
    form_model = "group"
    form_fields = ["bid_price"]

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            role=seller_role(player),
            page_title="Buyer valuation",
            prompt="Enter the maximum price you are willing to pay for the mug.",
            reference_value=C.MUG_VALUE_TO_BUYER,
            cash_endowment=C.CASH_ENDOWMENT,
        )

    @staticmethod
    def error_message(player: Player, values):
        if values["bid_price"] < C.PRICE_MIN or values["bid_price"] > C.PRICE_MAX:
            return "Enter a price within the allowed range."


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        seller = group.get_player_by_id(1)
        buyer = group.get_player_by_id(2)
        return dict(
            role=seller_role(player),
            ask_price=group.ask_price,
            bid_price=group.bid_price,
            traded=group.traded,
            trade_price=group.trade_price,
            seller_payoff=seller.payoff,
            buyer_payoff=buyer.payoff,
            seller_value=C.MUG_VALUE_TO_SELLER,
            buyer_value=C.MUG_VALUE_TO_BUYER,
        )


page_sequence = [Unmatched, Introduction, Ask, Bid, ResultsWaitPage, Results]
