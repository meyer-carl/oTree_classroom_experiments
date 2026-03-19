from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield Introduction

        if use_strategy_method(self.player):
            if self.round_number == 1:
                data = {
                    f'strategy_take_{r}': False
                    for r in range(1, C.NUM_ROUNDS + 1)
                    if (r % 2 == 1 and self.player.id_in_group == 1)
                    or (r % 2 == 0 and self.player.id_in_group == 2)
                }
                yield StrategyDecision, data
        else:
            is_my_turn = (self.player.id_in_group == 1 and self.round_number % 2 == 1) or (
                self.player.id_in_group == 2 and self.round_number % 2 == 0
            )
            if is_my_turn:
                yield Decision, dict(take=False)

        if Results.is_displayed(self.player):
            yield Results
