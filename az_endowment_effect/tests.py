from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number > active_rounds(self.player):
            return

        if self.player.active_this_round is False:
            yield SitOutRound
            expect(self.player.payoff, cu(0))
            return

        if self.round_number == 1:
            yield Introduction

        if seller_role(self.player) == C.SELLER_ROLE:
            yield SubmissionMustFail(Ask, dict(ask_price=cu(200)))
            yield Ask, dict(ask_price=cu(30))
        else:
            yield Bid, dict(bid_price=cu(60))

        yield Results

        if seller_role(self.player) == C.SELLER_ROLE:
            expect(self.player.raw_round_payoff, C.CASH_ENDOWMENT + cu(45))
        else:
            expect(self.player.raw_round_payoff, C.CASH_ENDOWMENT + C.MUG_VALUE_TO_BUYER - cu(45))
