from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    cases = ['direct_accept', 'direct_reject', 'strategy_accept', 'strategy_reject']

    def play_round(self):
        self.player.session.config['use_strategy_method'] = self.case.startswith('strategy')

        yield Introduction

        accepted = self.case.endswith('accept')
        expected_payoff = cu(50) if accepted else cu(0)

        if self.player.id_in_group == 1:
            yield SubmissionMustFail(Offer, dict(offer=C.ENDOWMENT + cu(1)))
            yield Offer, dict(offer=cu(50))
        else:
            if use_strategy_method(self.player):
                yield SubmissionMustFail(
                    StrategyResponse,
                    dict(min_accept=C.ENDOWMENT + cu(1)),
                )
                min_accept = cu(40) if accepted else cu(60)
                yield StrategyResponse, dict(min_accept=min_accept)
            else:
                yield SubmissionMustFail(Response, dict(accepted='invalid'))
                yield Response, dict(accepted=accepted)

        expect(self.player.group.accepted, accepted)
        expect(self.player.payoff, expected_payoff)
        yield Results
