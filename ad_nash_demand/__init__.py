from otree.api import *

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
    PLAYERS_PER_GROUP = 2  # Number of players in each group
    NUM_ROUNDS = 1  # Number of rounds in the game
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


# Helper to detect incomplete groups
def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.PLAYERS_PER_GROUP


# Page to notify unmatched participants and skip the app
class Unmatched(Page):
    template_name = 'global/Unmatched.html'

    @staticmethod
    def is_displayed(player: Player):
        return is_unmatched(player) and player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(required_size=C.PLAYERS_PER_GROUP)

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return upcoming_apps[0] if upcoming_apps else None


# FUNCTIONS
def set_payoffs(group: Group):
    # Function to calculate payoffs for the group
    players = group.get_players()  # Get all players in the group
    group.total_requests = sum([p.request for p in players])  # Calculate total requests
    if group.total_requests <= C.AMOUNT_SHARED:
        # If total requests are within the available amount, each player gets their requested amount
        for p in players:
            p.payoff = p.request
    else:
        # If total requests exceed the available amount, all players get nothing
        for p in players:
            p.payoff = cu(0)


def other_player(player: Player):
    # Helper function to get the other player in the group
    return player.get_others_in_group()[0]


# PAGES
class Introduction(Page):
    # Introduction page for the game
    pass


class Request(Page):
    # Page where players make their requests
    form_model = 'player'  # Model to store the form data
    form_fields = ['request']  # Fields to be filled in the form


class ResultsWaitPage(WaitPage):
    # Wait page to synchronize players and calculate payoffs
    after_all_players_arrive = set_payoffs  # Function to call after all players arrive


class Results(Page):
    # Results page to display outcomes
    @staticmethod
    def vars_for_template(player: Player):
        # Variables to pass to the template
        return dict(other_player_request=other_player(player).request)


# Sequence of pages in the game
page_sequence = [Unmatched, Introduction, Request, ResultsWaitPage, Results]
