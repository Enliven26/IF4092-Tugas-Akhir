import json
import os
from enum import Enum
from string import Template
from typing import Any

DEFAULT_LLM_MODEL = "gpt-4o-mini"
DEFAULT_EMBEDDINGS_MODEL = "text-embedding-3-small"

DEFAULT_CMG_TEMPERATURE = 0.7
DEFAULT_LLM_QUERY_TEXT_TEMPERATURE = 0.7
DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE = 0
DEFAULT_HIGH_LEVEL_CONTEXT_INDEX_NAME = "high_level_context_index"

END_DOCUMENT_SPLIT_SEPARATOR = "\n\n--- RETRIEVED DOCUMENT SPLIT END ---\n\n"


class _FewShotExampleModel:
    class __JsonKey(Enum):
        ID = "id"
        DIFF = "diff"
        SOURCE_CODE = "source_code"
        HIGH_LEVEL_CONTEXT = "high_level_context"
        COMMIT_TYPE = "commit_type"
        COMMIT_SUBJECT = "commit_subject"
        COMMIT_BODY = "commit_body"
        JIRA_TICKET_TYPE = "jira_ticket_type"

    def __init__(self):
        self.diff = ""
        self.source_code = ""
        self.high_level_context = ""
        self.commit_type = ""
        self.commit_subject = ""
        self.commit_body = ""

    def get_commit_message(self) -> str:
        return f"{self.commit_type}: {self.commit_subject}\n\n{self.commit_body}"

    @classmethod
    def from_json(cls, json_string: str) -> list["_FewShotExampleModel"]:
        try:
            data_list = json.loads(json_string)
            if not isinstance(data_list, list):
                raise ValueError("JSON data must be a list of objects.")

            data_list: list[dict[str, Any]] = data_list

            instances = []
            for data in data_list:
                instance = cls()
                instance.diff = data.get(cls.__JsonKey.DIFF.value, "")
                instance.source_code = data.get(cls.__JsonKey.SOURCE_CODE.value, "")
                instance.high_level_context = data.get(
                    cls.__JsonKey.HIGH_LEVEL_CONTEXT.value, []
                )
                instance.commit_type = data.get(cls.__JsonKey.COMMIT_TYPE.value, "")
                instance.commit_subject = data.get(
                    cls.__JsonKey.COMMIT_SUBJECT.value, ""
                )
                instance.commit_body = data.get(cls.__JsonKey.COMMIT_BODY.value, "")

                instances.append(instance)

            return instances

        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid JSON string for EvaluationModel list: {e}")


__EXAMPLE_PATH = os.path.join("data", "cmg", "examples.json")

__json_string = ""

try:
    with open(__EXAMPLE_PATH, "r") as f:
        __json_string = f.read()
except FileNotFoundError:
    __json_string = "[]"

__EXAMPLES = _FewShotExampleModel.from_json(__json_string)

for __example in __EXAMPLES:
    __example.diff = __example.diff.replace("{", "{{").replace("}", "}}")
    __example.source_code = __example.source_code.replace("{", "{{").replace("}", "}}")
    __example.high_level_context = __example.high_level_context.replace(
        "{", "{{"
    ).replace("}", "}}")
    __example.commit_type = __example.commit_type.replace("{", "{{").replace("}", "}}")
    __example.commit_subject = __example.commit_subject.replace("{", "{{").replace(
        "}", "}}"
    )
    __example.commit_body = __example.commit_body.replace("{", "{{").replace("}", "}}")

__ZERO_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_ORIGINAL_TEMPLATE = """Write a concise commit message based on the Git diff and relevant source code provided. The relevant source code should be used to provide additional context for the changes made in the Git diff.

A good commit message explains what changes were made and why they were necessary. Wrap the body at one to three brief sentences.

Follow this format for the commit message:

{{type}}: {{subject}}

{{body}}

Git diff:
{diff}

Relevant source code:
{source_code}

Commit type: {type}

Commit message:"""

__FEW_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_ORIGINAL_TEMPLATE = """Write a concise commit message based on the Git diff and relevant source code provided. The relevant source code should be used to provide additional context for the changes made in the Git diff.

A good commit message explains what changes were made and why they were necessary. Wrap the body at one to three brief sentences.

Follow this format for the commit message:

{{type}}: {{subject}}

{{body}}

Git diff 1:
$diff_1

Relevant source code 1:
$source_code_1

Commit Type 1: $commit_type_1

commit message 1: $commit_message_1

Git diff 2:
$diff_2

Relevant source code 2:
$source_code_2

Commit Type 2: $commit_type_2

Commit message 2: $commit_message_2

Git diff 3:
$diff_3

Relevant source code 3:
$source_code_3

Commit Type 3: $commit_type_3

Commit message 3: $commit_message_3

Git diff 4:
{diff}

Relevant source code 4:
{source_code}

Commit type 4: {type}

Commit message 4:"""

