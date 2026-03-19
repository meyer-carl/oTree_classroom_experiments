from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction

        if self.player.is_buyer:
            yield Order, dict(offer_price=self.player.private_value)
        else:
            yield Order, dict(offer_price=self.player.private_cost)

        yield Results
