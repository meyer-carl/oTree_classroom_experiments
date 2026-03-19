from otree.api import *


doc = """
Volunteer's dilemma: each player decides whether to volunteer.
If at least one volunteers, everyone benefits, but volunteers pay a cost.
"""


class C(BaseConstants):
    NAME_IN_URL = 'volunteer_dilemma'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1

    NUM_OTHER_PLAYERS = PLAYERS_PER_GROUP - 1
    GENERAL_BENEFIT = cu(100)
    VOLUNTEER_COST = cu(40)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    num_volunteers = models.IntegerField()


class Player(BasePlayer):
    volunteer = models.BooleanField(
        label='Do you wish to volunteer?', doc="""Whether player volunteers"""
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
    players = group.get_players()
    group.num_volunteers = sum([p.volunteer for p in players])
    if group.num_volunteers > 0:
        baseline_amount = C.GENERAL_BENEFIT
    else:
        baseline_amount = cu(0)
    for p in players:
        p.payoff = baseline_amount
        if p.volunteer:
            p.payoff -= C.VOLUNTEER_COST


# PAGES
class Introduction(Page):
    pass


class Decision(Page):
    form_model = 'player'
    form_fields = ['volunteer']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    pass


page_sequence = [Unmatched, Introduction, Decision, ResultsWaitPage, Results]
