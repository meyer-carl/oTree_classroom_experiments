from otree.api import Bot, SubmissionMustFail, expect
import json
from . import *


class PlayerBot(Bot):
    cases = ['piece_rate', 'tournament']

    def _answers(self, make_one_wrong=False):
        tasks = json.loads(self.player.task_data)
        answers = {
            f'answer_{i}': task['a'] + task['b']
            for i, task in enumerate(tasks, start=1)
        }
        if make_one_wrong:
            answers['answer_1'] += 1
        return answers

    def play_round(self):
        if self.case == 'piece_rate' and self.round_number == 1:
            yield Introduction
            invalid = self._answers()
            invalid['answer_1'] = -1
            yield SubmissionMustFail(Task, invalid)
        elif self.round_number == 1:
            yield Introduction

        if self.player.round_number == 3:
            yield SubmissionMustFail(Choice, dict(comp_choice='invalid'))
            yield Choice, dict(comp_choice='piece' if self.case == 'piece_rate' else 'tournament')

        answers = self._answers(
            make_one_wrong=self.case == 'tournament'
            and self.player.id_in_group != 1
            and self.player.round_number > 1
        )
        yield Task, answers

        if self.case == 'piece_rate':
            expected_round = cu(60 if self.round_number != 2 else 120)
            expect(self.player.group.winner_count, 4 if self.round_number == 2 else 0)
        else:
            expected_round = cu(60)
            if self.round_number > 1 and self.player.id_in_group == 1:
                expected_round = cu(120)
            elif self.round_number > 1:
                expected_round = cu(0)
            expect(self.player.group.winner_count, 0 if self.round_number == 1 else 1)

        expect(self.player.payoff, expected_round)
        if self.round_number == C.NUM_ROUNDS:
            total = sum(p.payoff for p in self.player.in_all_rounds())
            if self.case == 'piece_rate':
                expect(total, cu(240))
            else:
                expect(total, cu(300) if self.player.id_in_group == 1 else cu(60))
        yield Results
