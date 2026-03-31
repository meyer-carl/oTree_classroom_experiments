from types import SimpleNamespace

from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    cases = ['direct_return', 'strategy_return']

    def play_round(self):
        self.player.session.vars['trust_force_strategy'] = self.case == 'strategy_return'

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
                invalid = {name: cu(0) for name in strategy_fields(self.player)}
                invalid['strategy_send_back_10'] = C.ENDOWMENT + cu(1)
                yield SubmissionMustFail(StrategySendBack, invalid)
                data = {
                    name: cu(0) for name in strategy_fields(self.player)
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


class DummyGroup:
    def __init__(self, *, players, session, sent_amount=None, sent_back_amount=None):
        self._players = players
        self.session = session
        self.sent_amount = sent_amount
        self.sent_back_amount = sent_back_amount

    def get_players(self):
        return self._players


class DummySubsession:
    def __init__(self, players):
        self._players = players

    def get_players(self):
        return self._players


def test_set_payoffs_handles_unmatched_second_mover():
    session = SimpleNamespace(config={}, vars={'trust_force_strategy': True})
    first_mover = SimpleNamespace(
        id_in_group=1,
        group=None,
        session=session,
        subsession=None,
        payoff=None,
    )
    second_mover = SimpleNamespace(
        id_in_group=2,
        group=None,
        session=session,
        subsession=None,
        payoff=None,
        strategy_send_back_40=cu(25),
    )
    first_mover.group = DummyGroup(players=[first_mover], session=session, sent_amount=cu(40))
    second_mover.group = DummyGroup(players=[second_mover], session=session)
    subsession = DummySubsession([first_mover, second_mover])
    first_mover.subsession = subsession
    second_mover.subsession = subsession

    set_payoffs(second_mover.group)

    assert second_mover.group.sent_amount == cu(40)
    assert second_mover.group.sent_back_amount == cu(25)
    assert second_mover.payoff == cu(95)
