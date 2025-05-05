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
    def _process_invalid_scores(
        self,
        evaluation_id: str,
        generator_score: GeneratorScore,
    ) -> set[int]:
        pass

    def clean(
        self, test_case_scores: list[TestCaseScore], partial_cleaning: bool = False
    ) -> list[TestCaseScore]:
        cleaned_test_case_scores: list[TestCaseScore] = []
        total_individual_responses = 0
        total_invalid_individual_responses = 0

        for test_case_score in test_case_scores:
            invalid_indices = set()

            total_individual_responses += len(test_case_score.scores[0].scores)

            for generator_score in test_case_score.scores:
                invalid_indices = invalid_indices.union(
                    self._process_invalid_scores(
                        test_case_score.evaluation_id, generator_score
                    )
                )

            if not partial_cleaning:
                valid_test_case_score = self.__get_valid_test_case_score(
                    test_case_score, invalid_indices
                )

                cleaned_test_case_scores.append(valid_test_case_score)

            total_invalid_individual_responses += len(invalid_indices)

        print(
            f"Total cleaned individual responses: {total_invalid_individual_responses}"
        )
        print(
            f"Percentage of cleaned individual responses: {total_invalid_individual_responses / total_individual_responses * 100:.2f}%"
        )
        print(
            f"Total remaining individual responses: {total_individual_responses - total_invalid_individual_responses}"
        )

        return cleaned_test_case_scores if not partial_cleaning else test_case_scores

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

    def _process_invalid_scores(
        self,
        evaluation_id: str,
        generator_score: GeneratorScore,
    ) -> set[int]:
        invalid_indices = set()

        for idx, commit_message_score in enumerate(generator_score.scores):
            is_valid = self.__process_invalid_score(
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
            commit_message_score.rationality_score is not None
            and (
                commit_message_score.rationality_score == 3
                and (re.search(jira_ticket_pattern, commit_message))
            )
            or (
                commit_message_score.rationality_score == 4
                and (not re.search(jira_ticket_pattern, commit_message))
            )
        ):
            return False

        return True

    def __is_conciseness_score_valid(
        self, commit_message_score: CommitMessageScore, commit_subject_length: int
    ) -> bool:
        if commit_message_score.conciseness_score is not None and (
            commit_message_score.conciseness_score != 1
            and (commit_subject_length > 100)
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

        if commit_message_score.correctness_score is not None and (
            commit_message_score.correctness_score == 4
            and (
                len(ticket_ids) > 1
                or (len(ticket_ids) == 1 and ticket_ids[0] != ground_truth_ticket_id)
            )
        ):
            return False

        return True

    def __process_invalid_score(
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

        if not is_rationality_valid:
            commit_message_score.rationality_score = None

        if not is_comprehensiveness_valid:
            commit_message_score.comprehensiveness_score = None

        if not is_conciseness_valid:
            commit_message_score.conciseness_score = None

        if not is_correctness_valid:
            commit_message_score.correctness_score = None

        return (
            is_rationality_valid
            and is_comprehensiveness_valid
            and is_conciseness_valid
            and is_correctness_valid
        )

    def clean(
        self, test_case_scores, partial_cleaning: bool = False
    ) -> list[TestCaseScore]:
        print("Cleaning scores based on rules...")
        result = super().clean(test_case_scores, partial_cleaning)
        print("Cleaning completed.")
        return result


class OutlierCleaner(BaseCleaner):
    def __init__(self, scale: float = 1.483, k: float = 3, min_sample_size: int = 4):
        super().__init__()

        self.__k = k
        self.__scale = scale
        self.__min_sample_size = min_sample_size

    def _process_invalid_scores(
        self,
        evaluation_id: str,
        generator_score: GeneratorScore,
    ) -> set[int]:
        invalid_indices = set()

        if len(generator_score.scores) >= self.__min_sample_size:
            samples_collection: list[list[int]] = [[] for _ in range(4)]
            samples_indices: list[list[int]] = [[] for _ in range(4)]

            for idx, commit_message_score in enumerate(generator_score.scores):
                self.__fill_samples(
                    commit_message_score, samples_collection, samples_indices, idx
                )

            print(f"Evaluation ID: {evaluation_id}")
            print(f"Generator ID: {generator_score.generator_id}")
            print(f"Samples: {samples_collection}")
            print(f"Samples Indices: {samples_indices}")

            for sample_idx, samples in enumerate(samples_collection):
                if len(samples) < self.__min_sample_size:
                    continue

                new_outlier_sample_indices = self.__get_outlier_indices(samples)
                new_outlier_indices = [
                    samples_indices[sample_idx][idx]
                    for idx in new_outlier_sample_indices
                ]

                print(f"Outlier indices: {new_outlier_indices}")

                self.__remove_outlier_scores(
                    generator_score, new_outlier_indices, sample_idx
                )

                invalid_indices = invalid_indices.union(new_outlier_indices)

        return invalid_indices

    def __remove_outlier_scores(
        self,
        generator_score: GeneratorScore,
        new_outlier_indices: list[int],
        sample_idx: int,
    ):
        for idx in new_outlier_indices:
            commit_message_score = generator_score.scores[idx]

            if sample_idx == 0:
                commit_message_score.rationality_score = None

            elif sample_idx == 1:
                commit_message_score.comprehensiveness_score = None

            elif sample_idx == 2:
                commit_message_score.conciseness_score = None

            elif sample_idx == 3:
                commit_message_score.correctness_score = None

    def __fill_samples(
        self,
        commit_message_score: CommitMessageScore,
        samples_collection: list[list[int]],
        samples_indices: list[list[int]],
        idx: int,
    ):
        if commit_message_score.rationality_score is not None:
            samples_collection[0].append(commit_message_score.rationality_score)
            samples_indices[0].append(idx)

        if commit_message_score.comprehensiveness_score is not None:
            samples_collection[1].append(commit_message_score.comprehensiveness_score)
            samples_indices[1].append(idx)

        if commit_message_score.conciseness_score is not None:
            samples_collection[2].append(commit_message_score.conciseness_score)
            samples_indices[2].append(idx)

        if commit_message_score.correctness_score is not None:
            samples_collection[3].append(commit_message_score.correctness_score)
            samples_indices[3].append(idx)

    def __get_outlier_indices(self, samples: list[int]) -> set[int]:
        median = statistics.median(samples)
        mad = statistics.median([abs(x - median) for x in samples])
        made = self.__scale * mad

        lower_bound = median - self.__k * made
        upper_bound = median + self.__k * made

        return {i for i, x in enumerate(samples) if x < lower_bound or x > upper_bound}

    def clean(
        self, test_case_scores, partial_cleaning: bool = False
    ) -> list[TestCaseScore]:
        print("Cleaning outliers...")
        result = super().clean(test_case_scores, partial_cleaning)
        print("Outliers cleaned.")
        return result


class ResultSummarizer:
    def __init__(self, cleaners: list[BaseCleaner]):
        self.__cleaners = cleaners

    def summarize(
        self,
        test_case_scores: list[TestCaseScore],
        partial_cleaning: bool = False,
    ) -> list[ScoreSummary]:
        for cleaner in self.__cleaners:
            test_case_scores = cleaner.clean(test_case_scores, partial_cleaning)

        score_summaries: list[ScoreSummary] = []
        score_count_map: dict[tuple[str, int], int] = {}

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

                    for i in range(4):
                        score_count_map[(generator_score.generator_id, i)] = 0

                for commit_message_score in generator_score.scores:
                    self.__add_score(
                        score_summary, commit_message_score, score_count_map
                    )

        for score_summary in score_summaries:
            self.__calculate_average(score_summary, score_count_map)

        return score_summaries

    def __add_score(
        self,
        score_summary: ScoreSummary,
        commit_message_score: CommitMessageScore,
        score_count_map: dict[tuple[str, int], int],
    ) -> None:
        if commit_message_score.rationality_score is not None:
            score_summary.rationality_score += commit_message_score.rationality_score
            score_count_map[(score_summary.generator_id, 0)] += 1

        if commit_message_score.comprehensiveness_score is not None:
            score_summary.comprehensiveness_score += (
                commit_message_score.comprehensiveness_score
            )
            score_count_map[(score_summary.generator_id, 1)] += 1

        if commit_message_score.conciseness_score is not None:
            score_summary.conciseness_score += commit_message_score.conciseness_score
            score_count_map[(score_summary.generator_id, 2)] += 1

        if commit_message_score.correctness_score is not None:
            score_summary.correctness_score += commit_message_score.correctness_score
            score_count_map[(score_summary.generator_id, 3)] += 1

    def __calculate_average(
        self,
        score_summary: ScoreSummary,
        score_count_map: dict[tuple[str, int], int],
    ) -> None:
        if score_count_map[(score_summary.generator_id, 0)] > 0:
            score_summary.rationality_score /= score_count_map[
                (score_summary.generator_id, 0)
            ]

            print(f"Rationality score count: {score_count_map[(score_summary.generator_id, 0)]}")

        if score_count_map[(score_summary.generator_id, 1)] > 0:
            score_summary.comprehensiveness_score /= score_count_map[
                (score_summary.generator_id, 1)
            ]

            print(f"Comprehensiveness score count: {score_count_map[(score_summary.generator_id, 1)]}")

        if score_count_map[(score_summary.generator_id, 2)] > 0:
            score_summary.conciseness_score /= score_count_map[
                (score_summary.generator_id, 2)
            ]

            print(f"Conciseness score count: {score_count_map[(score_summary.generator_id, 2)]}")

        if score_count_map[(score_summary.generator_id, 3)] > 0:
            score_summary.correctness_score /= score_count_map[
                (score_summary.generator_id, 3)
            ]

            print(f"Correctness score count: {score_count_map[(score_summary.generator_id, 3)]}")
