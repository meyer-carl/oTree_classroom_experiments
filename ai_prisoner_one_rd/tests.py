from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number > pair_cycle_rounds(self.player):
            return

        if self.player.active_this_round is False:
            yield SitOutRound
            expect(self.player.payoff, cu(0))
            return

        if self.round_number == 1:
            yield Introduction
        yield Decision, dict(cooperate=True)
        expect('Both of you chose to Cooperate', 'in', self.html)
        expect(self.player.raw_round_payoff, C.PAYOFF_B)
        yield Results
