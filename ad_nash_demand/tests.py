from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):

    cases = [
        'success',  # players agree on an amount under the threshold
        'greedy',  # players ask for too much so end up with nothing
    ]

    def play_round(self):
        if self.round_number > pair_cycle_rounds(self.player):
            return

        if self.player.active_this_round is False:
            yield SitOutRound
            expect(self.player.payoff, cu(0))
            return

        # start
        if self.round_number == 1:
            yield Introduction

        if self.case == 'success':
            request = cu(10)
            yield Request, dict(request=request)
            yield Results
            expect(self.player.raw_round_payoff, request)

        if self.case == 'greedy':
            yield Request, dict(request=C.AMOUNT_SHARED)
            yield Results
            expect(self.player.raw_round_payoff, cu(0))
