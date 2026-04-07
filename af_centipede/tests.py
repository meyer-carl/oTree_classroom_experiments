from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    cases = ['direct_take', 'direct_pass', 'strategy_take', 'strategy_pass']

    def play_round(self):
        if self.round_number > active_rounds(self.player):
            return

        self.player.session.vars['centipede_force_strategy'] = (
            self.case.startswith('strategy') and not role_balanced_classroom(self.player)
        )

        if self.player.active_this_round is False:
            if role_balanced_classroom(self.player) and is_block_start_round(self.player):
                yield SitOutRound
            expect(self.player.payoff, cu(0))
            return

        if self.round_number == 1:
            yield Introduction

        if use_strategy_method(self.player):
            if StrategyDecision.is_displayed(self.player):
                fields = strategy_fields_for_player(self.player)
                data = {name: False for name in fields}
                if self.case == 'strategy_take' and fields:
                    data[fields[0]] = True
                yield StrategyDecision, data
        else:
            if Decision.is_displayed(self.player):
                yield SubmissionMustFail(Decision, dict())
                yield Decision, dict(take=self.case == 'direct_take')

        if Results.is_displayed(self.player):
            taking = use_strategy_method(self.player) and self.case == 'strategy_take'
            taking = taking or (not use_strategy_method(self.player) and self.case == 'direct_take')
            if taking:
                expected = cu(60) if self.player.id_in_group == 1 else cu(40)
            else:
                expected = cu(175)
            expect(self.player.raw_round_payoff, expected)
            yield Results
