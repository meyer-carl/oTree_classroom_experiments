from otree.api import expect, Bot, cu
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number > active_rounds(self.player):
            return

        if self.player.active_this_round is False:
            yield SitOutRound
            expect(self.player.payoff, cu(0))
            return

        yield Choice, dict(penny_side='Heads')

        if pair_cycle_enabled(self.player):
            expect(self.player.raw_round_payoff, C.STAKES)
        else:
            paying_round = self.player.session.vars['paying_round']
            if self.round_number == paying_round:
                expect(self.player.payoff, C.STAKES)
            else:
                expect(self.player.payoff, cu(0))

        if self.player.round_number == active_rounds(self.player):
            total = sum([p.payoff for p in self.player.in_all_rounds()])
            if pair_cycle_enabled(self.player):
                expect(total >= cu(0), True)
            else:
                expect(total, C.STAKES)
