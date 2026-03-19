from otree.api import *


doc = """
Cournot competition: firms choose quantities. The unit price falls as total
output rises. Payoff equals unit price times own quantity.
"""


class C(BaseConstants):
    NAME_IN_URL = 'cournot'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    TOTAL_CAPACITY = 60
    MAX_UNITS_PER_PLAYER = int(TOTAL_CAPACITY / PLAYERS_PER_GROUP)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    unit_price = models.CurrencyField()
    total_units = models.IntegerField(doc="""Total units produced by all players""")


class Player(BasePlayer):
    units = models.IntegerField(
        min=0,
        max=C.MAX_UNITS_PER_PLAYER,
        doc="""Quantity of units to produce""",
        label="How many units will you produce?",
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
    group.total_units = sum([p.units for p in players])
    group.unit_price = C.TOTAL_CAPACITY - group.total_units
    for p in players:
        p.payoff = group.unit_price * p.units


def other_player(player: Player):
    return player.get_others_in_group()[0]


# PAGES
class Introduction(Page):
    pass


class Decide(Page):
    form_model = 'player'
    form_fields = ['units']


class ResultsWaitPage(WaitPage):
    body_text = "Waiting for the other participant to decide."
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(other_player_units=other_player(player).units)


page_sequence = [Unmatched, Introduction, Decide, ResultsWaitPage, Results]
