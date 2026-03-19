from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    cases = ['direct_take', 'direct_pass', 'strategy_take', 'strategy_pass']

    def play_round(self):
        self.player.session.vars['centipede_force_strategy'] = self.case.startswith('strategy')

        if self.round_number == 1:
            yield Introduction

        if use_strategy_method(self.player):
            if StrategyDecision.is_displayed(self.player):
                fields = strategy_fields_for_player(self.player)
                data = {name: False for name in fields}
                if self.case == 'strategy_take' and self.player.id_in_group == 1:
                    data[fields[0]] = True
                yield StrategyDecision, data
        else:
            if Decision.is_displayed(self.player):
                yield SubmissionMustFail(Decision, dict())
                yield Decision, dict(take=self.case == 'direct_take')

        if Results.is_displayed(self.player):
            if self.case in ['direct_take', 'strategy_take']:
                expected = cu(60) if self.player.id_in_group == 1 else cu(40)
            else:
                expected = cu(175)
            expect(self.player.payoff, expected)
            yield Results
