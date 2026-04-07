from otree.api import Bot, expect
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction
        yield Bid, dict(bid_amount=cu(1))
        yield Results
        expect(self.player.group.actual_bidder_count, len(self.player.group.get_players()))
