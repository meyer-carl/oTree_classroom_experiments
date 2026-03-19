from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    cases = ['truthful_midpoint', 'no_trade', 'guardrails']

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
            order_price = C.PRICE_MAX if self.case == 'no_trade' else self.player.private_cost
            yield Order, dict(order_price=order_price)

        if self.case == 'no_trade':
            expect(self.player.group.num_trades, 0)
            expect(self.player.group.clearing_price, cu(0))
            expect(self.player.traded, False)
            expect(self.player.payoff, cu(0))
        else:
            expect(self.player.group.num_trades, 4)
            expect(self.player.group.clearing_price, cu(60))
            expect(self.player.traded, True)
            if self.player.is_buyer:
                expect(self.player.payoff, self.player.private_value - cu(60))
            else:
                expect(self.player.payoff, cu(60) - self.player.private_cost)
        yield Results
