from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction

        if self.player.id_in_group == 1:
            yield Offer, dict(offer=cu(50))
        else:
            if use_strategy_method(self.player):
                yield StrategyResponse, dict(min_accept=cu(40))
            else:
                yield Response, dict(accepted=True)

        yield Results
