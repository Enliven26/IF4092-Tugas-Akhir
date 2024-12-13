import os

from core import code_parser, diff_parser, git
from evaluation.evaluators import Evaluator

evaluator = Evaluator(git, diff_parser, code_parser)
