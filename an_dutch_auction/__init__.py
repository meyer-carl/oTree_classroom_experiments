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
Dutch auction (descending price).
Players submit the price at which they would stop the clock.
The highest stop price wins and pays their own price.
"""


class C(BaseConstants):
    NAME_IN_URL = 'dutch_auction'
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 4
    NUM_ROUNDS = 1

    VALUE_MIN = 60
    VALUE_MAX = 120

    PRICE_MIN = 0
    PRICE_MAX = 150
    RESERVE_PRICE = 0


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    winning_price = models.CurrencyField(initial=cu(0))
    sold = models.BooleanField(initial=False)
    actual_bidder_count = models.IntegerField(initial=0)


class Player(BasePlayer):
    private_value = models.CurrencyField(initial=cu(0))
    stop_price = models.CurrencyField(
        min=C.PRICE_MIN,
        max=C.PRICE_MAX,
        label="Stop price",
        doc="""Price at which the player would stop the auction""",
    )
    is_winner = models.BooleanField(initial=False)


def use_flexible_groups(context):
    return bool_config_value(context, 'auction_flexible_grouping', False)


def target_group_size(context):
    default_size = C.HEADCOUNT_GROUP_SIZE if not use_flexible_groups(context) else 4
    return max(2, int_config_value(context, 'auction_target_group_size', default_size))


def maximum_group_size(context):
    if not use_flexible_groups(context):
        return C.HEADCOUNT_GROUP_SIZE
    configured = int_config_value(context, 'auction_max_group_size', 6)
    return max(target_group_size(context), configured)


def minimum_group_size(context):
    if not use_flexible_groups(context):
        return C.HEADCOUNT_GROUP_SIZE
    configured = int_config_value(context, 'auction_min_group_size', 2)
    return max(2, min(configured, maximum_group_size(context)))


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

    for player in players:
        player.private_value = cu(random.randint(C.VALUE_MIN, C.VALUE_MAX))


def set_payoffs(group: Group):
    players = group.get_players()
    group.actual_bidder_count = len(players)
    highest = max([player.stop_price for player in players])

    if highest < cu(C.RESERVE_PRICE):
        group.sold = False
        group.winning_price = cu(0)
        for player in players:
            player.is_winner = False
            player.payoff = cu(0)
        return

    winners = [player for player in players if player.stop_price == highest]
    winner = random.choice(winners)

    group.sold = True
    group.winning_price = highest

    for player in players:
        player.is_winner = player == winner
        if player.is_winner:
            player.payoff = max(cu(0), player.private_value - group.winning_price)
        else:
            player.payoff = cu(0)


def page_vars(player: Player):
    return dict(
        actual_bidder_count=player.group.actual_bidder_count or current_bidder_count(player),
        use_flexible_grouping=use_flexible_groups(player),
    )


class Introduction(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return page_vars(player)


class StopPrice(Page):
    form_model = 'player'
    form_fields = ['stop_price']

    @staticmethod
    def error_message(player: Player, values):
        price = values['stop_price']
        if price > player.private_value:
            return 'Your stop price cannot exceed your private value.'


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return page_vars(player)


page_sequence = [Unmatched, Introduction, StopPrice, ResultsWaitPage, Results]
