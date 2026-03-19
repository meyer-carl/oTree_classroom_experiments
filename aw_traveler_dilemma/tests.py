from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction
        yield Claim, dict(claim=C.MIN_AMOUNT)
        yield Results
