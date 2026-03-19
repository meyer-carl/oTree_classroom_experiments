from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction
        yield Decision, dict(volunteer=True)
        yield Results
