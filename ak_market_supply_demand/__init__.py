from otree.api import *
import random


doc = """
Market experiment with supply and demand using a single-call market.
Buyers submit bids and sellers submit asks for one unit. Orders are sorted to
find trades and a uniform clearing price. Payoffs depend on values and costs.
"""


class C(BaseConstants):
    NAME_IN_URL = 'market_supply_demand'
    NUM_ROUNDS = 1

    # Edit these lists to change the market size and value/cost schedules.
    BUYER_VALUES = [cu(100), cu(90), cu(80), cu(70)]
    SELLER_COSTS = [cu(20), cu(30), cu(40), cu(50)]

    NUM_BUYERS = len(BUYER_VALUES)
    NUM_SELLERS = len(SELLER_COSTS)
    PLAYERS_PER_GROUP = NUM_BUYERS + NUM_SELLERS

    PRICE_MIN = cu(0)
    PRICE_MAX = cu(120)

    # Options: 'midpoint', 'bid', 'ask'
    CLEARING_PRICE_RULE = 'midpoint'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    clearing_price = models.CurrencyField(initial=cu(0))
    num_trades = models.IntegerField(initial=0)


class Player(BasePlayer):
    is_buyer = models.BooleanField()
    private_value = models.CurrencyField(initial=cu(0))
    private_cost = models.CurrencyField(initial=cu(0))
    order_price = models.CurrencyField(
        min=C.PRICE_MIN,
        max=C.PRICE_MAX,
        label="Your order price",
        doc="""Bid (buyers) or ask (sellers) price""",
    )
    traded = models.BooleanField(initial=False)
    trade_price = models.CurrencyField(initial=cu(0))

    def role(self):
        return 'Buyer' if self.is_buyer else 'Seller'


# FUNCTIONS
def creating_session(subsession: Subsession):
    for group in subsession.get_groups():
        players = group.get_players()
        expected = C.NUM_BUYERS + C.NUM_SELLERS
        if len(players) != expected:
            # leave role/value assignment empty for unmatched groups
            for player in players:
                player.is_buyer = False
                player.private_value = cu(0)
                player.private_cost = cu(0)
            continue

        random.shuffle(players)
        buyer_values = C.BUYER_VALUES.copy()
        seller_costs = C.SELLER_COSTS.copy()
        random.shuffle(buyer_values)
        random.shuffle(seller_costs)

        buyers = players[: C.NUM_BUYERS]
        sellers = players[C.NUM_BUYERS :]

        for player, value in zip(buyers, buyer_values):
            player.is_buyer = True
            player.private_value = value
            player.private_cost = cu(0)

        for player, cost in zip(sellers, seller_costs):
            player.is_buyer = False
            player.private_cost = cost
            player.private_value = cu(0)


def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.PLAYERS_PER_GROUP


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


def _clearing_price(marginal_bid, marginal_ask):
    if C.CLEARING_PRICE_RULE == 'bid':
        return marginal_bid
    if C.CLEARING_PRICE_RULE == 'ask':
        return marginal_ask
    return (marginal_bid + marginal_ask) / 2


def set_market_outcome(group: Group):
    players = group.get_players()
    buyers = sorted(
        [p for p in players if p.is_buyer], key=lambda p: p.order_price, reverse=True
    )
    sellers = sorted([p for p in players if not p.is_buyer], key=lambda p: p.order_price)

    trades = []
    for buyer, seller in zip(buyers, sellers):
        if buyer.order_price >= seller.order_price:
            trades.append((buyer, seller))
        else:
            break

    group.num_trades = len(trades)
    group.clearing_price = cu(0)

    for p in players:
        p.traded = False
        p.trade_price = cu(0)
        p.payoff = cu(0)

    if trades:
        marginal_bid = buyers[len(trades) - 1].order_price
        marginal_ask = sellers[len(trades) - 1].order_price
        clearing_price = _clearing_price(marginal_bid, marginal_ask)
        group.clearing_price = clearing_price

        for buyer, seller in trades:
            buyer.traded = True
            seller.traded = True
            buyer.trade_price = clearing_price
            seller.trade_price = clearing_price
            buyer.payoff = max(cu(0), buyer.private_value - clearing_price)
            seller.payoff = max(cu(0), clearing_price - seller.private_cost)


# PAGES
class Introduction(Page):
    pass


class Order(Page):
    form_model = 'player'
    form_fields = ['order_price']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(role=player.role())

    @staticmethod
    def error_message(player: Player, values):
        price = values['order_price']
        if player.is_buyer and price > player.private_value:
            return 'Your bid cannot exceed your private value.'
        if not player.is_buyer and price < player.private_cost:
            return 'Your ask cannot be below your private cost.'


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_market_outcome


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        buyers = sorted(
            [p for p in group.get_players() if p.is_buyer],
            key=lambda p: p.order_price,
            reverse=True,
        )
        sellers = sorted(
            [p for p in group.get_players() if not p.is_buyer],
            key=lambda p: p.order_price,
        )
        return dict(buyers=buyers, sellers=sellers)


page_sequence = [Unmatched, Introduction, Order, ResultsWaitPage, Results]
