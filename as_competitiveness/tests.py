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

    def _answers(self):
        tasks = json.loads(self.player.task_data)
        field_names = Task.get_form_fields(self.player)
        return {
            field_name: task['a'] + task['b']
            for field_name, task in zip(field_names, tasks)
        }

    def _apply_case_adjustments(self, answers):
        if self.case == 'tournament' and self.player.id_in_group != 1 and self.player.round_number > 1:
            first_field = next(iter(answers))
            answers[first_field] += 1
            return answers

        if self.case == 'configured_tournament':
            wrong_answers = 0
            if self.player.id_in_group == 3:
                wrong_answers = 1
            elif self.player.id_in_group == 4:
                wrong_answers = 2
            elif self.player.id_in_group > 4:
                wrong_answers = 0
            for field_name in list(answers.keys())[:wrong_answers]:
                answers[field_name] += 1
        return answers

    def _expected_round_payoff(self):
        if self.case == 'piece_rate':
            if self.round_number == 2:
                return cu(120) if self.player.id_in_group == 1 else cu(0)
            return cu(60)

        if self.case == 'tournament':
            if self.round_number == 1:
                return cu(60)
            return cu(120) if self.player.id_in_group == 1 else cu(0)

        if self.round_number == 1:
            if self.player.id_in_group in [1, 2] or self.player.id_in_group > 4:
                return cu(45)
            if self.player.id_in_group == 3:
                return cu(30)
            return cu(15)
        return cu(75) if self.player.id_in_group in [1, 2] else cu(0)

    def _expected_total_payoff(self):
        if self.case == 'piece_rate':
            return cu(240) if self.player.id_in_group == 1 else cu(120)
        if self.case == 'tournament':
            return cu(300) if self.player.id_in_group == 1 else cu(60)
        if self.player.id_in_group in [1, 2]:
            return cu(195)
        if self.player.id_in_group == 3:
            return cu(30)
        if self.player.id_in_group == 4:
            return cu(15)
        return cu(45)

    def _expected_winner_count(self):
        if self.round_number == 1:
            return 0
        if self.case == 'configured_tournament':
            return 2
        if self.case == 'piece_rate' and self.round_number == 3:
            return 0
        return 1

    def play_round(self):
        self._configure_non_default_case()
        originals = self._patch_non_default_helpers()

        if self.round_number == 1:
            yield Introduction
            if self.case == 'piece_rate':
                invalid = self._answers()
                invalid[next(iter(invalid))] = -1
                yield SubmissionMustFail(Task, invalid)

        if self.player.round_number == 3:
            yield SubmissionMustFail(Choice, dict(comp_choice='invalid'))
            yield Choice, dict(comp_choice='piece' if self.case == 'piece_rate' else 'tournament')

        if self.case == 'configured_tournament':
            assert len(Task.get_form_fields(self.player)) == 3
            assert Task.get_timeout_seconds(self.player) == 15

        answers = self._apply_case_adjustments(self._answers())
        yield Task, answers
        yield Results

        expect(self.player.group.effective_group_size, len(self.player.group.get_players()))
        expect(self.player.group.winner_count, self._expected_winner_count())
        expect(self.player.payoff, self._expected_round_payoff())
        if self.round_number == C.NUM_ROUNDS:
            expect(sum(player.payoff for player in self.player.in_all_rounds()), self._expected_total_payoff())

        self._restore_non_default_helpers(originals)
