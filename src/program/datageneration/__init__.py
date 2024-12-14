from core import (
    code_parser,
    data_generation_chain,
    diff_parser,
    git,
    mock_data_generation_chain,
)
from datageneration.generators import DataGenerator

data_generator = DataGenerator(data_generation_chain, git, diff_parser, code_parser)

mock_data_generator = DataGenerator(
    mock_data_generation_chain, git, diff_parser, code_parser
)
