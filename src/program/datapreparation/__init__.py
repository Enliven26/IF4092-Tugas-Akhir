from core import git
from core.parsers import code_parser, diff_parser
from datapreparation.generators import ExampleGenerator, JiraContextGenerator

context_generator = JiraContextGenerator(git)

example_generator = ExampleGenerator(git, diff_parser, code_parser)
