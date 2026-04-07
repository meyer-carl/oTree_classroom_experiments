from otree.api import *
import random

from classroom_utils import (
    bool_config_value,
    bounded_group_matrix,
    group_matrix_for_sizes,
    int_config_value,
    next_app,
    partition_group_sizes,
)


doc = """
Common value auction: players bid on an item with the same true value.
Each player sees a noisy estimate of the value. Highest bidder wins and earns
(value - bid), floored at 0.
"""


class C(BaseConstants):
    NAME_IN_URL = 'common_value_auction'
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 4
    NUM_ROUNDS = 1

    BID_MIN = cu(0)
    BID_MAX = cu(10)
    BID_NOISE = cu(1)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    item_value = models.CurrencyField(
        doc="""Common value of the item to be auctioned"""
    )
    highest_bid = models.CurrencyField()
    actual_bidder_count = models.IntegerField(initial=0)


class Player(BasePlayer):
    item_value_estimate = models.CurrencyField(
        doc="""Estimate of the common value, may differ across players"""
    )
    bid_amount = models.CurrencyField(
        min=C.BID_MIN,
        max=C.BID_MAX,
        doc="""Amount bid by the player""",
        label="Bid amount",
    )
    is_winner = models.BooleanField(
        initial=False, doc="""Indicates whether the player is the winner"""
    )


def use_flexible_groups(context):
    return bool_config_value(context, 'auction_flexible_grouping', False)


def target_group_size(context):
    default_size = C.HEADCOUNT_GROUP_SIZE if not use_flexible_groups(context) else 4
    return max(3, int_config_value(context, 'auction_target_group_size', default_size))


def maximum_group_size(context):
    if not use_flexible_groups(context):
        return C.HEADCOUNT_GROUP_SIZE
    configured = int_config_value(context, 'auction_max_group_size', 6)
    return max(target_group_size(context), configured)


def minimum_group_size(context):
    if not use_flexible_groups(context):
        return C.HEADCOUNT_GROUP_SIZE
    configured = int_config_value(context, 'auction_min_group_size', 3)
    return max(3, min(configured, maximum_group_size(context)))


def current_bidder_count(context):
    group = getattr(context, 'group', context)
    return len(group.get_players())


def is_unmatched(player: Player):
    return current_bidder_count(player) < minimum_group_size(player)


class Unmatched(Page):
    template_name = 'global/Unmatched.html'

    @staticmethod
    def is_displayed(player: Player):
        return is_unmatched(player) and player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(required_size=minimum_group_size(player))

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return next_app(upcoming_apps)


def creating_session(subsession: Subsession):
    players = subsession.get_players()
    if use_flexible_groups(subsession):
        random.shuffle(players)
        subsession.set_group_matrix(
            bounded_group_matrix(
                players,
                target_group_size(subsession),
                min_group_size=minimum_group_size(subsession),
                max_group_size=maximum_group_size(subsession),
            )
        )
    else:
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

    for group in subsession.get_groups():
        item_value = random.uniform(float(C.BID_MIN), float(C.BID_MAX))
        group.item_value = cu(round(item_value, 1))


def generate_value_estimate(group: Group):
    estimate = group.item_value + random.uniform(-C.BID_NOISE, C.BID_NOISE)
    estimate = round(float(estimate), 1)
    if estimate < float(C.BID_MIN):
        estimate = float(C.BID_MIN)
    if estimate > float(C.BID_MAX):
        estimate = float(C.BID_MAX)
    return cu(estimate)


def set_payoff(player: Player):
    group = player.group

    if player.is_winner:
        player.payoff = group.item_value - player.bid_amount
        if player.payoff < 0:
            player.payoff = cu(0)
    else:
        player.payoff = cu(0)


def set_winner(group: Group):
    players = group.get_players()
    group.actual_bidder_count = len(players)
    group.highest_bid = max([player.bid_amount for player in players])
    players_with_highest_bid = [
        player for player in players if player.bid_amount == group.highest_bid
    ]
    winner = random.choice(players_with_highest_bid)
    winner.is_winner = True
    for player in players:
        set_payoff(player)


def page_vars(player: Player):
    return dict(
        actual_bidder_count=player.group.actual_bidder_count or current_bidder_count(player),
        use_flexible_grouping=use_flexible_groups(player),
    )


class Introduction(Page):
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.item_value_estimate = generate_value_estimate(player.group)

    @staticmethod
    def vars_for_template(player: Player):
        return page_vars(player)


class Bid(Page):
    form_model = 'player'
    form_fields = ['bid_amount']

    @staticmethod
    def vars_for_template(player: Player):
        return page_vars(player)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_winner


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            is_greedy=player.group.item_value - player.bid_amount < 0,
            **page_vars(player),
        )


page_sequence = [Unmatched, Introduction, Bid, ResultsWaitPage, Results]
