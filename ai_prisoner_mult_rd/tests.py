from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    cases = ['mutual_cooperate', 'mutual_defect', 'alternating']

    def play_round(self):
        if self.round_number == 1:
            yield Introduction

        if self.case == 'mutual_cooperate' and self.round_number == 1:
            yield SubmissionMustFail(Decision, dict())

        if self.case == 'mutual_cooperate':
            cooperate = True
        elif self.case == 'mutual_defect':
            cooperate = False
        else:
            cooperate = (
                (self.player.id_in_group == 1 and self.round_number % 2 == 1)
                or (self.player.id_in_group == 2 and self.round_number % 2 == 0)
            )

        yield Decision, dict(cooperate=cooperate)

        if self.case == 'mutual_cooperate':
            expected_round = C.PAYOFF_B
        elif self.case == 'mutual_defect':
            expected_round = C.PAYOFF_C
        else:
            expected_round = C.PAYOFF_D if cooperate else C.PAYOFF_A

        expect(self.player.payoff, expected_round)

        if self.round_number == C.NUM_ROUNDS:
            total = sum(p.payoff for p in self.player.in_all_rounds())
            if self.case == 'mutual_cooperate':
                expect(total, C.NUM_ROUNDS * C.PAYOFF_B)
            elif self.case == 'mutual_defect':
                expect(total, C.NUM_ROUNDS * C.PAYOFF_C)
            else:
                expect(total, (C.NUM_ROUNDS // 2) * C.PAYOFF_A)

        yield Results
