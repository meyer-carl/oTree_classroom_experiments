from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction
        yield Bid, dict(bid_amount=cu(1))
        yield Results
