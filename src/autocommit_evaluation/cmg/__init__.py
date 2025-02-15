from autocommit.core import git
from autocommit.core.parsers import diff_parser
from autocommit.core.parsers.language import java_code_parser
from autocommit_evaluation.cmg.evaluators import Evaluator

evaluator = Evaluator(git, diff_parser, java_code_parser)
