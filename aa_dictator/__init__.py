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
Dictator Game: One player decides how to divide a certain amount between themself and the other
player.
The code is slightly modified from the original oTree code, found
<a href="https://github.com/oTree-org/oTree/tree/lite" target="_blank">
    here
</a>.
"""

# Constants used throughout the app
class C(BaseConstants):
    NAME_IN_URL = 'dictator'  # URL name for the app
    PLAYERS_PER_GROUP = None  # Number of players in each group
    HEADCOUNT_GROUP_SIZE = 2
    NUM_ROUNDS = 4  # Maximum rounds used by classroom role-balanced presets
    LEGACY_ACTIVE_ROUNDS = 1
    ENDOWMENT = cu(100)  # Initial amount allocated to the dictator
    DICTATOR_ROLE = 'Dictator'
    RECIPIENT_ROLE = 'Recipient'

# Subsession class
class Subsession(BaseSubsession):
    pass

# Group-level data and logic
class Group(BaseGroup):
    # Field to store the amount the dictator decides to keep
    kept = models.CurrencyField(
        doc="""Amount dictator decided to keep for himself""",  # Documentation for the field
        min=0,  # Minimum value allowed
        max=C.ENDOWMENT,  # Maximum value allowed
        label="I will keep",  # Label shown to the dictator
    )

# Player-level data and logic
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


def role_name(player: Player):
    if role_balanced_classroom(player):
        return player.assigned_role
    return C.DICTATOR_ROLE if player.id_in_group == 1 else C.RECIPIENT_ROLE


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
                C.DICTATOR_ROLE,
                C.RECIPIENT_ROLE,
            )
            subsession.session.vars[ACTIVE_COUNT_KEY] = schedule_active_counts(schedule)

        role_map = subsession.session.vars[ROLE_KEY][subsession.round_number - 1]
        apply_pair_schedule(
            subsession,
            subsession.session.vars[SCHEDULE_KEY][subsession.round_number - 1],
            role_assignments=role_map,
            primary_role=C.DICTATOR_ROLE,
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


def assign_payoff(player: Player, raw_payoff):
    player.raw_round_payoff = raw_payoff
    if role_balanced_classroom(player) and role_cycle_payoff_rule(player) == 'average_active':
        active_count = player.session.vars[ACTIVE_COUNT_KEY].get(player.participant.code, 1)
        player.payoff = normalized_average_payoff(player, raw_payoff, active_count)
    else:
        player.payoff = raw_payoff

# FUNCTIONS
# Function to calculate and set payoffs for both players
def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)  # Get the dictator (player 1)
    p2 = group.get_player_by_id(2)  # Get the recipient (player 2)
    assign_payoff(p1, group.kept)  # Dictator's payoff is the amount they kept
    assign_payoff(p2, C.ENDOWMENT - group.kept)  # Recipient's payoff is the remainder

# PAGES
# Introduction page
class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.active_this_round

# Page where the dictator makes their decision
class Offer(Page):
    form_model = 'group'  # The form data is stored at the group level
    form_fields = ['kept']  # Field to be filled out by the dictator

    # Only display this page to the dictator (player 1)
    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round and role_name(player) == C.DICTATOR_ROLE

# Wait page to synchronize players and calculate payoffs
class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs  # Call set_payoffs after all P1 and P2 get to this page

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round

# Results page to display the outcome to both players
class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round

    # Pass variables to the template for display
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group  # Get the player's group

        # Return the amount offered to the recipient
        return dict(offer=C.ENDOWMENT - group.kept, role=role_name(player), raw_round_payoff=player.raw_round_payoff)

# Sequence of pages in the app
page_sequence = [Unmatched, SitOutRound, Introduction, Offer, ResultsWaitPage, Results]
