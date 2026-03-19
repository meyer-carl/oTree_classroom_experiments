from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction
        yield ProxyBid, dict(proxy_bid=self.player.private_value)
        yield Results
