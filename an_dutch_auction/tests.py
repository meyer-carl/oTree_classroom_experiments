from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction
        yield StopPrice, dict(stop_price=self.player.private_value)
        yield Results
