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
This Nash Demand game involves 2 players. Each demands for a portion of some
available amount. If the sum of demands is no larger than the available
amount, both players get demanded portions. Otherwise, both get nothing.
The code is slightly modified from the original oTree code, found
<a href="https://github.com/oTree-org/oTree/tree/lite" target="_blank">
    here
</a>.
"""


class C(BaseConstants):
    # Constants for the game
    NAME_IN_URL = 'nash_demand'  # URL name for the app
    PLAYERS_PER_GROUP = None  # Number of players in each group
    HEADCOUNT_GROUP_SIZE = 2
    NUM_ROUNDS = 4  # Maximum rounds used by classroom pair-cycle presets
    AMOUNT_SHARED = cu(100)  # Total amount available to be shared


class Subsession(BaseSubsession):
    # Subsession class, used to define session-level data
    pass


class Group(BaseGroup):
    # Group-level data
    total_requests = models.CurrencyField()  # Total amount requested by all players in the group


class Player(BasePlayer):
    # Player-level data
    request = models.CurrencyField(
        doc="""
        Amount requested by this player.
        """,  # Documentation for the field
        min=0,  # Minimum value for the request
        max=C.AMOUNT_SHARED,  # Maximum value for the request
        label=f"Please enter an amount from 0 to {C.AMOUNT_SHARED}",  # Label for the input field
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
    # Function to calculate payoffs for the group
    players = group.get_players()  # Get all players in the group
    group.total_requests = sum([p.request for p in players])  # Calculate total requests
    if group.total_requests <= C.AMOUNT_SHARED:
        # If total requests are within the available amount, each player gets their requested amount
        for p in players:
            assign_payoff(p, p.request)
    else:
        # If total requests exceed the available amount, all players get nothing
        for p in players:
            assign_payoff(p, cu(0))


def other_player(player: Player):
    # Helper function to get the other player in the group
    return player.get_others_in_group()[0]


# PAGES
class Introduction(Page):
    # Introduction page for the game
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.active_this_round


class Request(Page):
    # Page where players make their requests
    form_model = 'player'  # Model to store the form data
    form_fields = ['request']  # Fields to be filled in the form

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round


class ResultsWaitPage(WaitPage):
    # Wait page to synchronize players and calculate payoffs
    after_all_players_arrive = set_payoffs  # Function to call after all players arrive

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round


class Results(Page):
    # Results page to display outcomes
    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round

    @staticmethod
    def vars_for_template(player: Player):
        # Variables to pass to the template
        return dict(
            other_player_request=other_player(player).request,
            raw_round_payoff=player.raw_round_payoff,
        )


# Sequence of pages in the game
page_sequence = [Unmatched, SitOutRound, Introduction, Request, ResultsWaitPage, Results]
