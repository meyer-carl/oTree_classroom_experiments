from otree.api import *
import math
import random

from classroom_utils import (
    bool_config_value,
    currency_config_value,
    currency_list_config_value,
    group_matrix_for_sizes,
    is_incomplete_group,
    int_config_value,
    next_app,
    partition_group_sizes,
    session_config_value,
    unmatched_template_vars,
)


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
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = NUM_BUYERS + NUM_SELLERS

    PRICE_MIN = cu(0)
    PRICE_MAX = cu(120)
    PRICE_STEP = 5

    # Options: 'midpoint', 'bid', 'ask'
    CLEARING_PRICE_RULE = 'midpoint'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    clearing_price = models.CurrencyField(initial=cu(0))
    num_trades = models.IntegerField(initial=0)
    actual_num_buyers = models.IntegerField(initial=0)
    actual_num_sellers = models.IntegerField(initial=0)
    buyer_schedule_csv = models.LongStringField(initial='')
    seller_schedule_csv = models.LongStringField(initial='')


class Player(BasePlayer):
    is_buyer = models.BooleanField()
    private_value = models.CurrencyField(initial=cu(0))
    private_cost = models.CurrencyField(initial=cu(0))
    order_price = models.CurrencyField(
        min=C.PRICE_MIN,
        label="Your order price",
        doc="""Bid (buyers) or ask (sellers) price""",
    )
    traded = models.BooleanField(initial=False)
    trade_price = models.CurrencyField(initial=cu(0))

    def role(self):
        return 'Buyer' if self.is_buyer else 'Seller'


def buyer_values(context):
    if classroom_whole_market(context):
        return generated_buyer_values(context, actual_market_buyer_count(context))
    return currency_list_config_value(context, 'buyer_values', C.BUYER_VALUES)


def seller_costs(context):
    if classroom_whole_market(context):
        return generated_seller_costs(context, actual_market_seller_count(context))
    return currency_list_config_value(context, 'seller_costs', C.SELLER_COSTS)


def required_group_size(context):
    if classroom_whole_market(context):
        return market_min_headcount(context)
    return len(buyer_values(context)) + len(seller_costs(context))


def classroom_whole_market(context):
    return bool_config_value(context, 'classroom_whole_market', False)


def market_min_headcount(context):
    return int_config_value(context, 'market_min_headcount', 4)


def buyer_value_high(context):
    return currency_config_value(context, 'buyer_value_high', C.BUYER_VALUES[0])


def buyer_value_low(context):
    return currency_config_value(context, 'buyer_value_low', C.BUYER_VALUES[-1])


def seller_cost_low(context):
    return currency_config_value(context, 'seller_cost_low', C.SELLER_COSTS[0])


def seller_cost_high(context):
    return currency_config_value(context, 'seller_cost_high', C.SELLER_COSTS[-1])


def round_classroom_price(value):
    return cu(int(round(float(value) / C.PRICE_STEP) * C.PRICE_STEP))


def linear_schedule(count, start, end):
    if count <= 0:
        return []
    if count == 1:
        return [round_classroom_price(start)]
    step = (end - start) / (count - 1)
    values = [round_classroom_price(start + step * index) for index in range(count)]
    return values


def generated_buyer_values(context, count):
    values = linear_schedule(count, buyer_value_high(context), buyer_value_low(context))
    return sorted(values, reverse=True)


def generated_seller_costs(context, count):
    values = linear_schedule(count, seller_cost_low(context), seller_cost_high(context))
    return sorted(values)


def actual_market_headcount(context):
    group = getattr(context, 'group', None)
    if group:
        return len(group.get_players())
    subsession = getattr(context, 'subsession', None)
    if subsession:
        return len(subsession.get_players())
    return int_config_value(context, 'num_demo_participants', C.HEADCOUNT_GROUP_SIZE)


def actual_market_buyer_count(context):
    group = getattr(context, 'group', None)
    if group and group.actual_num_buyers:
        return group.actual_num_buyers
    total_players = actual_market_headcount(context)
    if classroom_whole_market(context):
        return math.ceil(total_players / 2)
    return len(currency_list_config_value(context, 'buyer_values', C.BUYER_VALUES))


def actual_market_seller_count(context):
    group = getattr(context, 'group', None)
    if group and group.actual_num_sellers:
        return group.actual_num_sellers
    total_players = actual_market_headcount(context)
    if classroom_whole_market(context):
        return total_players - actual_market_buyer_count(context)
    return len(currency_list_config_value(context, 'seller_costs', C.SELLER_COSTS))


def schedule_csv(values):
    return ", ".join(str(int(value)) for value in values)


def clearing_price_rule(context):
    rule = session_config_value(context, 'clearing_price_rule', C.CLEARING_PRICE_RULE)
    return rule if rule in {'midpoint', 'bid', 'ask'} else C.CLEARING_PRICE_RULE


