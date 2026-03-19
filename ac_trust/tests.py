from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction

        if self.player.id_in_group == 1:
            sent_amount = cu(10) if use_strategy_method(self.player) else cu(4)
            yield Send, dict(sent_amount=sent_amount)
        else:
            if use_strategy_method(self.player):
                data = {
                    f'strategy_send_back_{amount}': cu(0)
                    for amount in C.STRATEGY_SEND_AMOUNTS
                }
                yield StrategySendBack, data
            else:
                yield SendBack, dict(sent_back_amount=cu(8))

        yield Results
