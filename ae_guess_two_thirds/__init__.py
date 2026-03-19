from otree.api import *


doc = """
Keynesian beauty contest/ guess 2/3 of the average: Players all guess a number; whoever guesses closest to
2/3 of the average wins.
The code is slightly modified from the original oTree code, found
<a href="https://github.com/oTree-org/oTree/tree/lite" target="_blank">
    here
</a>.
"""


class C(BaseConstants):
    # Constants for the game
    PLAYERS_PER_GROUP = 2  # Number of players per group
    NUM_ROUNDS = 3  # Number of rounds in the game
    NAME_IN_URL = 'guess_two_thirds'  # URL name for the app
    JACKPOT = cu(100)  # Prize amount for winners
    GUESS_MAX = 100  # Maximum allowable guess


class Subsession(BaseSubsession):
    # Subsession class for managing rounds
    pass


class Group(BaseGroup):
    # Group-level variables
    two_thirds_avg = models.FloatField()  # Stores 2/3 of the average guess
    best_guess = models.IntegerField()  # Stores the closest guess to 2/3 of the average
    num_winners = models.IntegerField()  # Number of players who guessed correctly


class Player(BasePlayer):
    # Player-level variables
    guess = models.IntegerField(
        min=0, max=C.GUESS_MAX, label="Please pick a number from 0 to 100:"
    )  # Player's guess input
    is_winner = models.BooleanField(initial=False)  # Indicates if the player is a winner


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
    # Calculate payoffs for the group
    players = group.get_players()  # Get all players in the group
    guesses = [p.guess for p in players]  # Collect all guesses
    two_thirds_avg = (2 / 3) * sum(guesses) / len(players)  # Calculate 2/3 of the average guess
    group.two_thirds_avg = round(two_thirds_avg, 2)  # Store rounded value in group
    group.best_guess = min(guesses, key=lambda guess: abs(guess - group.two_thirds_avg))  # Find closest guess
    winners = [p for p in players if p.guess == group.best_guess]  # Identify winners
    group.num_winners = len(winners)  # Store number of winners
    for p in winners:
        p.is_winner = True  # Mark player as a winner
        p.payoff = C.JACKPOT / group.num_winners  # Distribute jackpot among winners


def two_thirds_avg_history(group: Group):
    # Retrieve the history of 2/3 average values from previous rounds
    return [g.two_thirds_avg for g in group.in_previous_rounds()]


# PAGES
class Introduction(Page):
    # Page to display instructions for the game
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Guess(Page):
    # Page where players make their guesses
    form_model = 'player'  # Specifies the model to use for the form
    form_fields = ['guess']  # Specifies the field(s) to include in the form

    @staticmethod
    def vars_for_template(player: Player):
        # Provide variables for the template
        group = player.group  # Get the player's group

        return dict(two_thirds_avg_history=two_thirds_avg_history(group))  # Pass the history of 2/3 averages


class ResultsWaitPage(WaitPage):
    # Wait page to synchronize players before showing results
    after_all_players_arrive = set_payoffs  # Function to calculate payoffs after all players submit their guesses


class Results(Page):
    # Page to display the results of the round
    @staticmethod
    def vars_for_template(player: Player):
        # Provide variables for the template
        group = player.group  # Get the player's group

        # Get all guesses from the group and sort them
        sorted_guesses = sorted(p.guess for p in group.get_players())
        return dict(sorted_guesses=sorted_guesses)  # Pass the sorted guesses to the template


# Sequence of pages in the app
page_sequence = [Unmatched, Introduction, Guess, ResultsWaitPage, Results]
