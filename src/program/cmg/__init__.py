from cmg.evaluators import Evaluator
from core import git
from core.parsers import diff_parser, code_parser

evaluator = Evaluator(git, diff_parser, code_parser)
