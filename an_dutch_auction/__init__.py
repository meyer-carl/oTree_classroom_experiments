from otree.api import *
import random


doc = """
Dutch auction (descending price).
Players submit the price at which they would stop the clock.
The highest stop price wins and pays their own price.
"""


class C(BaseConstants):
    NAME_IN_URL = 'dutch_auction'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 1

    VALUE_MIN = 60
    VALUE_MAX = 120

    PRICE_MIN = 0
    PRICE_MAX = 150
    RESERVE_PRICE = 0


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    winning_price = models.CurrencyField(initial=cu(0))
    sold = models.BooleanField(initial=False)


class Player(BasePlayer):
    private_value = models.CurrencyField(initial=cu(0))
    stop_price = models.CurrencyField(
        min=C.PRICE_MIN,
        max=C.PRICE_MAX,
        label="Stop price",
        doc="""Price at which the player would stop the auction""",
    )
    is_winner = models.BooleanField(initial=False)


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
def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        p.private_value = cu(random.randint(C.VALUE_MIN, C.VALUE_MAX))


def set_payoffs(group: Group):
    players = group.get_players()
    highest = max([p.stop_price for p in players])

    if highest < cu(C.RESERVE_PRICE):
        group.sold = False
        group.winning_price = cu(0)
        for p in players:
            p.is_winner = False
            p.payoff = cu(0)
        return

    winners = [p for p in players if p.stop_price == highest]
    winner = random.choice(winners)

    group.sold = True
    group.winning_price = highest

    for p in players:
        p.is_winner = p == winner
        if p.is_winner:
            p.payoff = max(cu(0), p.private_value - group.winning_price)
        else:
            p.payoff = cu(0)


# PAGES
class Introduction(Page):
    pass


class StopPrice(Page):
    form_model = 'player'
    form_fields = ['stop_price']

    @staticmethod
    def error_message(player: Player, values):
        price = values['stop_price']
        if price > player.private_value:
            return 'Your stop price cannot exceed your private value.'


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    pass


page_sequence = [Unmatched, Introduction, StopPrice, ResultsWaitPage, Results]
