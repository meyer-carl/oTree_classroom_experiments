from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    cases = ["trade", "no_trade"]

    def play_round(self):
        if self.round_number == 1:
            yield Introduction

        if self.case == "trade":
            if self.round_number == 1:
                if self.player.id_in_group == 1:
                    yield SubmissionMustFail(Trade, dict(action="buy"))
                    yield Trade, dict(action="buy", order_price=cu(70))
                elif self.player.id_in_group == 2:
                    yield SubmissionMustFail(Trade, dict(action="sell"))
                    yield Trade, dict(action="sell", order_price=cu(50))
                else:
                    yield Trade, dict(action="hold")
            else:
                yield Trade, dict(action="hold")
        else:
            if self.player.id_in_group == 1:
                yield SubmissionMustFail(Trade, dict(action="buy", order_price=cu(125)))
                yield Trade, dict(action="buy", order_price=cu(40))
            elif self.player.id_in_group == 2:
                yield Trade, dict(action="sell", order_price=cu(80))
            else:
                yield Trade, dict(action="hold")

        yield Results

        if self.round_number == 1:
            if self.case == "trade":
                expect(self.group.quantity_traded, 1)
                expect(self.group.clearing_price, cu(60))
            else:
                expect(self.group.quantity_traded, 0)
                expect(self.group.clearing_price, cu(0))

        if self.round_number == C.NUM_ROUNDS:
            if self.case == "trade":
                expected = {
                    1: cu(220),
                    2: cu(260),
                    3: cu(240),
                    4: cu(240),
                }[self.player.id_in_group]
            else:
                expected = cu(240)
            expect(self.player.payoff, expected)
