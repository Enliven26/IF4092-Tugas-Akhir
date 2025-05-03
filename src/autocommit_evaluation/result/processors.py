import re
import statistics
from abc import ABC, abstractmethod
from typing import Any

from autocommit_evaluation.result.models import (
    CommitMessageScore,
    GeneratorScore,
    ScoreSummary,
    TestCaseScore,
)


class BaseCleaner(ABC):
    @abstractmethod
    def _get_invalid_indices(
        self,
        evaluation_id: str,
        generator_score: GeneratorScore,
    ) -> set[int]:
        pass

    def clean(self, test_case_scores: list[TestCaseScore]) -> list[TestCaseScore]:
        cleaned_test_case_scores: list[TestCaseScore] = []
        total_individual_responses = 0
        total_invalid_individual_responses = 0

        for test_case_score in test_case_scores:
            invalid_indices = set()

            total_individual_responses += len(test_case_score.scores[0].scores)

            for generator_score in test_case_score.scores:
                invalid_indices = invalid_indices.union(
                    self._get_invalid_indices(
                        test_case_score.evaluation_id, generator_score
                    )
                )

            valid_test_case_score = self.__get_valid_test_case_score(
                test_case_score, invalid_indices
            )

            cleaned_test_case_scores.append(valid_test_case_score)
            total_invalid_individual_responses += len(invalid_indices)

        print(
            f"Total removed individual responses: {total_invalid_individual_responses}"
        )
        print(
            f"Percentage of removed individual responses: {total_invalid_individual_responses / total_individual_responses * 100:.2f}%"
        )
        print(
            f"Total remaining individual responses: {total_individual_responses - total_invalid_individual_responses}"
        )

        return cleaned_test_case_scores

    def __get_valid_test_case_score(
        self, test_case_score: TestCaseScore, invalid_indices: set[int]
    ) -> TestCaseScore:
        valid_test_case_score = TestCaseScore()
        valid_test_case_score.evaluation_id = test_case_score.evaluation_id
        valid_test_case_score.scores = []

        for generator_score in test_case_score.scores:
            valid_generator_score = GeneratorScore()
            valid_generator_score.generator_id = generator_score.generator_id
            valid_generator_score.scores = []

            for idx, commit_message_score in enumerate(generator_score.scores):
                if idx in invalid_indices:
                    continue

                valid_generator_score.scores.append(commit_message_score)

            valid_test_case_score.scores.append(valid_generator_score)

        return valid_test_case_score


class RuleBasedCleaner(BaseCleaner):
    def __init__(self, result_data: list[Any]):
        super().__init__()

        self.__result_data: list[Any] = result_data

    def _get_invalid_indices(
        self,
        evaluation_id: str,
        generator_score: GeneratorScore,
    ) -> set[int]:
        invalid_indices = set()

        for idx, commit_message_score in enumerate(generator_score.scores):
            is_valid = self.__is_valid_score(
                evaluation_id,
                generator_score.generator_id,
                commit_message_score,
            )

            if not is_valid:
                invalid_indices.add(idx)

        return invalid_indices

    def __is_rationality_score_valid(
        self, commit_message_score: CommitMessageScore, commit_message: str
    ) -> bool:
        jira_ticket_pattern = r"\b[A-Z]+-\d+\b"

        if (
            commit_message_score.rationality_score == 3
            and (re.search(jira_ticket_pattern, commit_message))
        ) or (
            commit_message_score.rationality_score == 4
            and (not re.search(jira_ticket_pattern, commit_message))
        ):
            return False

        return True

    def __is_conciseness_score_valid(
        self, commit_message_score: CommitMessageScore, commit_subject_length: int
    ) -> bool:
        if commit_message_score.conciseness_score != 1 and (
            commit_subject_length > 100
        ):
            return False

        return True

    def __is_correctness_score_valid(
        self,
        commit_message_score: CommitMessageScore,
        commit_message: str,
        jira_url: str,
    ) -> bool:

        ground_truth_ticket_id = jira_url.split("/")[-1]
        ticket_ids = re.findall(r"\b[A-Z]+-\d+\b", commit_message)

        if commit_message_score.correctness_score == 4 and (
            len(ticket_ids) > 1
            or (len(ticket_ids) == 1 and ticket_ids[0] != ground_truth_ticket_id)
        ):
            return False

        return True

    def __is_valid_score(
        self,
        evaluation_id: str,
        generator_id: str,
        commit_message_score: CommitMessageScore,
    ) -> bool:
        commit = next(
            (
                commit
                for commit in self.__result_data
                if commit["evaluation_id"] == evaluation_id
            ),
            None,
        )
        commit_message = next(
            (
                result
                for result in commit["generation_results"]
                if result["generator_id"] == generator_id
            ),
            None,
        )

        if commit_message is None:
            return True

        is_rationality_valid = self.__is_rationality_score_valid(
            commit_message_score,
            commit_message.get("cleaned_commit_message")
            or commit_message["commit_message"],
        )
        is_comprehensiveness_valid = True
        is_conciseness_valid = self.__is_conciseness_score_valid(
            commit_message_score, commit_message["commit_subject_length"]
        )
        is_correctness_valid = self.__is_correctness_score_valid(
            commit_message_score,
            commit_message.get("cleaned_commit_message")
            or commit_message["commit_message"],
            commit["jira_url"],
        )

        return (
            is_rationality_valid
            and is_comprehensiveness_valid
            and is_conciseness_valid
            and is_correctness_valid
        )

    def clean(self, test_case_scores):
        print("Cleaning scores based on rules...")
        result = super().clean(test_case_scores)
        print("Cleaning completed.")
        return result


