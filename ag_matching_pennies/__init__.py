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

# Documentation for the game
doc = """
Matching Pennies:
Two players choose heads or tails. If they match, the matcher wins; if they mismatch, the mismatcher wins.
The game is played for a number of rounds, with a randomly selected paying round.
The code is adapted from the Matching Pennies game, found
<a href="https://github.com/oTree-org/oTree/tree/lite" target="_blank">
    here
</a>.
"""

# Constants for the game
class C(BaseConstants):
    NAME_IN_URL = 'matching_pennies'  # URL name for the app
    PLAYERS_PER_GROUP = None  # Number of players per group
    HEADCOUNT_GROUP_SIZE = 2
    NUM_ROUNDS = 4  # Total number of rounds in the game
    LEGACY_ACTIVE_ROUNDS = 4
    STAKES = cu(100)  # Amount to be won in the paying round

    # Roles for the players
    MATCHER_ROLE = 'Matcher'
    MISMATCHER_ROLE = 'Mismatcher'

# Subsession class (one per round)
class Subsession(BaseSubsession):
    pass

# Group class (one per group of players)
class Group(BaseGroup):
    pass

# Player class (one per player)
class Player(BasePlayer):
    # Field for the player's choice of penny side
    penny_side = models.StringField(
        choices=[['Heads', 'Heads'], ['Tails', 'Tails']],  # Choices for the penny side
        widget=widgets.RadioSelect,  # Widget to display the choices
        label="I choose:",  # Label for the field
    )
    # Field to indicate if the player is a winner
    is_winner = models.BooleanField(initial=False)
    assigned_role = models.StringField(blank=True)
    active_this_round = models.BooleanField(initial=True)
    raw_round_payoff = models.CurrencyField(initial=cu(0))


SCHEDULE_KEY = schedule_var_key(C.NAME_IN_URL, 'pair_cycle_schedule')
ROLE_KEY = schedule_var_key(C.NAME_IN_URL, 'pair_cycle_roles')
ACTIVE_COUNT_KEY = schedule_var_key(C.NAME_IN_URL, 'pair_cycle_active_counts')


def pair_cycle_enabled(context):
    return bool_config_value(context, 'pair_cycle_enabled', False)


def active_rounds(context):
    if pair_cycle_enabled(context):
        return int(session_config_value(context, 'pair_cycle_rounds', C.NUM_ROUNDS))
    return C.LEGACY_ACTIVE_ROUNDS


def pair_cycle_payoff_rule(context):
    return session_config_value(context, 'pair_cycle_payoff_rule', 'average_active')


def role_name(player: Player):
    if pair_cycle_enabled(player):
        return player.assigned_role
    return C.MATCHER_ROLE if player.id_in_group == 1 else C.MISMATCHER_ROLE


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

# FUNCTIONS

# Function to set up the session
def creating_session(subsession: Subsession):
    session = subsession.session
    role_map = {}

    if pair_cycle_enabled(subsession):
        if subsession.round_number == 1:
            schedule = round_robin_pair_schedule(
                [player.participant.code for player in subsession.get_players()],
                active_rounds(subsession),
            )
            session.vars[SCHEDULE_KEY] = schedule
            session.vars[ROLE_KEY] = role_assignment_schedule(schedule, C.MATCHER_ROLE, C.MISMATCHER_ROLE)
            session.vars[ACTIVE_COUNT_KEY] = schedule_active_counts(schedule)

        round_roles = session.vars[ROLE_KEY][subsession.round_number - 1]
        role_map = round_roles
        apply_pair_schedule(
            subsession,
            session.vars[SCHEDULE_KEY][subsession.round_number - 1],
            role_assignments=round_roles,
            primary_role=C.MATCHER_ROLE,
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
        paying_round = random.randint(1, active_rounds(subsession))
        session.vars['paying_round'] = paying_round
    elif subsession.round_number == 2:
        subsession.group_like_round(1)
    elif subsession.round_number == 3:
        for group in subsession.get_groups():
            if len(group.get_players()) == 2:
                p1 = group.get_player_by_id(1)
                p2 = group.get_player_by_id(2)
                group.set_players([p2, p1])
    else:
        subsession.group_like_round(3)

    for player in subsession.get_players():
        player.active_this_round = is_active_round(player) and not is_unmatched(player)
        player.raw_round_payoff = cu(0)
        player.is_winner = False
        player.assigned_role = role_map.get(player.participant.code, '') if pair_cycle_enabled(subsession) else (role_name(player) if player.active_this_round else '')


def assign_payoff(player: Player, raw_payoff):
    player.raw_round_payoff = raw_payoff
    if pair_cycle_enabled(player) and pair_cycle_payoff_rule(player) == 'average_active':
        active_count = player.session.vars[ACTIVE_COUNT_KEY].get(player.participant.code, 1)
        player.payoff = normalized_average_payoff(player, raw_payoff, active_count)
    else:
        player.payoff = raw_payoff

# Function to calculate payoffs for the group
def set_payoffs(group: Group):
    subsession = group.subsession
    session = group.session

    # Get the two players in the group
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)

    # Determine the winner and calculate payoffs
    for p in [p1, p2]:
        is_matcher = role_name(p) == C.MATCHER_ROLE
        p.is_winner = (p1.penny_side == p2.penny_side) == is_matcher  # Determine if the player wins
        if pair_cycle_enabled(p) and p.is_winner:
            assign_payoff(p, C.STAKES)
        elif not pair_cycle_enabled(p) and subsession.round_number == session.vars['paying_round'] and p.is_winner:
            assign_payoff(p, C.STAKES)
        else:
            assign_payoff(p, cu(0))

# PAGES

# Page where players make their choice
class Choice(Page):
    form_model = 'player'  # Model for the form
    form_fields = ['penny_side']  # Fields to be filled in the form

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round

    @staticmethod
    def vars_for_template(player: Player):
        # Provide data for the template, including the player's history in previous rounds
        return dict(player_in_previous_rounds=player.in_previous_rounds(), role_name=role_name(player))

# Wait page to calculate results after all players have made their choices
class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs  # Call the set_payoffs function after all players arrive

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round

# Page to display the summary of results
class ResultsSummary(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Display this page only in the final round
        return player.round_number == active_rounds(player)

    @staticmethod
    def vars_for_template(player: Player):
        session = player.session

        # Get the player's data from all rounds
        player_in_all_rounds = [
            p for p in player.in_all_rounds()
            if p.round_number <= active_rounds(player)
        ]
        return dict(
            total_payoff=sum([p.payoff for p in player_in_all_rounds]),  # Total payoff across all rounds
            paying_round=None if pair_cycle_enabled(player) else session.vars['paying_round'],
            classroom_pair_cycle=pair_cycle_enabled(player),
            player_in_all_rounds=player_in_all_rounds,  # Player's data from all rounds
        )

# Sequence of pages in the game
page_sequence = [Unmatched, SitOutRound, Choice, ResultsWaitPage, ResultsSummary]
