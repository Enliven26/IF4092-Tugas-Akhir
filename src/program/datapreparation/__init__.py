from core import git, high_level_context_chain, jira
from core.parsers import code_parser, diff_parser
from datapreparation.generators import ExampleGenerator, JiraContextGenerator

context_generator = JiraContextGenerator(git, jira)

example_generator = ExampleGenerator(
    high_level_context_chain, git, diff_parser, code_parser
)