def market_price_cap(context):
    configured_prices = buyer_values(context) + seller_costs(context)
    return max(configured_prices) if configured_prices else C.PRICE_MAX


# FUNCTIONS
def creating_session(subsession: Subsession):
    if classroom_whole_market(subsession):
        subsession.set_group_matrix([list(subsession.get_players())])
    else:
        players = list(subsession.get_players())
        subsession.set_group_matrix(
            group_matrix_for_sizes(
                players,
                partition_group_sizes(
                    len(players),
                    C.HEADCOUNT_GROUP_SIZE,
                    allow_variable_group_sizes=False,
                    minimum_group_size=1,
                ),
            )
        )

    for group in subsession.get_groups():
        players = group.get_players()
        expected = required_group_size(subsession)
        if len(players) < expected:
            # leave role/value assignment empty for unmatched groups
            group.actual_num_buyers = 0
            group.actual_num_sellers = 0
            group.buyer_schedule_csv = ''
            group.seller_schedule_csv = ''
            for player in players:
                player.is_buyer = False
                player.private_value = cu(0)
                player.private_cost = cu(0)
            continue

        random.shuffle(players)
        if classroom_whole_market(subsession):
            buyer_count = math.ceil(len(players) / 2)
            seller_count = len(players) - buyer_count
            session_buyer_values = generated_buyer_values(subsession, buyer_count)
            session_seller_costs = generated_seller_costs(subsession, seller_count)
        else:
            session_buyer_values = buyer_values(subsession)
            session_seller_costs = seller_costs(subsession)

        random.shuffle(session_buyer_values)
        random.shuffle(session_seller_costs)

        group.actual_num_buyers = len(session_buyer_values)
        group.actual_num_sellers = len(session_seller_costs)
        group.buyer_schedule_csv = schedule_csv(sorted(session_buyer_values, reverse=True))
        group.seller_schedule_csv = schedule_csv(sorted(session_seller_costs))

        buyers = players[: len(session_buyer_values)]
        sellers = players[len(session_buyer_values) :]

        for player, value in zip(buyers, session_buyer_values):
            player.is_buyer = True
            player.private_value = value
            player.private_cost = cu(0)

        for player, cost in zip(sellers, session_seller_costs):
            player.is_buyer = False
            player.private_cost = cost
            player.private_value = cu(0)


def is_unmatched(player: Player):
    return is_incomplete_group(player, required_group_size(player))


class Unmatched(Page):
    template_name = 'global/Unmatched.html'

    @staticmethod
    def is_displayed(player: Player):
        return is_unmatched(player) and player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return unmatched_template_vars(required_group_size(player))

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return next_app(upcoming_apps)


def _clearing_price(context, marginal_bid, marginal_ask):
    if clearing_price_rule(context) == 'bid':
        return marginal_bid
    if clearing_price_rule(context) == 'ask':
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
        clearing_price = _clearing_price(group, marginal_bid, marginal_ask)
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
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            num_buyers=player.group.actual_num_buyers or len(buyer_values(player)),
            num_sellers=player.group.actual_num_sellers or len(seller_costs(player)),
            clearing_rule=clearing_price_rule(player),
            classroom_whole_market=classroom_whole_market(player),
            buyer_schedule_csv=player.group.buyer_schedule_csv or schedule_csv(sorted(buyer_values(player), reverse=True)),
            seller_schedule_csv=player.group.seller_schedule_csv or schedule_csv(sorted(seller_costs(player))),
            total_traders=len(player.group.get_players()),
        )


class Order(Page):
    form_model = 'player'
    form_fields = ['order_price']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            role=player.role(),
            price_cap=market_price_cap(player),
            total_traders=len(player.group.get_players()),
            num_buyers=player.group.actual_num_buyers or len(buyer_values(player)),
            num_sellers=player.group.actual_num_sellers or len(seller_costs(player)),
        )

    @staticmethod
    def error_message(player: Player, values):
        price = values['order_price']
        if price < C.PRICE_MIN or price > market_price_cap(player):
            return f"Order price must be between {C.PRICE_MIN} and {market_price_cap(player)} for this session."
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
        return dict(
            buyers=buyers,
            sellers=sellers,
            clearing_rule=clearing_price_rule(player),
            total_traders=len(group.get_players()),
            num_buyers=group.actual_num_buyers or len(buyer_values(player)),
            num_sellers=group.actual_num_sellers or len(seller_costs(player)),
            buyer_schedule_csv=group.buyer_schedule_csv or schedule_csv(sorted(buyer_values(player), reverse=True)),
            seller_schedule_csv=group.seller_schedule_csv or schedule_csv(sorted(seller_costs(player))),
            classroom_whole_market=classroom_whole_market(player),
        )


page_sequence = [Unmatched, Introduction, Order, ResultsWaitPage, Results]
