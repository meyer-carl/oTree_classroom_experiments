from otree.api import *
import random


doc = """
Common value auction: players bid on an item with the same true value.
Each player sees a noisy estimate of the value. Highest bidder wins and earns
(value - bid), floored at 0.
"""


class C(BaseConstants):
    NAME_IN_URL = 'common_value_auction'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 1

    BID_MIN = cu(0)
    BID_MAX = cu(10)
    BID_NOISE = cu(1)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    item_value = models.CurrencyField(
        doc="""Common value of the item to be auctioned"""
    )
    highest_bid = models.CurrencyField()


class Player(BasePlayer):
    item_value_estimate = models.CurrencyField(
        doc="""Estimate of the common value, may differ across players"""
    )
    bid_amount = models.CurrencyField(
        min=C.BID_MIN,
        max=C.BID_MAX,
        doc="""Amount bid by the player""",
        label="Bid amount",
    )
    is_winner = models.BooleanField(
        initial=False, doc="""Indicates whether the player is the winner"""
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
def creating_session(subsession: Subsession):
    for group in subsession.get_groups():
        item_value = random.uniform(float(C.BID_MIN), float(C.BID_MAX))
        group.item_value = cu(round(item_value, 1))


def generate_value_estimate(group: Group):
    estimate = group.item_value + random.uniform(-C.BID_NOISE, C.BID_NOISE)
    estimate = round(float(estimate), 1)
    if estimate < float(C.BID_MIN):
        estimate = float(C.BID_MIN)
    if estimate > float(C.BID_MAX):
        estimate = float(C.BID_MAX)
    return cu(estimate)


def set_payoff(player: Player):
    group = player.group

    if player.is_winner:
        player.payoff = group.item_value - player.bid_amount
        if player.payoff < 0:
            player.payoff = cu(0)
    else:
        player.payoff = cu(0)


def set_winner(group: Group):
    players = group.get_players()
    group.highest_bid = max([p.bid_amount for p in players])
    players_with_highest_bid = [p for p in players if p.bid_amount == group.highest_bid]
    winner = random.choice(players_with_highest_bid)
    winner.is_winner = True
    for p in players:
        set_payoff(p)


# PAGES
class Introduction(Page):
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.item_value_estimate = generate_value_estimate(player.group)


class Bid(Page):
    form_model = 'player'
    form_fields = ['bid_amount']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_winner


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(is_greedy=group.item_value - player.bid_amount < 0)


page_sequence = [Unmatched, Introduction, Bid, ResultsWaitPage, Results]
