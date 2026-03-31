from otree.api import Bot, SubmissionMustFail, expect
import json
import sys
from . import *

APP = sys.modules[__package__]


class PlayerBot(Bot):
    cases = ['piece_rate', 'tournament', 'configured_tournament']

    def _configure_non_default_case(self):
        if self.case != 'configured_tournament':
            return
        self.player.task_data = json.dumps(
            [
                {'a': 10, 'b': 10},
                {'a': 20, 'b': 20},
                {'a': 30, 'b': 30},
            ]
        )

    def _patch_non_default_helpers(self):
        if self.case != 'configured_tournament':
            return None
        originals = (
            APP.competitiveness_num_tasks,
            APP.competitiveness_time_limit,
            APP.competitiveness_piece_rate,
            APP.competitiveness_tournament_rate,
            APP.competitiveness_tournament_winners,
        )
        APP.competitiveness_num_tasks = lambda context: 3
        APP.competitiveness_time_limit = lambda context: 15
        APP.competitiveness_piece_rate = lambda context: cu(15)
        APP.competitiveness_tournament_rate = lambda context: cu(25)
        APP.competitiveness_tournament_winners = lambda context: 2
        return originals

    def _restore_non_default_helpers(self, originals):
        if not originals:
            return
        (
            APP.competitiveness_num_tasks,
            APP.competitiveness_time_limit,
            APP.competitiveness_piece_rate,
            APP.competitiveness_tournament_rate,
            APP.competitiveness_tournament_winners,
        ) = originals

    def _answers(self, make_one_wrong=False):
        tasks = json.loads(self.player.task_data)
        field_names = Task.get_form_fields(self.player)
        answers = {
            field_name: task['a'] + task['b']
            for field_name, task in zip(field_names, tasks)
        }
        if make_one_wrong:
            answers[field_names[0]] += 1
        return answers

    def play_round(self):
        self._configure_non_default_case()
        originals = self._patch_non_default_helpers()

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

        if self.case == 'configured_tournament':
            assert len(Task.get_form_fields(self.player)) == 3
            assert Task.get_timeout_seconds(self.player) == 15

        answers = self._answers(
            make_one_wrong=self.case == 'tournament'
            and self.player.id_in_group != 1
            and self.player.round_number > 1
        )
        if self.case == 'configured_tournament':
            wrong_answers = 0
            if self.player.id_in_group == 3:
                wrong_answers = 1
            elif self.player.id_in_group == 4:
                wrong_answers = 2
            for i in range(1, wrong_answers + 1):
                answers[f'answer_{i}'] += 1
        yield Task, answers

        if self.case == 'configured_tournament':
            set_round_results(self.player.group)

        if self.case == 'piece_rate':
            expected_round = cu(60)
            if self.round_number == 2 and self.player.id_in_group == 1:
                expected_round = cu(120)
            elif self.round_number == 2:
                expected_round = cu(0)
            expect(self.player.group.winner_count, 1 if self.round_number == 2 else 0)
        elif self.case == 'configured_tournament':
            if self.round_number == 1:
                expected_round = {1: cu(45), 2: cu(45), 3: cu(30), 4: cu(15)}[self.player.id_in_group]
                expect(self.player.group.winner_count, 0)
            else:
                expected_round = cu(75) if self.player.id_in_group in [1, 2] else cu(0)
                expect(self.player.group.winner_count, 2)
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
                expect(total, cu(240) if self.player.id_in_group == 1 else cu(120))
            elif self.case == 'configured_tournament':
                expect(total, {1: cu(195), 2: cu(195), 3: cu(30), 4: cu(15)}[self.player.id_in_group])
            else:
                expect(total, cu(300) if self.player.id_in_group == 1 else cu(60))
        yield Results
        self._restore_non_default_helpers(originals)
