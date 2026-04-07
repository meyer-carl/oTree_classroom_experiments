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
Gift exchange game with one employer and one worker.
The employer offers a wage and the worker responds with effort.
Higher effort raises the employer's output but also costs the worker more.
"""


class C(BaseConstants):
    NAME_IN_URL = "gift_exchange"
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 2
    NUM_ROUNDS = 4
    LEGACY_ACTIVE_ROUNDS = 1

    BASE_PAYOFF = cu(40)
    WAGE_INCREMENT = cu(10)
    MAX_WAGE = cu(100)
    PRODUCTIVITY_PER_EFFORT = cu(20)
    EFFORT_COSTS = {
        0: cu(0),
        1: cu(2),
        2: cu(5),
        3: cu(9),
        4: cu(14),
        5: cu(20),
    }
    EMPLOYER_ROLE = "Employer"
    WORKER_ROLE = "Worker"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    wage = models.CurrencyField(
        min=cu(0),
        max=C.MAX_WAGE,
        label="Wage offer",
    )
    effort = models.IntegerField(
        min=0,
        max=max(C.EFFORT_COSTS),
        choices=[[i, str(i)] for i in range(0, max(C.EFFORT_COSTS) + 1)],
        widget=widgets.RadioSelect,
        label="Effort choice",
    )
    employer_payoff = models.CurrencyField(initial=cu(0))
    worker_payoff = models.CurrencyField(initial=cu(0))


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
                C.EMPLOYER_ROLE,
                C.WORKER_ROLE,
            )
            subsession.session.vars[ACTIVE_COUNT_KEY] = schedule_active_counts(schedule)

        role_map = subsession.session.vars[ROLE_KEY][subsession.round_number - 1]
        apply_pair_schedule(
            subsession,
            subsession.session.vars[SCHEDULE_KEY][subsession.round_number - 1],
            role_assignments=role_map,
            primary_role=C.EMPLOYER_ROLE,
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
        player.assigned_role = role_map.get(player.participant.code, '') if role_balanced_classroom(subsession) else (role_name(player) if player.active_this_round else '')


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


def role_name(player: Player):
    if role_balanced_classroom(player):
        return player.assigned_role
    return C.EMPLOYER_ROLE if player.id_in_group == 1 else C.WORKER_ROLE


def assign_payoff(player: Player, raw_payoff):
    player.raw_round_payoff = raw_payoff
    if role_balanced_classroom(player) and role_cycle_payoff_rule(player) == 'average_active':
        active_count = player.session.vars[ACTIVE_COUNT_KEY].get(player.participant.code, 1)
        player.payoff = normalized_average_payoff(player, raw_payoff, active_count)
    else:
        player.payoff = raw_payoff


def set_payoffs(group: Group):
    employer = group.get_player_by_id(1)
    worker = group.get_player_by_id(2)
    effort_cost = C.EFFORT_COSTS[group.effort]

    group.employer_payoff = C.BASE_PAYOFF + C.PRODUCTIVITY_PER_EFFORT * group.effort - group.wage
    group.worker_payoff = C.BASE_PAYOFF + group.wage - effort_cost

    assign_payoff(employer, group.employer_payoff)
    assign_payoff(worker, group.worker_payoff)


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.active_this_round


class OfferWage(Page):
    form_model = "group"
    form_fields = ["wage"]

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round and role_name(player) == C.EMPLOYER_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            role=role_name(player),
            page_title="Employer offer",
            prompt="Choose a wage offer for the worker.",
            wage_increment=C.WAGE_INCREMENT,
            productivity=C.PRODUCTIVITY_PER_EFFORT,
        )

    @staticmethod
    def error_message(player: Player, values):
        wage = values["wage"]
        if int(wage) % int(C.WAGE_INCREMENT) != 0:
            return f"Use wage increments of {C.WAGE_INCREMENT}."


class WaitForWage(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round


class ChooseEffort(Page):
    form_model = "group"
    form_fields = ["effort"]

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round and role_name(player) == C.WORKER_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            role=role_name(player),
            page_title="Worker effort",
            prompt="Choose the effort level after seeing the wage offer.",
            effort_costs=C.EFFORT_COSTS,
        )


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
        return dict(
            role=role_name(player),
            wage=group.wage,
            effort=group.effort,
            effort_cost=C.EFFORT_COSTS[group.effort],
            employer_payoff=group.employer_payoff,
            worker_payoff=group.worker_payoff,
            raw_round_payoff=player.raw_round_payoff,
        )


page_sequence = [
    Unmatched,
    SitOutRound,
    Introduction,
    OfferWage,
    WaitForWage,
    ChooseEffort,
    ResultsWaitPage,
    Results,
]
