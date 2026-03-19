from otree.api import *

doc = """
Repeated classroom asset market with a simple call-market clearing rule.
Players trade one asset per round at a uniform clearing price and receive
known dividends, making it easy to compare market prices with fundamentals.
"""


class C(BaseConstants):
    NAME_IN_URL = "asset_market_bubble"
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 5

    INITIAL_CASH = cu(120)
    INITIAL_ASSETS = 3
    DIVIDEND_PER_ASSET = cu(8)
    TERMINAL_VALUE = cu(0)
    MAX_ORDER_PRICE = cu(100)
    PRICE_INCREMENT = cu(10)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    clearing_price = models.CurrencyField(initial=cu(0))
    quantity_traded = models.IntegerField(initial=0)


class Player(BasePlayer):
    action = models.StringField(
        choices=[
            ["buy", "Buy 1 asset"],
            ["sell", "Sell 1 asset"],
            ["hold", "Hold"],
        ],
        widget=widgets.RadioSelect,
        label="This round's action",
    )
    order_price = models.CurrencyField(
        min=cu(0),
        max=C.MAX_ORDER_PRICE,
        blank=True,
        label="Limit price",
    )
    cash = models.CurrencyField(initial=cu(0))
    asset_units = models.IntegerField(initial=0)
    traded = models.BooleanField(initial=False)
    trade_price = models.CurrencyField(initial=cu(0))
    round_dividend = models.CurrencyField(initial=cu(0))


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        subsession.group_randomly()
        for player in subsession.get_players():
            player.cash = C.INITIAL_CASH
            player.asset_units = C.INITIAL_ASSETS
    else:
        subsession.group_like_round(1)


def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.PLAYERS_PER_GROUP


def fundamental_value(round_number: int):
    remaining_dividend_rounds = max(0, C.NUM_ROUNDS - round_number + 1)
    return remaining_dividend_rounds * C.DIVIDEND_PER_ASSET + C.TERMINAL_VALUE


def clear_market(group: Group):
    players = group.get_players()
    for player in players:
        player.traded = False
        player.trade_price = cu(0)
        player.round_dividend = cu(0)

    buyers = [
        player
        for player in players
        if player.action == "buy" and player.order_price is not None and player.cash >= player.order_price
    ]
    sellers = [
        player
        for player in players
        if player.action == "sell" and player.order_price is not None and player.asset_units > 0
    ]

    buyers.sort(key=lambda player: player.order_price, reverse=True)
    sellers.sort(key=lambda player: player.order_price)

    matches = []
    while buyers and sellers and buyers[0].order_price >= sellers[0].order_price:
        matches.append((buyers.pop(0), sellers.pop(0)))

    if matches:
        last_buyer, last_seller = matches[-1]
        clearing_price = (last_buyer.order_price + last_seller.order_price) / 2
        group.clearing_price = clearing_price
        group.quantity_traded = len(matches)

        for buyer, seller in matches:
            buyer.cash -= clearing_price
            buyer.asset_units += 1
            seller.cash += clearing_price
            seller.asset_units -= 1
            buyer.traded = True
            seller.traded = True
            buyer.trade_price = clearing_price
            seller.trade_price = clearing_price
    else:
        group.clearing_price = cu(0)
        group.quantity_traded = 0

    for player in players:
        player.round_dividend = player.asset_units * C.DIVIDEND_PER_ASSET
        player.cash += player.round_dividend
        player.payoff = player.cash if player.round_number == C.NUM_ROUNDS else cu(0)
        if player.round_number < C.NUM_ROUNDS:
            next_round_player = player.in_round(player.round_number + 1)
            next_round_player.cash = player.cash
            next_round_player.asset_units = player.asset_units


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


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Trade(Page):
    form_model = "player"
    form_fields = ["action", "order_price"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            round_number=player.round_number,
            cash=player.cash,
            asset_units=player.asset_units,
            dividend=C.DIVIDEND_PER_ASSET,
            fundamental_value=fundamental_value(player.round_number),
            next_fundamental_value=fundamental_value(player.round_number + 1),
            price_increment=C.PRICE_INCREMENT,
        )

    @staticmethod
    def error_message(player: Player, values):
        action = values["action"]
        order_price = values.get("order_price")

        if action == "hold":
            if order_price is not None:
                return "Leave the price blank if you choose hold."
            return

        if order_price is None:
            return "Enter a limit price for buy or sell orders."

        if int(order_price) % int(C.PRICE_INCREMENT) != 0:
            return f"Use price increments of {C.PRICE_INCREMENT}."

        if action == "buy" and order_price > player.cash:
            return "You cannot bid above your available cash."

        if action == "sell" and player.asset_units < 1:
            return "You need at least 1 asset to submit a sell order."


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = clear_market


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        total_wealth = player.cash + player.asset_units * C.TERMINAL_VALUE
        return dict(
            round_number=player.round_number,
            group=player.group,
            current_fundamental_value=fundamental_value(player.round_number),
            next_fundamental_value=fundamental_value(player.round_number + 1),
            total_wealth=total_wealth,
        )


page_sequence = [Unmatched, Introduction, Trade, ResultsWaitPage, Results]
