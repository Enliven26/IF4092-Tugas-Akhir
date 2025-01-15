from core import data_generation_chain, git
from core.parsers import code_parser, diff_parser
from datageneration.generators import DataGenerator

data_generator = DataGenerator(data_generation_chain, git, diff_parser, code_parser)
