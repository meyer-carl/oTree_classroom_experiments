from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    cases = ['direct_return', 'strategy_return']

    def play_round(self):
        self.player.session.config['use_strategy_method'] = self.case == 'strategy_return'

        yield Introduction

        if self.player.id_in_group == 1:
            if use_strategy_method(self.player):
                yield SubmissionMustFail(Send, dict(sent_amount=cu(5)))
                sent_amount = cu(10)
            else:
                yield SubmissionMustFail(Send, dict(sent_amount=C.ENDOWMENT + cu(1)))
                sent_amount = cu(40)
            yield Send, dict(sent_amount=sent_amount)
        else:
            if use_strategy_method(self.player):
                invalid = {name: cu(0) for name in strategy_fields()}
                invalid['strategy_send_back_10'] = C.ENDOWMENT + cu(1)
                yield SubmissionMustFail(StrategySendBack, invalid)
                data = {
                    name: cu(0) for name in strategy_fields()
                }
                data['strategy_send_back_10'] = cu(4)
                yield StrategySendBack, data
            else:
                yield SubmissionMustFail(SendBack, dict(sent_back_amount=cu(-1)))
                yield SendBack, dict(sent_back_amount=cu(20))

        if self.case == 'direct_return':
            expected = cu(80) if self.player.id_in_group == 1 else cu(100)
        else:
            expected = cu(94) if self.player.id_in_group == 1 else cu(26)

        expect(self.player.payoff, expected)
        yield Results
