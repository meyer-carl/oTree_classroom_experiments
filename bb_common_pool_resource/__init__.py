from otree.api import *

from classroom_utils import (
    bool_config_value,
    bounded_group_matrix,
    group_matrix_for_sizes,
    int_config_value,
    next_app,
    partition_group_sizes,
)


doc = """
Common-pool resource game with a shared stock that replenishes between rounds.
Players extract from a common resource, and the remaining stock carries forward.
"""


class C(BaseConstants):
    NAME_IN_URL = "common_pool_resource"
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 4
    NUM_ROUNDS = 4

    INITIAL_STOCK = 120
    REGEN_RATE = 0.9
    MAX_EXTRACTION_PER_ROUND = 40


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    start_stock = models.IntegerField(initial=C.INITIAL_STOCK)
    remaining_stock = models.IntegerField(initial=C.INITIAL_STOCK)
    total_extracted = models.IntegerField(initial=0)
    effective_group_size = models.IntegerField(initial=0)
    effective_max_extraction = models.IntegerField(initial=0)
    effective_regen_rate = models.FloatField(initial=C.REGEN_RATE)


class Player(BasePlayer):
    extraction = models.IntegerField(
        min=0,
        max=C.MAX_EXTRACTION_PER_ROUND,
        label="How many units will you extract this round?",
    )
    round_payoff = models.CurrencyField(initial=cu(0))


def use_flexible_groups(context):
    return bool_config_value(context, 'common_pool_flexible_grouping', False)


def target_group_size(context):
    default_size = C.HEADCOUNT_GROUP_SIZE if not use_flexible_groups(context) else 4
    return max(3, int_config_value(context, 'common_pool_target_group_size', default_size))


def maximum_group_size(context):
    if not use_flexible_groups(context):
        return C.HEADCOUNT_GROUP_SIZE
    configured = int_config_value(context, 'common_pool_max_group_size', 5)
    return max(target_group_size(context), configured)


def minimum_group_size(context):
    if not use_flexible_groups(context):
        return C.HEADCOUNT_GROUP_SIZE
    configured = int_config_value(context, 'common_pool_min_group_size', 3)
    return max(3, min(configured, maximum_group_size(context)))


def current_group_size(context):
    group = getattr(context, 'group', context)
    return len(group.get_players())


def initial_stock_per_person(context):
    default_value = C.INITIAL_STOCK // C.HEADCOUNT_GROUP_SIZE
    return int_config_value(context, 'common_pool_initial_stock_per_person', default_value)


def max_extraction_per_person(context):
    default_value = C.INITIAL_STOCK // C.HEADCOUNT_GROUP_SIZE
    return int_config_value(context, 'common_pool_max_extraction_per_person', default_value)


def common_pool_regen_rate(context):
    return float(getattr(getattr(context, 'session', context), 'config', {}).get('common_pool_regen_rate', C.REGEN_RATE))


def starting_stock_for_group(group_size, context):
    if not use_flexible_groups(context):
        return C.INITIAL_STOCK
    return initial_stock_per_person(context) * group_size


def is_unmatched(player: Player):
    return current_group_size(player) < minimum_group_size(player)


class Unmatched(Page):
    template_name = "global/Unmatched.html"

    @staticmethod
    def is_displayed(player: Player):
        return is_unmatched(player) and player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(required_size=minimum_group_size(player))

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return next_app(upcoming_apps)


def effective_max_extraction(group: Group):
    group_size = group.effective_group_size or current_group_size(group)
    if not use_flexible_groups(group.session):
        return min(C.MAX_EXTRACTION_PER_ROUND, group.start_stock // C.HEADCOUNT_GROUP_SIZE)
    return min(
        max_extraction_per_person(group.session),
        group.start_stock // group_size,
    )


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        players = subsession.get_players()
        if use_flexible_groups(subsession):
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
            group.effective_group_size = len(group.get_players())
            group.effective_regen_rate = common_pool_regen_rate(subsession)
            group.start_stock = starting_stock_for_group(group.effective_group_size, subsession)
            group.remaining_stock = group.start_stock
            group.effective_max_extraction = effective_max_extraction(group)
    else:
        subsession.group_like_round(1)
        previous_subsession = subsession.in_previous_rounds()[-1]
        for group in subsession.get_groups():
            previous_group = previous_subsession.get_groups()[group.id_in_subsession - 1]
            group.effective_group_size = len(group.get_players())
            group.effective_regen_rate = common_pool_regen_rate(subsession)
            group.start_stock = int(round(previous_group.remaining_stock * group.effective_regen_rate))
            group.remaining_stock = group.start_stock
            group.effective_max_extraction = effective_max_extraction(group)


def set_payoffs(group: Group):
    players = group.get_players()
    group.effective_group_size = len(players)
    group.effective_regen_rate = common_pool_regen_rate(group.session)
    group.effective_max_extraction = effective_max_extraction(group)
    total_requested = sum(player.extraction for player in players)
    group.total_extracted = total_requested
    group.remaining_stock = max(0, group.start_stock - total_requested)

    for player in players:
        player.round_payoff = cu(player.extraction)
        player.payoff = player.round_payoff


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            actual_group_size=player.group.effective_group_size or current_group_size(player),
            initial_stock=player.group.start_stock,
            regen_rate=player.group.effective_regen_rate or common_pool_regen_rate(player),
        )


class Extract(Page):
    form_model = "player"
    form_fields = ["extraction"]

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(
            round_number=player.round_number,
            start_stock=group.start_stock,
            max_extraction=group.effective_max_extraction or effective_max_extraction(group),
            regen_rate=group.effective_regen_rate or common_pool_regen_rate(player),
            actual_group_size=group.effective_group_size or current_group_size(player),
        )

    @staticmethod
    def error_message(player: Player, values):
        limit = player.group.effective_max_extraction or effective_max_extraction(player.group)
        if values["extraction"] > limit:
            return f"Choose at most {limit} units this round."


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        total_payoff = sum(round_player.payoff for round_player in player.in_all_rounds())
        next_round_stock = int(round(group.remaining_stock * group.effective_regen_rate))
        return dict(
            round_number=player.round_number,
            start_stock=group.start_stock,
            total_extracted=group.total_extracted,
            remaining_stock=group.remaining_stock,
            next_round_stock=next_round_stock,
            round_payoff=player.payoff,
            total_payoff=total_payoff,
            actual_group_size=group.effective_group_size or current_group_size(player),
            max_extraction=group.effective_max_extraction or effective_max_extraction(group),
            regen_rate=group.effective_regen_rate or common_pool_regen_rate(player),
        )


page_sequence = [Unmatched, Introduction, Extract, ResultsWaitPage, Results]
