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
from src.simple_config_parser.simple_config_parser import (
    NoOptionError,
    NoSectionError,
    SimpleConfigParser,
)
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


def test_has_option(parser):
    assert parser.has_option("section_1", "option_1") is True
    assert parser.has_option("section_1", "option_128") is False
    # section does not exist:
    assert parser.has_option("section_128", "option_1") is False


def test_getval(parser):
    # test regular option values
    assert parser.getval("section_1", "option_1") == "value_1"
    assert parser.getval("section_3", "option_3") == "value_3"
    assert parser.getval("section_4", "option_4") == "value_4"
    assert parser.getval("section number 5", "option_5") == "this.is.value-5"
    assert parser.getval("section number 5", "option_5_1") == "value_5_1"
    assert parser.getval("section_2", "option_2") == "value_2"

    # test multiline option values
    ml_val = parser.getval("section number 5", "multi_option")
    assert isinstance(ml_val, list)
    assert len(ml_val) > 0


def test_getval_fallback(parser):
    assert parser.getval("section_1", "option_128", "fallback") == "fallback"


def test_getval_exceptions(parser):
    with pytest.raises(NoSectionError):
        parser.getval("section_128", "option_1")

    with pytest.raises(NoOptionError):
        parser.getval("section_1", "option_128")


def test_getint(parser):
    value = parser.getint("section_1", "option_1_2")
    assert isinstance(value, int)


def test_getint_from_val(parser):
    with pytest.raises(ValueError):
        parser.getint("section_1", "option_1")


def test_getint_from_float(parser):
    with pytest.raises(ValueError):
        parser.getint("section_1", "option_1_3")


def test_getint_from_boolean(parser):
    with pytest.raises(ValueError):
        parser.getint("section_1", "option_1_1")


def test_getint_fallback(parser):
    assert parser.getint("section_1", "option_128", 128) == 128


def test_getboolean(parser):
    value = parser.getboolean("section_1", "option_1_1")
    assert isinstance(value, bool)
    assert value is True or value is False


def test_getboolean_from_val(parser):
    with pytest.raises(ValueError):
        parser.getboolean("section_1", "option_1")


def test_getboolean_from_int(parser):
    with pytest.raises(ValueError):
        parser.getboolean("section_1", "option_1_2")


def test_getboolean_from_float(parser):
    with pytest.raises(ValueError):
        parser.getboolean("section_1", "option_1_3")


def test_getboolean_fallback(parser):
    assert parser.getboolean("section_1", "option_128", True) is True
    assert parser.getboolean("section_1", "option_128", False) is False


def test_getfloat(parser):
    value = parser.getfloat("section_1", "option_1_3")
    assert isinstance(value, float)


def test_getfloat_from_val(parser):
    with pytest.raises(ValueError):
        parser.getfloat("section_1", "option_1")


def test_getfloat_from_int(parser):
    value = parser.getfloat("section_1", "option_1_2")
    assert isinstance(value, float)


def test_getfloat_from_boolean(parser):
    with pytest.raises(ValueError):
        parser.getfloat("section_1", "option_1_1")


def test_getfloat_fallback(parser):
    assert parser.getfloat("section_1", "option_128", 1.234) == 1.234