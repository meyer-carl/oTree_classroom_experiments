from types import SimpleNamespace

from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    cases = ['direct_accept', 'strategy_accept']

    def play_round(self):
        if self.round_number > active_rounds(self.player):
            return

        self.player.session.vars['ultimatum_force_strategy'] = (
            self.case.startswith('strategy') and not role_balanced_classroom(self.player)
        )

        if self.player.active_this_round is False:
            yield SitOutRound
            expect(self.player.payoff, cu(0))
            return

        if self.round_number == 1:
            yield Introduction

        accepted = True

        if role_name(self.player) == C.PROPOSER_ROLE:
            yield SubmissionMustFail(Offer, dict(offer=C.ENDOWMENT + cu(1)))
            yield Offer, dict(offer=cu(50))
        else:
            if use_strategy_method(self.player):
                yield SubmissionMustFail(
                    StrategyResponse,
                    dict(min_accept=C.ENDOWMENT + cu(1)),
                )
                yield StrategyResponse, dict(min_accept=cu(40))
            else:
                yield SubmissionMustFail(Response, dict())
                yield Response, dict(accepted=accepted)

        expect(self.player.group.accepted, accepted)
        expect(self.player.raw_round_payoff, cu(50))
        yield Results

        if role_balanced_classroom(self.player) and self.round_number == active_rounds(self.player):
            roles = {
                round_player.assigned_role
                for round_player in self.player.in_all_rounds()
                if round_player.active_this_round
            }
            expect(C.PROPOSER_ROLE in roles, True)
            expect(C.RESPONDER_ROLE in roles, True)


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
