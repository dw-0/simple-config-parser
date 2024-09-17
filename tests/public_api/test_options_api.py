# ======================================================================= #
#  Copyright (C) 2024 Dominik Willner <th33xitus@gmail.com>               #
#                                                                         #
#  https://github.com/dw-0/simple-config-parser                           #
#                                                                         #
#  This file may be distributed under the terms of the GNU GPLv3 license  #
# ======================================================================= #
from pathlib import Path

import pytest

from src.simple_config_parser.constants import COLLECTOR_IDENT
from src.simple_config_parser.simple_config_parser import SimpleConfigParser
from tests.utils import load_testdata_from_file

BASE_DIR = Path(__file__).parent.parent.joinpath("assets")
TEST_DATA_PATH = BASE_DIR.joinpath("test_config_1.cfg")


@pytest.fixture
def parser():
    parser = SimpleConfigParser()
    for line in load_testdata_from_file(TEST_DATA_PATH):
        parser._parse_line(line)  # noqa

    return parser


def test_get_options(parser):
    expected_options = {
        "section_1": {"option_1"},
        "section_2": {"option_2"},
        "section_3": {"option_3"},
        "section_4": {"option_4"},
        "section number 5": {"option_5", "multi_option", "option_5_1"},
    }

    for section, options in expected_options.items():
        assert options.issubset(
            parser.get_options(section)
        ), f"Expected options: {options} in section: {section}, got: {parser.get_options(section)}"
        assert "_raw" not in parser.get_options(section)
        assert all(
            not option.startswith(COLLECTOR_IDENT)
            for option in parser.get_options(section)
        )
