from otree.api import *

from classroom_utils import (
    apply_pair_schedule,
    bool_config_value,
    group_matrix_for_sizes,
    int_config_value,
    next_app,
    normalized_average_payoff,
    partition_group_sizes,
    round_robin_pair_schedule,
    schedule_active_counts,
    schedule_var_key,
    session_config_value,
    unmatched_template_vars,
)


doc = """
This is a one-shot "Prisoner's Dilemma". Two players are asked separately
whether they want to cooperate or defect. Their choices directly determine the
payoffs.
"""


class C(BaseConstants):
    NAME_IN_URL = 'prisoner'
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 2
    NUM_ROUNDS = 4
    PAYOFF_A = cu(300)
    PAYOFF_B = cu(200)
    PAYOFF_C = cu(100)
    PAYOFF_D = cu(0)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    cooperate = models.BooleanField(
        choices=[[True, 'Cooperate'], [False, 'Defect']],
        doc="""This player's decision""",
        widget=widgets.RadioSelect,
    )
    active_this_round = models.BooleanField(initial=True)
    raw_round_payoff = models.CurrencyField(initial=cu(0))


SCHEDULE_KEY = schedule_var_key(C.NAME_IN_URL, 'pair_cycle_schedule')
ACTIVE_COUNT_KEY = schedule_var_key(C.NAME_IN_URL, 'pair_cycle_active_counts')


def pair_cycle_enabled(context):
    return bool_config_value(context, 'pair_cycle_enabled', False)


def pair_cycle_rounds(context):
    return int_config_value(context, 'pair_cycle_rounds', 4) if pair_cycle_enabled(context) else 1


def pair_cycle_payoff_rule(context):
    return session_config_value(context, 'pair_cycle_payoff_rule', 'average_active')


def is_active_round(player: Player):
    return player.round_number <= pair_cycle_rounds(player)

# Helper to detect incomplete groups
def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.HEADCOUNT_GROUP_SIZE

# Page to notify unmatched participants and skip the app
class Unmatched(Page):
    template_name = 'global/Unmatched.html'

    @staticmethod
    def is_displayed(player: Player):
        return not pair_cycle_enabled(player) and is_unmatched(player) and player.round_number == 1

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
        return pair_cycle_enabled(player) and is_active_round(player) and is_unmatched(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(current_round=player.round_number, total_rounds=pair_cycle_rounds(player))


def creating_session(subsession: Subsession):
    if pair_cycle_enabled(subsession):
        if subsession.round_number == 1:
            schedule = round_robin_pair_schedule(
                [player.participant.code for player in subsession.get_players()],
                pair_cycle_rounds(subsession),
            )
            subsession.session.vars[SCHEDULE_KEY] = schedule
            subsession.session.vars[ACTIVE_COUNT_KEY] = schedule_active_counts(schedule)

        apply_pair_schedule(
            subsession,
            subsession.session.vars[SCHEDULE_KEY][subsession.round_number - 1],
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


def assign_payoff(player: Player, raw_payoff):
    player.raw_round_payoff = raw_payoff
    if pair_cycle_enabled(player) and pair_cycle_payoff_rule(player) == 'average_active':
        active_rounds = player.session.vars[ACTIVE_COUNT_KEY].get(player.participant.code, 1)
        player.payoff = normalized_average_payoff(player, raw_payoff, active_rounds)
    else:
        player.payoff = raw_payoff


# FUNCTIONS
def set_payoffs(group: Group):
    for p in group.get_players():
        set_payoff(p)


def other_player(player: Player):
    return player.get_others_in_group()[0]


def set_payoff(player: Player):
    payoff_matrix = {
        (False, True): C.PAYOFF_A,
        (True, True): C.PAYOFF_B,
        (False, False): C.PAYOFF_C,
        (True, False): C.PAYOFF_D,
    }
    other = other_player(player)
    assign_payoff(player, payoff_matrix[(player.cooperate, other.cooperate)])


# PAGES
class Introduction(Page):
    timeout_seconds = 100

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.active_this_round


class Decision(Page):
    form_model = 'player'
    form_fields = ['cooperate']

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round


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
        opponent = other_player(player)
        return dict(
            opponent=opponent,
            same_choice=player.cooperate == opponent.cooperate,
            my_decision=player.field_display('cooperate'),
            opponent_decision=opponent.field_display('cooperate'),
            raw_round_payoff=player.raw_round_payoff,
        )


page_sequence = [Unmatched, SitOutRound, Introduction, Decision, ResultsWaitPage, Results]
