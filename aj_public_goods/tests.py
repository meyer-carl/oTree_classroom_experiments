from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield Introduction
        yield Contribute, dict(contribution=cu(1))
        yield Results
