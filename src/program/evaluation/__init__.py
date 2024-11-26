from core import code_parser, diff_parser, git
from evaluation.evaluators import Evaluator

evaluator = Evaluator(git, code_parser, diff_parser)
