from core import code_parser, diff_parser, git, mock_data_generation_chain
from datageneration.generators import DataGenerator

mock_data_generator = DataGenerator(
    mock_data_generation_chain, git, diff_parser, code_parser
)