FEW_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = (
    Template(__FEW_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_ORIGINAL_TEMPLATE).substitute(
        {
            "diff_1": __EXAMPLES[0].diff,
            "diff_2": __EXAMPLES[1].diff,
            "diff_3": __EXAMPLES[2].diff,
            "source_code_1": __EXAMPLES[0].source_code,
            "source_code_2": __EXAMPLES[1].source_code,
            "source_code_3": __EXAMPLES[2].source_code,
            "commit_message_1": __EXAMPLES[0].get_commit_message(),
            "commit_message_2": __EXAMPLES[1].get_commit_message(),
            "commit_message_3": __EXAMPLES[2].get_commit_message(),
            "commit_type_1": __EXAMPLES[0].commit_type,
            "commit_type_2": __EXAMPLES[1].commit_type,
            "commit_type_3": __EXAMPLES[2].commit_type,
        }
    )
    if len(__EXAMPLES) >= 3
    else __ZERO_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_ORIGINAL_TEMPLATE
)

ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = """Write a concise commit message based on the Git diff and additional context provided. If the context is relevant, include it in the commit body. Use IDs, names, or titles to reference relevant contexts for brevity. Including multiple contexts is allowed.

A good commit message explains what changes were made and why they were necessary. Wrap the body at one to three brief sentences.

Follow this format for the commit message:

{{type}}: {{subject}}

{{body}}

Git diff:
{diff}

Additional context:
{context}

Commit type: {type}

Commit message: """

__FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_ORIGINAL_TEMPLATE = """Write a concise commit message based on the Git diff and additional context provided. If the context is relevant, include it in the commit body. Use IDs, names, or titles to reference relevant contexts for brevity. Including multiple contexts is allowed.

A good commit message explains what changes were made and why they were necessary. Wrap the body at one to three brief sentences.

Follow this format for the commit message:

{{type}}: {{subject}}

{{body}}

Git diff 1:
$diff_1

Additional context 1:
$context_1

Commit Type 1: $commit_type_1

commit message 1: $commit_message_1

Git diff 2:
$diff_2

Additional context 2:
$context_2

Commit Type 2: $commit_type_2

Commit message 2: $commit_message_2

Git diff 3:
$diff_3

Additional context 3:
$context_3

Commit Type 3: $commit_type_3

Commit message 3: $commit_message_3

Git diff 4:
{diff}

Additional context 4:
{context}

Commit type 4: {type}

Commit message 4:"""


FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = (
    Template(__FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_ORIGINAL_TEMPLATE).substitute(
        {
            "diff_1": __EXAMPLES[0].diff,
            "diff_2": __EXAMPLES[1].diff,
            "diff_3": __EXAMPLES[2].diff,
            "context_1": __EXAMPLES[0].high_level_context,
            "context_2": __EXAMPLES[1].high_level_context,
            "context_3": __EXAMPLES[2].high_level_context,
            "commit_message_1": __EXAMPLES[0].get_commit_message(),
            "commit_message_2": __EXAMPLES[1].get_commit_message(),
            "commit_message_3": __EXAMPLES[2].get_commit_message(),
            "commit_type_1": __EXAMPLES[0].commit_type,
            "commit_type_2": __EXAMPLES[1].commit_type,
            "commit_type_3": __EXAMPLES[2].commit_type,
        }
    )
    if len(__EXAMPLES) >= 3
    else ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE
)


DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE = """Given a Git diff and the relevant source code, write a concise summary of the code changes in a way that a non-technical person can understand. The query text must summarize the code changes in two very brief sentences.

Git diff:
{diff}

Source code:
{source_code}

Query text:"""

HIGH_LEVEL_CONTEXT_FILTER_PROMPT_TEMPLATE = """Evaluate the performance of a document retriever. Given the Git diff and retrieved context, return YES if the context directly or indirectly correlates with the changes in the Git diff. Otherwise, return NO.

> Git diff: 
>>>
{diff}
>>>
> Retrieved context:
>>>
{context}
>>>
> Relevant (YES / NO):"""

LOW_LEVEL_CONTEXT_DIFF_CLASSIFIER_PROMPT_TEMPLATE = """Classify the Git diff into one of the following six software maintenance activities: feat, fix, perf, test, refactor, or chore. Return the activity that best matches the code changes. Refer to the definitions below for each activity.

feat: introducing new features into the system.
fix: fixing existing bugs or issues in the system.
perf: improving the performance of the system.
test: adding, modifying, or deleting test cases.
refactor: changes made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior, including code styling.
chore: regular maintenance tasks, such as updating dependencies or build tasks.

Avoid adding any additional comments or annotations to the classification.

> Git diff: {diff}

> Software maintenance activity (feat / fix / perf / test / refactor / chore):
"""


HIGH_LEVEL_CONTEXT_DIFF_CLASSIFIER_PROMPT_TEMPLATE = """Classify the Git diff into one of the following six software maintenance activities: feat, fix, perf, test, refactor, or chore. Return the activity that best matches the code changes. If one or more contexts are relevant to the code changes, use them to help classify the Git diff.

Refer to the definitions below for each activity.

feat: introducing new features into the system.
fix: fixing existing bugs or issues in the system.
perf: improving the performance of the system.
test: adding, modifying, or deleting test cases.
refactor: changes made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior, including code styling.
chore: regular maintenance tasks, such as updating dependencies or build tasks.

Avoid adding any additional comments or annotations to the classification.

> Git diff: {diff}

> Additional context:
{context}

> Software maintenance activity (feat / fix / perf / test / refactor / chore):
"""
