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
Traveler's dilemma: two players make claims for compensation.
If claims match, both get that claim. Otherwise, both get the lower claim,
with a bonus for the lower claimant and a penalty for the higher claimant.
"""


class C(BaseConstants):
    NAME_IN_URL = 'traveler_dilemma'
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 2
    NUM_ROUNDS = 4

    ADJUSTMENT_ABS = cu(2)
    MAX_AMOUNT = cu(100)
    MIN_AMOUNT = cu(2)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    lower_claim = models.CurrencyField()


class Player(BasePlayer):
    claim = models.CurrencyField(
        min=C.MIN_AMOUNT,
        max=C.MAX_AMOUNT,
        label='How much will you claim for your antique?',
        doc="""Each player's claim""",
    )
    adjustment = models.CurrencyField()
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
    p1, p2 = group.get_players()
    if p1.claim == p2.claim:
        group.lower_claim = p1.claim
        for p in [p1, p2]:
            assign_payoff(p, group.lower_claim)
            p.adjustment = cu(0)
    else:
        if p1.claim < p2.claim:
            winner = p1
            loser = p2
        else:
            winner = p2
            loser = p1
        group.lower_claim = winner.claim
        winner.adjustment = C.ADJUSTMENT_ABS
        loser.adjustment = -C.ADJUSTMENT_ABS
        assign_payoff(winner, group.lower_claim + winner.adjustment)
        assign_payoff(loser, group.lower_claim + loser.adjustment)


def other_player(player: Player):
    return player.get_others_in_group()[0]


# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.active_this_round


class Claim(Page):
    form_model = 'player'
    form_fields = ['claim']

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
        return dict(other_player_claim=other_player(player).claim, raw_round_payoff=player.raw_round_payoff)


page_sequence = [Unmatched, SitOutRound, Introduction, Claim, ResultsWaitPage, Results]
