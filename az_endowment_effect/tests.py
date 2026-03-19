from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction

        if self.player.id_in_group == 1:
            yield SubmissionMustFail(Ask, dict(ask_price=cu(200)))
            yield Ask, dict(ask_price=cu(30))
        else:
            yield Bid, dict(bid_price=cu(60))

        yield Results

        if self.player.id_in_group == 1:
            expect(self.player.payoff, C.CASH_ENDOWMENT + cu(45))
        else:
            expect(self.player.payoff, C.CASH_ENDOWMENT + C.MUG_VALUE_TO_BUYER - cu(45))
