from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction

        if self.player.id_in_group == 1:
            yield SubmissionMustFail(OfferWage, dict(wage=cu(35)))
            yield OfferWage, dict(wage=cu(40))
        else:
            yield ChooseEffort, dict(effort=4)

        yield Results

        if self.player.id_in_group == 1:
            expect(self.player.payoff, C.BASE_PAYOFF + C.PRODUCTIVITY_PER_EFFORT * 4 - cu(40))
        else:
            expect(self.player.payoff, C.BASE_PAYOFF + cu(40) - C.EFFORT_COSTS[4])
