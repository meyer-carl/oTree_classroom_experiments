from types import SimpleNamespace

from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    cases = ['direct_accept', 'direct_reject', 'strategy_accept', 'strategy_reject']

    def play_round(self):
        self.player.session.vars['ultimatum_force_strategy'] = self.case.startswith('strategy')

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
                yield SubmissionMustFail(Response, dict())
                yield Response, dict(accepted=accepted)

        expect(self.player.group.accepted, accepted)
        expect(self.player.payoff, expected_payoff)
        yield Results


class DummyGroup:
    def __init__(self, *, players, session, offer=None, accepted=None):
        self._players = players
        self.session = session
        self.offer = offer
        self.accepted = accepted

    def get_players(self):
        return self._players


class DummySubsession:
    def __init__(self, players):
        self._players = players

    def get_players(self):
        return self._players


def test_set_payoffs_handles_unmatched_responder():
    session = SimpleNamespace(config={}, vars={'ultimatum_force_strategy': True})
    proposer = SimpleNamespace(
        id_in_group=1,
        group=None,
        session=session,
        subsession=None,
        payoff=None,
        min_accept=None,
    )
    responder = SimpleNamespace(
        id_in_group=2,
        group=None,
        session=session,
        subsession=None,
        payoff=None,
        min_accept=cu(40),
    )
    proposer.group = DummyGroup(players=[proposer], session=session, offer=cu(50))
    responder.group = DummyGroup(players=[responder], session=session)
    subsession = DummySubsession([proposer, responder])
    proposer.subsession = subsession
    responder.subsession = subsession

    set_payoffs(responder.group)

    assert responder.group.offer == cu(50)
    assert responder.group.accepted is True
    assert responder.payoff == cu(50)
