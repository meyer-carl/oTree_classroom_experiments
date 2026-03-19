from otree.api import *
import random

from classroom_utils import bool_config_value, currency_config_value

doc = """
Ultimatum Game: One player decides how to divide a certain amount between themself and the other
player.
The code is adapted from the Dicatator game, found
<a href="https://github.com/oTree-org/oTree/tree/lite" target="_blank">
    here
</a>.
"""

# Constants used throughout the app
class C(BaseConstants):
    NAME_IN_URL = 'ultimatum'  # URL name for the app
    PLAYERS_PER_GROUP = 2  # Number of players in each group
    NUM_ROUNDS = 1  # Number of rounds in the game
    ENDOWMENT = cu(100)  # Initial amount allocated to the Player 1
    USE_STRATEGY_METHOD = False  # Set to True or use session config 'use_strategy_method'

# Subsession class
class Subsession(BaseSubsession):
    pass

# Group-level data and logic
class Group(BaseGroup):
    # Field to store the amount the P1 decides to offer
    offer = models.CurrencyField(
        doc="""Amount P1 offers to P2""",  # Documentation for the field
        min=0,  # Minimum value allowed
        max=C.ENDOWMENT,  # Maximum value allowed
        label="I will offer",  # Label shown to the P1
    )
    accepted = models.BooleanField(
        doc="""Whether the offer was accepted by P2""",  # Documentation for the field
        choices=[
            [True, 'Yes'],
            [False, 'No'],
        ],
        label="Do you accept the offer?",  # Label shown to P2
        widget=widgets.RadioSelect,  # Radio button widget for selection
    )

# Player-level data and logic
class Player(BasePlayer):
    min_accept = models.CurrencyField(
        min=cu(0),
        max=C.ENDOWMENT,
        doc="""Minimum acceptable offer (strategy method)""",
        label="Minimum acceptable offer",
        blank=True,
    )


def ultimatum_endowment(context):
    return currency_config_value(context, 'ultimatum_endowment', C.ENDOWMENT)


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        session = subsession.session
        has_unmatched = any(
            len(g.get_players()) < C.PLAYERS_PER_GROUP for g in subsession.get_groups()
        )
        session.vars['ultimatum_force_strategy'] = has_unmatched


def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.PLAYERS_PER_GROUP


def use_strategy_method(player: Player):
    return bool_config_value(player, 'use_strategy_method', C.USE_STRATEGY_METHOD) or player.session.vars.get(
        'ultimatum_force_strategy', False
    )


def random_responder(player: Player):
    candidates = [
        p for p in player.subsession.get_players() if p.id_in_group == 2 and p != player
    ]
    return random.choice(candidates) if candidates else None


def responder_accepts_offer(responder: Player, offer):
    if use_strategy_method(responder) and responder.min_accept is not None:
        return offer >= responder.min_accept
    return responder.group.accepted

# FUNCTIONS
# Function to calculate and set payoffs for both players
def set_payoffs(group: Group):
    endowment = ultimatum_endowment(group)
    players = group.get_players()
    if len(players) < C.PLAYERS_PER_GROUP:
        lone_player = players[0]
        responder = random_responder(lone_player)
        accepted = responder_accepts_offer(responder, group.offer) if responder else False
        group.accepted = accepted
        if lone_player.id_in_group == 1:
            lone_player.payoff = endowment - group.offer if accepted else cu(0)
        else:
            lone_player.payoff = group.offer if accepted else cu(0)
        return

    p1 = group.get_player_by_id(1)  # Get the P1 (Player 1)
    p2 = group.get_player_by_id(2)  # Get the P2 (Player 2)

    if use_strategy_method(p2):
        group.accepted = group.offer >= p2.min_accept

    if group.accepted:  # Check if P2 accepted the offer
        p1.payoff = endowment - group.offer  # P1's payoff is the amount they kept
        p2.payoff = group.offer  # P2's payoff is the amount they accepted
    else:
        p1.payoff = cu(0)  # If P2 did not accept, P1 gets nothing
        p2.payoff = cu(0)  # If P2 did not accept, P2 gets nothing

# PAGES
# Introduction page
class Introduction(Page):
    """Explain instructions to both players."""

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endowment=ultimatum_endowment(player))

# Page where the P1 makes their decision
class Offer(Page):
    form_model = 'group'  # The form data is stored at the group level
    form_fields = ['offer']  # Field to be filled out by the P1

    # Only display this page to the P1 (player 1)
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endowment=ultimatum_endowment(player))

    @staticmethod
    def error_message(player: Player, values):
        if values['offer'] > ultimatum_endowment(player):
            return f"The offer cannot exceed the session endowment of {ultimatum_endowment(player)}."
    
# Wait page to synchronize players
class WaitForOtherPlayers(WaitPage):
    """Wait for other Players."""
    pass

# Page where the P2 responds to the offer
class Response(Page):
    """Player 2 decides whether to accept or reject."""
    form_model  = 'group'
    form_fields = ['accepted']

    # Only display this page to the P2 (player 2)
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2 and not use_strategy_method(player)

    # Pass variables to the template for display
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            offer = player.group.offer,
            endowment = ultimatum_endowment(player),
        )


class StrategyResponse(Page):
    form_model = 'player'
    form_fields = ['min_accept']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2 and use_strategy_method(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endowment=ultimatum_endowment(player))

# Wait page to synchronize players and calculate payoffs
class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs  # Call set_payoffs after all P1 and P2 get to this page

# Results page to display the outcome to both players
class Results(Page):
    # Pass variables to the template for display
    @staticmethod
    def vars_for_template(player: Player):
        endowment = ultimatum_endowment(player)
        return dict(
            offer    = player.group.offer,
            accepted = player.group.accepted,
            kept     = endowment - player.group.offer,
            endowment=endowment,
        )

# Wait for all groups so strategy responses are available for random matching
class StrategySyncWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player):
        return use_strategy_method(player)

# Sequence of pages in the app
page_sequence = [
    Introduction,
    StrategyResponse,
    Offer,
    WaitForOtherPlayers,
    Response,
    StrategySyncWaitPage,
    ResultsWaitPage,
    Results,
]
