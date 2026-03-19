from otree.api import *
import random


doc = """
Bertrand competition: 2 firms simultaneously set prices for a homogeneous good.
The firm with the lower price wins the market; ties are broken at random.
"""


class C(BaseConstants):
    NAME_IN_URL = 'bertrand'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    MAXIMUM_PRICE = cu(100)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    winning_price = models.CurrencyField()


class Player(BasePlayer):
    price = models.CurrencyField(
        min=0,
        max=C.MAXIMUM_PRICE,
        doc="""Price chosen by the firm""",
        label="Please enter a price",
    )
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
def set_payoffs(group: Group):
    players = group.get_players()
    group.winning_price = min([p.price for p in players])
    winners = [p for p in players if p.price == group.winning_price]
    winner = random.choice(winners)
    for p in players:
        if p == winner:
            p.is_winner = True
            p.payoff = p.price
        else:
            p.is_winner = False
            p.payoff = cu(0)


# PAGES
class Introduction(Page):
    pass


class Decide(Page):
    form_model = 'player'
    form_fields = ['price']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    pass


page_sequence = [Unmatched, Introduction, Decide, ResultsWaitPage, Results]
