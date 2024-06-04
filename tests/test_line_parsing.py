import pytest

from src.simple_config_parser.simple_config_parser import SimpleConfigParser


@pytest.fixture
def parser():
    return SimpleConfigParser()


class TestLineParsing:
    @pytest.mark.parametrize("line", ["[test_section]", "[test_section two]"])
    def test_parse_valid_section(self, parser, line):
        parser._parse_section(line)

        # Check that the internal state of the parser is correct
        assert parser.curr_sect_name == line.strip("[]")
        assert parser.in_option_block is False
        assert parser._sections == [parser.curr_sect_name]
        assert parser._config[parser.curr_sect_name]["_raw"] == line
        assert parser._config[parser.curr_sect_name]["body"] == []
