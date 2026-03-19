from otree.api import *
import random

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
    PLAYERS_PER_GROUP = 2  # Number of players per group
    NUM_ROUNDS = 4  # Total number of rounds in the game
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
    is_winner = models.BooleanField()

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

# Function to set up the session
def creating_session(subsession: Subsession):
    session = subsession.session

    if subsession.round_number == 1:
        # Randomly assign groups for the first round
        subsession.group_randomly()
        # Randomly select a paying round between 1 and the total number of rounds
        paying_round = random.randint(1, C.NUM_ROUNDS)
        session.vars['paying_round'] = paying_round  # Store the paying round in session variables

    elif subsession.round_number == 2:
        subsession.group_like_round(1)

    elif subsession.round_number == 3:
        # swap roles by reversing id_in_group in each group
        for group in subsession.get_groups():
            p1 = group.get_player_by_id(1)
            p2 = group.get_player_by_id(2)
            group.set_players([p2, p1])  # now they have swapped positions/roles

    else:  # rounds >3
        subsession.group_like_round(3)

# Function to calculate payoffs for the group
def set_payoffs(group: Group):
    subsession = group.subsession
    session = group.session

    # Get the two players in the group
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)

    # Determine the winner and calculate payoffs
    for p in [p1, p2]:
        is_matcher = p.role == C.MATCHER_ROLE  # Check if the player is the matcher
        p.is_winner = (p1.penny_side == p2.penny_side) == is_matcher  # Determine if the player wins
        # Assign payoff only if it's the paying round and the player is a winner
        if subsession.round_number == session.vars['paying_round'] and p.is_winner:
            p.payoff = C.STAKES
        else:
            p.payoff = cu(0)

# PAGES

# Page where players make their choice
class Choice(Page):
    form_model = 'player'  # Model for the form
    form_fields = ['penny_side']  # Fields to be filled in the form

    @staticmethod
    def vars_for_template(player: Player):
        # Provide data for the template, including the player's history in previous rounds
        return dict(player_in_previous_rounds=player.in_previous_rounds())

# Wait page to calculate results after all players have made their choices
class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs  # Call the set_payoffs function after all players arrive

# Page to display the summary of results
class ResultsSummary(Page):
    @staticmethod
    def is_displayed(player: Player):
        # Display this page only in the final round
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        session = player.session

        # Get the player's data from all rounds
        player_in_all_rounds = player.in_all_rounds()
        return dict(
            total_payoff=sum([p.payoff for p in player_in_all_rounds]),  # Total payoff across all rounds
            paying_round=session.vars['paying_round'],  # The paying round
            player_in_all_rounds=player_in_all_rounds,  # Player's data from all rounds
        )

# Sequence of pages in the game
page_sequence = [Unmatched, Choice, ResultsWaitPage, ResultsSummary]
