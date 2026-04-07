from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number > active_rounds(self.player):
            return

        if self.player.active_this_round is False:
            yield SitOutRound
            return

        if self.round_number == 1:
            yield Introduction

        if self.player.is_buyer:
            yield Order, dict(offer_price=self.player.private_value)
        else:
            yield Order, dict(offer_price=self.player.private_cost)

        yield Results
