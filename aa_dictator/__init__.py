from otree.api import *

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
    PLAYERS_PER_GROUP = 2  # Number of players in each group
    NUM_ROUNDS = 1  # Number of rounds in the game
    ENDOWMENT = cu(100)  # Initial amount allocated to the dictator

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
    pass

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
# Function to calculate and set payoffs for both players
def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)  # Get the dictator (player 1)
    p2 = group.get_player_by_id(2)  # Get the recipient (player 2)
    p1.payoff = group.kept  # Dictator's payoff is the amount they kept
    p2.payoff = C.ENDOWMENT - group.kept  # Recipient's payoff is the remainder

# PAGES
# Introduction page
class Introduction(Page):
    pass

# Page where the dictator makes their decision
class Offer(Page):
    form_model = 'group'  # The form data is stored at the group level
    form_fields = ['kept']  # Field to be filled out by the dictator

    # Only display this page to the dictator (player 1)
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1

# Wait page to synchronize players and calculate payoffs
class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs  # Call set_payoffs after all P1 and P2 get to this page

# Results page to display the outcome to both players
class Results(Page):
    # Pass variables to the template for display
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group  # Get the player's group

        # Return the amount offered to the recipient
        return dict(offer=C.ENDOWMENT - group.kept)

# Sequence of pages in the app
page_sequence = [Unmatched, Introduction, Offer, ResultsWaitPage, Results]
