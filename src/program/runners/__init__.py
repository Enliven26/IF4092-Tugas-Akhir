from datapreparation import context_generator
from cmg import evaluator
from runners.contextgeneratorrunners import ContextGeneratorRunner
from runners.cmgrunners import CmgRunner

context_generator_runner = ContextGeneratorRunner(context_generator)
cmg_runner = CmgRunner(evaluator)
