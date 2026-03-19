from otree.api import *
import random


doc = """
Two-sided auction (double auction with one buyer and one seller).
Both sides submit a price simultaneously. A trade occurs if bid >= ask.
The trade price is the midpoint of the two offers.
"""


class C(BaseConstants):
    NAME_IN_URL = 'two_sided_auction'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    VALUE_MIN = 60
    VALUE_MAX = 100
    COST_MIN = 0
    COST_MAX = 40

    PRICE_MIN = 0
    PRICE_MAX = 120


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    trade_price = models.CurrencyField(initial=cu(0))
    traded = models.BooleanField(initial=False)


class Player(BasePlayer):
    is_buyer = models.BooleanField()
    private_value = models.CurrencyField(initial=cu(0))
    private_cost = models.CurrencyField(initial=cu(0))
    offer_price = models.CurrencyField(
        min=C.PRICE_MIN,
        max=C.PRICE_MAX,
        label="Your price",
        doc="""Bid (buyer) or ask (seller)""",
    )

    def role(self):
        return 'Buyer' if self.is_buyer else 'Seller'

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
        players = group.get_players()
        random.shuffle(players)
        buyer = players[0]
        seller = players[1]

        buyer.is_buyer = True
        buyer.private_value = cu(random.randint(C.VALUE_MIN, C.VALUE_MAX))
        buyer.private_cost = cu(0)

        seller.is_buyer = False
        seller.private_cost = cu(random.randint(C.COST_MIN, C.COST_MAX))
        seller.private_value = cu(0)


def set_payoffs(group: Group):
    buyer = [p for p in group.get_players() if p.is_buyer][0]
    seller = [p for p in group.get_players() if not p.is_buyer][0]

    group.traded = False
    group.trade_price = cu(0)
    buyer.payoff = cu(0)
    seller.payoff = cu(0)

    if buyer.offer_price >= seller.offer_price:
        group.traded = True
        group.trade_price = (buyer.offer_price + seller.offer_price) / 2
        buyer.payoff = max(cu(0), buyer.private_value - group.trade_price)
        seller.payoff = max(cu(0), group.trade_price - seller.private_cost)


# PAGES
class Introduction(Page):
    pass


class Order(Page):
    form_model = 'player'
    form_fields = ['offer_price']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(role=player.role())

    @staticmethod
    def error_message(player: Player, values):
        price = values['offer_price']
        if player.is_buyer and price > player.private_value:
            return 'Your bid cannot exceed your private value.'
        if not player.is_buyer and price < player.private_cost:
            return 'Your ask cannot be below your private cost.'


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    pass


page_sequence = [Unmatched, Introduction, Order, ResultsWaitPage, Results]
