from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number > pair_cycle_rounds(self.player):
            return

        if self.player.active_this_round is False:
            yield SitOutRound
            return

        if self.round_number == 1:
            yield Introduction
        yield Decide, dict(units=1)
        yield Results
