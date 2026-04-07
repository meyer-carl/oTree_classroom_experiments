from otree.api import *

from classroom_utils import (
    bool_config_value,
    bounded_group_matrix,
    currency_config_value,
    group_matrix_for_sizes,
    int_config_value,
    next_app,
    partition_group_sizes,
)


doc = """
Volunteer's dilemma: each player decides whether to volunteer.
If at least one volunteers, everyone benefits, but volunteers pay a cost.
"""


class C(BaseConstants):
    NAME_IN_URL = 'volunteer_dilemma'
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 3
    NUM_ROUNDS = 1

    NUM_OTHER_PLAYERS = HEADCOUNT_GROUP_SIZE - 1
    GENERAL_BENEFIT = cu(100)
    VOLUNTEER_COST = cu(40)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    num_volunteers = models.IntegerField()
    effective_group_size = models.IntegerField(initial=0)
    success_benefit = models.CurrencyField(initial=cu(0))
    volunteer_cost = models.CurrencyField(initial=cu(0))
    total_group_benefit = models.CurrencyField(initial=cu(0))


class Player(BasePlayer):
    volunteer = models.BooleanField(
        label='Do you wish to volunteer?', doc="""Whether player volunteers"""
    )


def use_flexible_groups(context):
    return bool_config_value(context, 'volunteer_flexible_grouping', False)


def target_group_size(context):
    default_size = C.HEADCOUNT_GROUP_SIZE if not use_flexible_groups(context) else 3
    return max(2, int_config_value(context, 'volunteer_target_group_size', default_size))


def maximum_group_size(context):
    if not use_flexible_groups(context):
        return C.HEADCOUNT_GROUP_SIZE
    configured = int_config_value(context, 'volunteer_max_group_size', 5)
    return max(target_group_size(context), configured)


def minimum_group_size(context):
    if not use_flexible_groups(context):
        return C.HEADCOUNT_GROUP_SIZE
    configured = int_config_value(context, 'volunteer_min_group_size', 2)
    return max(2, min(configured, maximum_group_size(context)))


def current_group_size(context):
    group = getattr(context, 'group', context)
    return len(group.get_players())


def is_unmatched(player: Player):
    return current_group_size(player) < minimum_group_size(player)


def effective_success_benefit(context):
    if not (use_flexible_groups(context) and bool_config_value(context, 'volunteer_scale_payoffs', True)):
        return C.GENERAL_BENEFIT
    return currency_config_value(context, 'volunteer_benefit_per_person', C.GENERAL_BENEFIT)


def effective_volunteer_cost(context):
    if not (use_flexible_groups(context) and bool_config_value(context, 'volunteer_scale_payoffs', True)):
        return C.VOLUNTEER_COST
    return currency_config_value(context, 'volunteer_cost_per_person', C.VOLUNTEER_COST)


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
        subsession.set_group_matrix(
            bounded_group_matrix(
                players,
                target_group_size(subsession),
                min_group_size=minimum_group_size(subsession),
                max_group_size=maximum_group_size(subsession),
            )
        )
        return
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


def set_payoffs(group: Group):
    players = group.get_players()
    group.effective_group_size = len(players)
    group.num_volunteers = sum([player.volunteer for player in players])
    group.success_benefit = effective_success_benefit(group)
    group.volunteer_cost = effective_volunteer_cost(group)
    group.total_group_benefit = group.success_benefit * group.effective_group_size

    baseline_amount = group.success_benefit if group.num_volunteers > 0 else cu(0)
    for player in players:
        player.payoff = baseline_amount
        if player.volunteer:
            player.payoff -= group.volunteer_cost


def page_vars(player: Player):
    group_size = player.group.effective_group_size or current_group_size(player)
    benefit = player.group.success_benefit or effective_success_benefit(player)
    cost = player.group.volunteer_cost or effective_volunteer_cost(player)
    return dict(
        actual_group_size=group_size,
        other_participants=max(0, group_size - 1),
        success_benefit=benefit,
        volunteer_cost=cost,
        total_group_benefit=benefit * group_size,
        use_flexible_groups=use_flexible_groups(player),
    )


class Introduction(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return page_vars(player)


class Decision(Page):
    form_model = 'player'
    form_fields = ['volunteer']

    @staticmethod
    def vars_for_template(player: Player):
        return page_vars(player)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return page_vars(player)


page_sequence = [Unmatched, Introduction, Decision, ResultsWaitPage, Results]
