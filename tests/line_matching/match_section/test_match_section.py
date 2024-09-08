from pathlib import Path

import pytest

from src.simple_config_parser.simple_config_parser import SimpleConfigParser

BASE_DIR = Path(__file__).parent.joinpath("test_data")
MATCHING_TEST_DATA_PATH = BASE_DIR.joinpath("matching_data.txt")
NON_MATCHING_TEST_DATA_PATH = BASE_DIR.joinpath("non_matching_data.txt")


@pytest.fixture
def parser():
    return SimpleConfigParser()


def load_testdata_from_file(file_path: Path):
    """Helper function to load test data from a text file"""

    with open(file_path, "r") as f:
        return [line.replace("\n", "") for line in f]


@pytest.mark.parametrize("line", load_testdata_from_file(MATCHING_TEST_DATA_PATH))
def test_match_section(parser, line):
    """Test that a line matches the definition of a section"""
    assert (
        parser._match_section(line) is True
    ), f"Expected line '{line}' to match section definition!"


@pytest.mark.parametrize("line", load_testdata_from_file(NON_MATCHING_TEST_DATA_PATH))
def test_non_matching_section(parser, line):
    """Test that a line does not match the definition of a section"""
    assert (
        parser._match_section(line) is False
    ), f"Expected line '{line}' to not match section definition!"
