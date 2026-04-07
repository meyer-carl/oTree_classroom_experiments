from otree.api import *
import random

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
Two-sided auction (double auction with one buyer and one seller).
Both sides submit a price simultaneously. A trade occurs if bid >= ask.
The trade price is the midpoint of the two offers.
"""


class C(BaseConstants):
    NAME_IN_URL = 'two_sided_auction'
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 2
    NUM_ROUNDS = 4
    LEGACY_ACTIVE_ROUNDS = 1

    VALUE_MIN = 60
    VALUE_MAX = 100
    COST_MIN = 0
    COST_MAX = 40

    PRICE_MIN = 0
    PRICE_MAX = 120
    BUYER_ROLE = 'Buyer'
    SELLER_ROLE = 'Seller'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    trade_price = models.CurrencyField(initial=cu(0))
    traded = models.BooleanField(initial=False)


class Player(BasePlayer):
    assigned_role = models.StringField(blank=True)
    active_this_round = models.BooleanField(initial=True)
    raw_round_payoff = models.CurrencyField(initial=cu(0))
    is_buyer = models.BooleanField()
    private_value = models.CurrencyField(initial=cu(0))
    private_cost = models.CurrencyField(initial=cu(0))
    offer_price = models.CurrencyField(
        min=C.PRICE_MIN,
        max=C.PRICE_MAX,
        label="Your price",
        doc="""Bid (buyer) or ask (seller)""",
    )

    def role(self):
        return 'Buyer' if self.is_buyer else 'Seller'


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


def role_name(player: Player):
    if role_balanced_classroom(player):
        return player.assigned_role
    return C.BUYER_ROLE if player.is_buyer else C.SELLER_ROLE


def is_active_round(player: Player):
    return player.round_number <= active_rounds(player)

# Helper to detect incomplete groups
def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.HEADCOUNT_GROUP_SIZE

# Page to notify unmatched participants and skip the app
class Unmatched(Page):
    template_name = 'global/Unmatched.html'

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
    template_name = 'global/SitOutRound.html'

    @staticmethod
    def is_displayed(player: Player):
        return role_balanced_classroom(player) and is_active_round(player) and is_unmatched(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(current_round=player.round_number, total_rounds=active_rounds(player))


# FUNCTIONS
def creating_session(subsession: Subsession):
    if role_balanced_classroom(subsession):
        if subsession.round_number == 1:
            schedule = round_robin_pair_schedule(
                [player.participant.code for player in subsession.get_players()],
                active_rounds(subsession),
            )
            subsession.session.vars[SCHEDULE_KEY] = schedule
            subsession.session.vars[ROLE_KEY] = role_assignment_schedule(
                schedule,
                C.BUYER_ROLE,
                C.SELLER_ROLE,
            )
            subsession.session.vars[ACTIVE_COUNT_KEY] = schedule_active_counts(schedule)

        role_map = subsession.session.vars[ROLE_KEY][subsession.round_number - 1]
        apply_pair_schedule(
            subsession,
            subsession.session.vars[SCHEDULE_KEY][subsession.round_number - 1],
            role_assignments=role_map,
            primary_role=C.BUYER_ROLE,
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
        player.assigned_role = ''

    for group in subsession.get_groups():
        players = group.get_players()
        if len(players) != 2:
            for player in players:
                player.is_buyer = False
                player.private_value = cu(0)
                player.private_cost = cu(0)
            continue

        if role_balanced_classroom(subsession):
            buyer = group.get_player_by_id(1)
            seller = group.get_player_by_id(2)
            buyer.assigned_role = C.BUYER_ROLE
            seller.assigned_role = C.SELLER_ROLE
        else:
            players = group.get_players()
            random.shuffle(players)
            buyer, seller = players[0], players[1]
            group.set_players([buyer, seller])

        buyer.is_buyer = True
        buyer.private_value = cu(random.randint(C.VALUE_MIN, C.VALUE_MAX))
        buyer.private_cost = cu(0)
        buyer.assigned_role = C.BUYER_ROLE

        seller.is_buyer = False
        seller.private_cost = cu(random.randint(C.COST_MIN, C.COST_MAX))
        seller.private_value = cu(0)
        seller.assigned_role = C.SELLER_ROLE


def assign_payoff(player: Player, raw_payoff):
    player.raw_round_payoff = raw_payoff
    if role_balanced_classroom(player) and role_cycle_payoff_rule(player) == 'average_active':
        active_count = player.session.vars[ACTIVE_COUNT_KEY].get(player.participant.code, 1)
        player.payoff = normalized_average_payoff(player, raw_payoff, active_count)
    else:
        player.payoff = raw_payoff


def set_payoffs(group: Group):
    buyer = [p for p in group.get_players() if p.is_buyer][0]
    seller = [p for p in group.get_players() if not p.is_buyer][0]

    group.traded = False
    group.trade_price = cu(0)
    assign_payoff(buyer, cu(0))
    assign_payoff(seller, cu(0))

    if buyer.offer_price >= seller.offer_price:
        group.traded = True
        group.trade_price = (buyer.offer_price + seller.offer_price) / 2
        assign_payoff(buyer, max(cu(0), buyer.private_value - group.trade_price))
        assign_payoff(seller, max(cu(0), group.trade_price - seller.private_cost))


# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.active_this_round


class Order(Page):
    form_model = 'player'
    form_fields = ['offer_price']

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round

    @staticmethod
    def vars_for_template(player: Player):
        return dict(role=player.role())

    @staticmethod
    def error_message(player: Player, values):
        price = values['offer_price']
        if player.is_buyer and price > player.private_value:
            return 'Your bid cannot exceed your private value.'
        if not player.is_buyer and price < player.private_cost:
            return 'Your ask cannot be below your private cost.'


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round


page_sequence = [Unmatched, SitOutRound, Introduction, Order, ResultsWaitPage, Results]
