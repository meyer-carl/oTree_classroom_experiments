from otree.api import *

from classroom_utils import (
    apply_pair_schedule,
    bool_config_value,
    group_matrix_for_sizes,
    next_app,
    normalized_average_payoff,
    partition_group_sizes,
    role_assignment_schedule,
    round_robin_pair_schedule,
    schedule_active_counts,
    schedule_var_key,
    session_config_value,
    unmatched_template_vars,
)

doc = """
Endowment effect game with one seller and one buyer.
The seller reports a minimum willingness-to-accept (WTA) to part with the mug.
The buyer reports a maximum willingness-to-pay (WTP).
If WTP meets or exceeds WTA, the trade clears at the midpoint price.
"""


class C(BaseConstants):
    NAME_IN_URL = "endowment_effect"
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 2
    NUM_ROUNDS = 4
    LEGACY_ACTIVE_ROUNDS = 1

    CASH_ENDOWMENT = cu(50)
    MUG_VALUE_TO_SELLER = cu(80)
    MUG_VALUE_TO_BUYER = cu(100)
    PRICE_MIN = cu(0)
    PRICE_MAX = cu(150)
    SELLER_ROLE = "Seller"
    BUYER_ROLE = "Buyer"


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
    assigned_role = models.StringField(blank=True)
    active_this_round = models.BooleanField(initial=True)
    raw_round_payoff = models.CurrencyField(initial=cu(0))


SCHEDULE_KEY = schedule_var_key(C.NAME_IN_URL, 'role_cycle_schedule')
ROLE_KEY = schedule_var_key(C.NAME_IN_URL, 'role_cycle_roles')
ACTIVE_COUNT_KEY = schedule_var_key(C.NAME_IN_URL, 'role_cycle_active_counts')


def role_balanced_classroom(context):
    return bool_config_value(context, 'role_balanced_classroom', False)


def active_rounds(context):
    if role_balanced_classroom(context):
        return int(session_config_value(context, 'role_cycle_rounds', C.NUM_ROUNDS))
    return C.LEGACY_ACTIVE_ROUNDS


def role_cycle_payoff_rule(context):
    return session_config_value(context, 'role_cycle_payoff_rule', 'average_active')


def is_active_round(player: Player):
    return player.round_number <= active_rounds(player)


def creating_session(subsession: Subsession):
    role_map = {}
    if role_balanced_classroom(subsession):
        if subsession.round_number == 1:
            schedule = round_robin_pair_schedule(
                [player.participant.code for player in subsession.get_players()],
                active_rounds(subsession),
            )
            subsession.session.vars[SCHEDULE_KEY] = schedule
            subsession.session.vars[ROLE_KEY] = role_assignment_schedule(
                schedule,
                C.SELLER_ROLE,
                C.BUYER_ROLE,
            )
            subsession.session.vars[ACTIVE_COUNT_KEY] = schedule_active_counts(schedule)

        role_map = subsession.session.vars[ROLE_KEY][subsession.round_number - 1]
        apply_pair_schedule(
            subsession,
            subsession.session.vars[SCHEDULE_KEY][subsession.round_number - 1],
            role_assignments=role_map,
            primary_role=C.SELLER_ROLE,
        )
    elif subsession.round_number == 1:
        players = list(subsession.get_players())
        subsession.set_group_matrix(
            group_matrix_for_sizes(
                players,
                partition_group_sizes(
                    len(players),
                    C.HEADCOUNT_GROUP_SIZE,
                    allow_variable_group_sizes=False,
                    minimum_group_size=1,
                ),
            )
        )
    else:
        subsession.group_like_round(1)

    for player in subsession.get_players():
        player.active_this_round = is_active_round(player) and not is_unmatched(player)
        player.raw_round_payoff = cu(0)
        player.assigned_role = role_map.get(player.participant.code, '') if role_balanced_classroom(subsession) else (seller_role(player) if player.active_this_round else '')


def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.HEADCOUNT_GROUP_SIZE


class Unmatched(Page):
    template_name = "global/Unmatched.html"

    @staticmethod
    def is_displayed(player: Player):
        return not role_balanced_classroom(player) and is_unmatched(player) and player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return unmatched_template_vars(C.HEADCOUNT_GROUP_SIZE)

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return next_app(upcoming_apps)


class SitOutRound(Page):
    template_name = "global/SitOutRound.html"

    @staticmethod
    def is_displayed(player: Player):
        return role_balanced_classroom(player) and is_active_round(player) and is_unmatched(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(current_round=player.round_number, total_rounds=active_rounds(player))


def seller_role(player: Player):
    if role_balanced_classroom(player):
        return player.assigned_role
    return C.SELLER_ROLE if player.id_in_group == 1 else C.BUYER_ROLE


def assign_payoff(player: Player, raw_payoff):
    player.raw_round_payoff = raw_payoff
    if role_balanced_classroom(player) and role_cycle_payoff_rule(player) == 'average_active':
        active_count = player.session.vars[ACTIVE_COUNT_KEY].get(player.participant.code, 1)
        player.payoff = normalized_average_payoff(player, raw_payoff, active_count)
    else:
        player.payoff = raw_payoff


def set_payoffs(group: Group):
    seller = group.get_player_by_id(1)
    buyer = group.get_player_by_id(2)

    group.traded = group.bid_price >= group.ask_price
    group.trade_price = (group.ask_price + group.bid_price) / 2 if group.traded else cu(0)

    if group.traded:
        assign_payoff(seller, C.CASH_ENDOWMENT + group.trade_price)
        assign_payoff(buyer, C.CASH_ENDOWMENT + C.MUG_VALUE_TO_BUYER - group.trade_price)
    else:
        assign_payoff(seller, C.CASH_ENDOWMENT + C.MUG_VALUE_TO_SELLER)
        assign_payoff(buyer, C.CASH_ENDOWMENT)


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.active_this_round


class Ask(Page):
    form_model = "group"
    form_fields = ["ask_price"]

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round and seller_role(player) == C.SELLER_ROLE

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
        return player.active_this_round and seller_role(player) == C.BUYER_ROLE

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

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round

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
            raw_round_payoff=player.raw_round_payoff,
        )


page_sequence = [Unmatched, SitOutRound, Introduction, Ask, Bid, ResultsWaitPage, Results]
