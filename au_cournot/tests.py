from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction
        yield Decide, dict(units=1)
        yield Results
