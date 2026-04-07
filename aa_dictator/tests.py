from otree.api import Currency as c, currency_range, expect, Bot
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

        if role_name(self.player) == C.DICTATOR_ROLE:
            yield Offer, dict(kept=cu(99))
            expect(self.player.raw_round_payoff, cu(99))
        else:
            expect(self.player.raw_round_payoff, cu(1))
        yield Results
