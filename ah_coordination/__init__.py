from otree.api import *
import random

from classroom_utils import (
    apply_pair_schedule,
    bool_config_value,
    group_matrix_for_sizes,
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
Pure Coordination Game:
Two players simultaneously choose Heads or Tails. On a randomly selected paying round,
if their choices match (i.e., they coordinate), both receive the payoff; otherwise both
receive zero.
The code is adapted from the Matching Pennies game, found
<a href="https://github.com/oTree-org/oTree/tree/lite" target="_blank">
    here
</a>.
"""


# Constants for the game
class C(BaseConstants):
    NAME_IN_URL = 'pure_coordination'  # change as appropriate
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 2
    NUM_ROUNDS = 4
    STAKES = cu(100)  # payoff each gets if they coordinate on the paying round
    LEGACY_ACTIVE_ROUNDS = 4

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    penny_side = models.StringField(
        choices=[['Heads', 'Heads'], ['Tails', 'Tails']],
        widget=widgets.RadioSelect,
        label="I choose:",
        blank=True,
    )
    coordinated = models.BooleanField(
        initial=False,
        doc="Whether this player successfully coordinated this round",
    )
    active_this_round = models.BooleanField(initial=True)
    raw_round_payoff = models.CurrencyField(initial=cu(0))


SCHEDULE_KEY = schedule_var_key(C.NAME_IN_URL, 'pair_cycle_schedule')
ACTIVE_COUNT_KEY = schedule_var_key(C.NAME_IN_URL, 'pair_cycle_active_counts')


def pair_cycle_enabled(context):
    return bool_config_value(context, 'pair_cycle_enabled', False)


def active_rounds(context):
    if pair_cycle_enabled(context):
        return int(session_config_value(context, 'pair_cycle_rounds', C.NUM_ROUNDS))
    return C.LEGACY_ACTIVE_ROUNDS


def pair_cycle_payoff_rule(context):
    return session_config_value(context, 'pair_cycle_payoff_rule', 'average_active')


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
        return dict(current_round=player.round_number, total_rounds=active_rounds(player))

# SESSION SETUP
def creating_session(subsession: Subsession):
    session = subsession.session

    if pair_cycle_enabled(subsession):
        if subsession.round_number == 1:
            schedule = round_robin_pair_schedule(
                [player.participant.code for player in subsession.get_players()],
                active_rounds(subsession),
            )
            session.vars[SCHEDULE_KEY] = schedule
            session.vars[ACTIVE_COUNT_KEY] = schedule_active_counts(schedule)

        apply_pair_schedule(
            subsession,
            session.vars[SCHEDULE_KEY][subsession.round_number - 1],
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
        session.vars['paying_round'] = random.randint(1, active_rounds(subsession))
    else:
        subsession.group_like_round(1)

    for player in subsession.get_players():
        player.active_this_round = is_active_round(player) and not is_unmatched(player)
        player.raw_round_payoff = cu(0)
        player.coordinated = False
        player.penny_side = ''


def assign_payoff(player: Player, raw_payoff):
    player.raw_round_payoff = raw_payoff
    if pair_cycle_enabled(player) and pair_cycle_payoff_rule(player) == 'average_active':
        active_count = player.session.vars[ACTIVE_COUNT_KEY].get(player.participant.code, 1)
        player.payoff = normalized_average_payoff(player, raw_payoff, active_count)
    else:
        player.payoff = raw_payoff

# PAYOFF CALCULATION
def set_payoffs(group: Group):
    subsession = group.subsession
    session = group.session

    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)

    # they coordinate if choices are identical
    coordinated = (p1.penny_side == p2.penny_side)

    for p in [p1, p2]:
        p.coordinated = coordinated
        if pair_cycle_enabled(p) and coordinated:
            assign_payoff(p, C.STAKES)
        elif not pair_cycle_enabled(p) and subsession.round_number == session.vars['paying_round'] and coordinated:
            assign_payoff(p, C.STAKES)
        else:
            assign_payoff(p, cu(0))

# PAGES
class Choice(Page):
    form_model = 'player'
    form_fields = ['penny_side']

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            player_in_previous_rounds=player.in_previous_rounds()
        )

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round

class ResultsSummary(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == active_rounds(player)

    @staticmethod
    def vars_for_template(player: Player):
        session = player.session
        player_in_all_rounds = [
            p for p in player.in_all_rounds()
            if p.round_number <= active_rounds(player)
        ]
        return dict(
            total_payoff=sum([p.payoff for p in player_in_all_rounds]),
            paying_round=None if pair_cycle_enabled(player) else session.vars['paying_round'],
            classroom_pair_cycle=pair_cycle_enabled(player),
            player_in_all_rounds=player_in_all_rounds,
        )

page_sequence = [Unmatched, SitOutRound, Choice, ResultsWaitPage, ResultsSummary]
