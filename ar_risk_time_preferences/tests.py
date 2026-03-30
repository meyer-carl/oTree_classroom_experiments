from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    cases = ['default', 'ambiguity_paid']

    def play_round(self):
        yield Introduction

        if include_risk(self.player):
            risk_data = {f'risk_choice_{i}': 'A' for i in range(1, C.NUM_RISK_ROWS + 1)}
            yield RiskChoices, risk_data

        if include_time(self.player):
            time_data = {f'time_choice_{i}': 'A' for i in range(1, C.NUM_TIME_ROWS + 1)}
            yield TimeChoices, time_data

        if include_loss(self.player):
            loss_data = {f'loss_choice_{i}': 'A' for i in range(1, C.NUM_LOSS_ROWS + 1)}
            yield SubmissionMustFail(LossChoices, dict(loss_choice_1='Z'))
            yield LossChoices, loss_data

        if include_ambiguity(self.player):
            ambiguity_data = {f'ambiguity_choice_{i}': 'A' for i in range(1, C.NUM_AMBIGUITY_ROWS + 1)}
            yield SubmissionMustFail(AmbiguityChoices, dict(ambiguity_choice_1='Z'))
            if self.case == 'ambiguity_paid':
                self.player.session.vars['risk_time_forced_pay_task'] = 'ambiguity'
                self.player.session.vars['risk_time_forced_pay_row'] = 1
                ambiguity_data['ambiguity_choice_1'] = 'B'
            yield AmbiguityChoices, ambiguity_data

        yield Results

        if self.case == 'ambiguity_paid':
            if include_ambiguity(self.player):
                expect(self.player.pay_task, 'ambiguity')
                expect(self.player.pay_row, 1)
                assert self.player.ambiguity_realized_p_high in C.AMBIGUITY_PROB_MENU
            else:
                assert self.player.pay_task != 'ambiguity'
