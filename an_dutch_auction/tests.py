from otree.api import Bot, expect
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction
        yield StopPrice, dict(stop_price=self.player.private_value)
        yield Results
        expect(self.player.group.actual_bidder_count, len(self.player.group.get_players()))
