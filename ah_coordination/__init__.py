from otree.api import *
import random

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
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 4
    STAKES = cu(100)  # payoff each gets if they coordinate on the paying round

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    penny_side = models.StringField(
        choices=[['Heads', 'Heads'], ['Tails', 'Tails']],
        widget=widgets.RadioSelect,
        label="I choose:",
    )
    coordinated = models.BooleanField(doc="Whether this player successfully coordinated this round")

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

# SESSION SETUP
def creating_session(subsession: Subsession):
    session = subsession.session

    if subsession.round_number == 1:
        # random pairing to start
        subsession.group_randomly()
        # choose one round to pay
        paying_round = random.randint(1, C.NUM_ROUNDS)
        session.vars['paying_round'] = paying_round
    else:
        # keep same pairs after round 1
        subsession.group_like_round(1)

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
        if subsession.round_number == session.vars['paying_round'] and coordinated:
            p.payoff = C.STAKES
        else:
            p.payoff = cu(0)

# PAGES
class Choice(Page):
    form_model = 'player'
    form_fields = ['penny_side']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            player_in_previous_rounds=player.in_previous_rounds()
        )

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

class ResultsSummary(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        session = player.session
        player_in_all_rounds = player.in_all_rounds()
        return dict(
            total_payoff=sum([p.payoff for p in player_in_all_rounds]),
            paying_round=session.vars['paying_round'],
            player_in_all_rounds=player_in_all_rounds,
        )

page_sequence = [Unmatched, Choice, ResultsWaitPage, ResultsSummary]
