from otree.api import Bot
from otree.api import SubmissionMustFail
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction

        if C.INCLUDE_RISK:
            risk_data = {f'risk_choice_{i}': 'A' for i in range(1, C.NUM_RISK_ROWS + 1)}
            yield RiskChoices, risk_data

        if C.INCLUDE_TIME:
            time_data = {f'time_choice_{i}': 'A' for i in range(1, C.NUM_TIME_ROWS + 1)}
            yield TimeChoices, time_data

        if C.INCLUDE_LOSS:
            loss_data = {f'loss_choice_{i}': 'A' for i in range(1, C.NUM_LOSS_ROWS + 1)}
            yield SubmissionMustFail(LossChoices, dict(loss_choice_1='Z'))
            yield LossChoices, loss_data

        yield Results
