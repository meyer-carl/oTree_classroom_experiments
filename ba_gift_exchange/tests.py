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

        if role_name(self.player) == C.EMPLOYER_ROLE:
            yield SubmissionMustFail(OfferWage, dict(wage=cu(35)))
            yield OfferWage, dict(wage=cu(40))
        else:
            yield ChooseEffort, dict(effort=4)

        yield Results

        if role_name(self.player) == C.EMPLOYER_ROLE:
            expect(self.player.raw_round_payoff, C.BASE_PAYOFF + C.PRODUCTIVITY_PER_EFFORT * 4 - cu(40))
        else:
            expect(self.player.raw_round_payoff, C.BASE_PAYOFF + cu(40) - C.EFFORT_COSTS[4])