class OutlierCleaner(BaseCleaner):
    def __init__(self, scale: float = 1.483, k: float = 3):
        super().__init__()

        self.__k = k
        self.__scale = scale

    def _get_invalid_indices(
        self,
        evaluation_id: str,
        generator_score: GeneratorScore,
    ) -> set[int]:
        invalid_indices = set()

        if len(generator_score.scores) >= 4:
            samples_collection = [[] for _ in range(4)]

            for commit_message_score in generator_score.scores:
                samples_collection[0].append(commit_message_score.rationality_score)
                samples_collection[1].append(
                    commit_message_score.comprehensiveness_score
                )
                samples_collection[2].append(commit_message_score.conciseness_score)
                samples_collection[3].append(commit_message_score.correctness_score)

            print(f"Generator ID: {generator_score.generator_id}")
            print(f"Evaluation ID: {evaluation_id}")
            print(f"Samples: {samples_collection}")

            for samples in samples_collection:
                new_outlier_indices = self.__get_outlier_indices(samples)
                print(f"Outlier indices: {new_outlier_indices}")
                invalid_indices = invalid_indices.union(new_outlier_indices)

        return invalid_indices

    def __get_outlier_indices(self, samples: list[int]) -> set[int]:
        median = statistics.median(samples)
        mad = statistics.median([abs(x - median) for x in samples])
        made = self.__scale * mad

        lower_bound = median - self.__k * made
        upper_bound = median + self.__k * made

        return {i for i, x in enumerate(samples) if x < lower_bound or x > upper_bound}

    def clean(self, test_case_scores):
        print("Cleaning outliers...")
        result = super().clean(test_case_scores)
        print("Outliers cleaned.")
        return result


class ResultSummarizer:
    def __init__(self, cleaners: list[BaseCleaner]):
        self.__cleaners = cleaners

    def summarize(
        self,
        test_case_scores: list[TestCaseScore],
    ) -> list[ScoreSummary]:
        for cleaner in self.__cleaners:
            test_case_scores = cleaner.clean(test_case_scores)

        score_summaries: list[ScoreSummary] = []

        for test_case_score in test_case_scores:
            for generator_score in test_case_score.scores:
                score_summary = next(
                    (
                        score
                        for score in score_summaries
                        if score.generator_id == generator_score.generator_id
                    ),
                    None,
                )

                if score_summary is None:
                    score_summary = ScoreSummary()
                    score_summary.generator_id = generator_score.generator_id
                    score_summaries.append(score_summary)

                for commit_message_score in generator_score.scores:
                    score_summary.rationality_score += (
                        commit_message_score.rationality_score
                    )
                    score_summary.comprehensiveness_score += (
                        commit_message_score.comprehensiveness_score
                    )
                    score_summary.conciseness_score += (
                        commit_message_score.conciseness_score
                    )
                    score_summary.correctness_score += (
                        commit_message_score.correctness_score
                    )

        for score_summary in score_summaries:
            score_count = sum(
                [
                    sum(
                        [
                            len(generator_score.scores)
                            for generator_score in test_case_score.scores
                            if generator_score.generator_id
                            == score_summary.generator_id
                        ]
                    )
                    for test_case_score in test_case_scores
                ]
            )

            score_summary.rationality_score /= score_count
            score_summary.comprehensiveness_score /= score_count
            score_summary.conciseness_score /= score_count
            score_summary.correctness_score /= score_count

        return score_summaries
