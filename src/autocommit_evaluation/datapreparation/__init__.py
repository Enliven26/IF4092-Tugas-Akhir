from autocommit.core import git
from autocommit.core.parsers import diff_parser
from autocommit.core.parsers.language import java_code_parser
from autocommit_evaluation.core import jira
from autocommit_evaluation.datapreparation.generators import (
    ExampleGenerator,
    JiraContextGenerator,
)

context_generator = JiraContextGenerator(git, jira)

example_generator = ExampleGenerator(git, jira, diff_parser, java_code_parser)
