from types import SimpleNamespace

from otree.api import Bot, SubmissionMustFail, expect
import sys
from . import *

APP = sys.modules[__package__]


class PlayerBot(Bot):
    cases = ['truthful_midpoint', 'truthful_bid_rule', 'truthful_ask_rule', 'no_trade', 'guardrails']

    def play_round(self):
        yield Introduction

        if self.case == 'guardrails':
            if self.player.is_buyer:
                yield SubmissionMustFail(
                    Order,
                    dict(order_price=self.player.private_value + cu(1)),
                )
            else:
                yield SubmissionMustFail(
                    Order,
                    dict(order_price=self.player.private_cost - cu(1)),
                )

        if self.player.is_buyer:
            order_price = cu(0) if self.case == 'no_trade' else self.player.private_value
            yield Order, dict(order_price=order_price)
        else:
            order_price = self.player.private_cost
            yield Order, dict(order_price=order_price)

        if self.case == 'no_trade':
            expect(self.player.group.num_trades, 0)
            expect(self.player.group.clearing_price, cu(0))
            expect(self.player.traded, False)
            expect(self.player.payoff, cu(0))
        else:
            buyers = sorted(
                [p for p in self.player.group.get_players() if p.is_buyer],
                key=lambda p: p.order_price,
                reverse=True,
            )
            sellers = sorted(
                [p for p in self.player.group.get_players() if not p.is_buyer],
                key=lambda p: p.order_price,
            )
            expected_trades = 0
            for buyer, seller in zip(buyers, sellers):
                if buyer.order_price >= seller.order_price:
                    expected_trades += 1
                else:
                    break
            expect(self.player.group.num_trades, expected_trades)
            expected_price = cu(0)
            if expected_trades:
                marginal_bid = buyers[expected_trades - 1].order_price
                marginal_ask = sellers[expected_trades - 1].order_price
                expected_price = APP._clearing_price(self.player.group, marginal_bid, marginal_ask)
            expect(self.player.group.clearing_price, expected_price)
            expected_trading_buyers = buyers[:expected_trades]
            expected_trading_sellers = sellers[:expected_trades]
            expected_traded = self.player in expected_trading_buyers or self.player in expected_trading_sellers
            expect(self.player.traded, expected_traded)
            if self.player.is_buyer and expected_traded:
                expect(self.player.payoff, self.player.private_value - expected_price)
            elif not self.player.is_buyer and expected_traded:
                expect(self.player.payoff, expected_price - self.player.private_cost)
            else:
                expect(self.player.payoff, cu(0))
        yield Results


def test_market_price_cap_tracks_configured_schedule():
    session = SimpleNamespace(config={'buyer_values': [150, 140], 'seller_costs': [130, 120]})
    buyer = SimpleNamespace(
        session=session,
        is_buyer=True,
        private_value=cu(150),
        private_cost=cu(0),
    )
    seller = SimpleNamespace(
        session=session,
        is_buyer=False,
        private_value=cu(0),
        private_cost=cu(130),
    )

    assert market_price_cap(buyer) == cu(150)
    assert Order.error_message(buyer, {'order_price': cu(150)}) is None
    assert Order.error_message(seller, {'order_price': cu(130)}) is None
    assert (
        Order.error_message(buyer, {'order_price': cu(151)})
        == f'Order price must be between {C.PRICE_MIN} and {cu(150)} for this session.'
    )


def test_whole_class_market_split_uses_actual_attendance():
    session = SimpleNamespace(config={'classroom_whole_market': True})
    group = SimpleNamespace(
        session=session,
        actual_num_buyers=3,
        actual_num_sellers=2,
        get_players=lambda: [1, 2, 3, 4, 5],
    )

    assert actual_market_buyer_count(group) == 3
    assert actual_market_seller_count(group) == 2
    assert generated_buyer_values(group, 3) == [cu(100), cu(85), cu(70)]
    assert generated_seller_costs(group, 2) == [cu(20), cu(50)]
