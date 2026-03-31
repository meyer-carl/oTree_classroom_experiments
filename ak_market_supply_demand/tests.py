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
            expected_price = cu(60)
            if self.case == 'truthful_bid_rule':
                original = APP.clearing_price_rule
                APP.clearing_price_rule = lambda context: 'bid'
                set_market_outcome(self.player.group)
                APP.clearing_price_rule = original
                expected_price = cu(70)
            elif self.case == 'truthful_ask_rule':
                original = APP.clearing_price_rule
                APP.clearing_price_rule = lambda context: 'ask'
                set_market_outcome(self.player.group)
                APP.clearing_price_rule = original
                expected_price = cu(50)
            expect(self.player.group.num_trades, 4)
            expect(self.player.group.clearing_price, expected_price)
            expect(self.player.traded, True)
            if self.player.is_buyer:
                expect(self.player.payoff, self.player.private_value - expected_price)
            else:
                expect(self.player.payoff, expected_price - self.player.private_cost)
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
