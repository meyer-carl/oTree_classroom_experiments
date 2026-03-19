from otree.api import expect, Bot, cu
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Choice, dict(penny_side='Heads')

        paying_round = self.player.session.vars['paying_round']
        if self.round_number == paying_round:
            expect(self.player.payoff, C.STAKES)
        else:
            expect(self.player.payoff, cu(0))

        if self.player.round_number == C.NUM_ROUNDS:
            total = sum([p.payoff for p in self.player.in_all_rounds()])
            expect(total, C.STAKES)
