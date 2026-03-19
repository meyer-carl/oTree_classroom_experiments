from otree.api import expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield Introduction
        yield Decision, dict(cooperate=True)
        expect('You chose to', 'in', self.html)
        expect(self.player.payoff, C.PAYOFF_B)
        yield Results
