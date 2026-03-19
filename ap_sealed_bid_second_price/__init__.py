from otree.api import *
import random


doc = """
Sealed-bid, second-price (Vickrey) auction.
Players submit bids simultaneously. Highest bidder wins and pays the second-highest bid.
"""


class C(BaseConstants):
    NAME_IN_URL = 'sealed_bid_second_price'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 1

    VALUE_MIN = 60
    VALUE_MAX = 120

    BID_MIN = 0
    BID_MAX = 150
    RESERVE_PRICE = 0


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    highest_bid = models.CurrencyField(initial=cu(0))
    second_highest_bid = models.CurrencyField(initial=cu(0))
    winning_price = models.CurrencyField(initial=cu(0))
    sold = models.BooleanField(initial=False)


class Player(BasePlayer):
    private_value = models.CurrencyField(initial=cu(0))
    bid = models.CurrencyField(
        min=C.BID_MIN,
        max=C.BID_MAX,
        label="Your bid",
        doc="""Sealed bid amount""",
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
    sorted_bids = sorted([p.bid for p in players], reverse=True)
    highest = sorted_bids[0]
    second_highest = sorted_bids[1] if len(sorted_bids) > 1 else cu(0)

    group.highest_bid = highest
    group.second_highest_bid = second_highest

    if highest < cu(C.RESERVE_PRICE):
        group.sold = False
        group.winning_price = cu(0)
        for p in players:
            p.is_winner = False
            p.payoff = cu(0)
        return

    winners = [p for p in players if p.bid == highest]
    winner = random.choice(winners)

    price = max(cu(C.RESERVE_PRICE), second_highest)

    group.sold = True
    group.winning_price = price

    for p in players:
        p.is_winner = p == winner
        if p.is_winner:
            p.payoff = max(cu(0), p.private_value - price)
        else:
            p.payoff = cu(0)


# PAGES
class Introduction(Page):
    pass


class Bid(Page):
    form_model = 'player'
    form_fields = ['bid']

    @staticmethod
    def error_message(player: Player, values):
        bid = values['bid']
        if bid > player.private_value:
            return 'Your bid cannot exceed your private value.'


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    pass


page_sequence = [Unmatched, Introduction, Bid, ResultsWaitPage, Results]
