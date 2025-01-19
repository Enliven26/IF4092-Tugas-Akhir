from core import git, jira
from core.parsers import code_parser, diff_parser
from datapreparation.generators import ExampleGenerator, JiraContextGenerator

context_generator = JiraContextGenerator(git, jira)

example_generator = ExampleGenerator(
    git, jira, diff_parser, code_parser
)
