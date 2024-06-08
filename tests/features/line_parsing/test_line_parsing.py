import pytest
from data.test_parse_invalid_section import testcases as test_parse_invalid_section
from data.test_parse_valid_option import testcases as test_parse_valid_option
from data.test_parse_valid_section import testcases as test_parse_valid_section

from src.simple_config_parser.simple_config_parser import (
    DuplicateSectionError,
    SimpleConfigParser,
)


@pytest.fixture
def parser():
    return SimpleConfigParser()


class TestLineParsing:
    @pytest.mark.parametrize("given, expected", [*test_parse_valid_section])
    def test_parse_valid_section(self, parser, given, expected):
        parser._parse_section(given)

        # Check that the internal state of the parser is correct
        assert parser.section_name == expected
        assert parser.in_option_block is False
        assert parser._all_sections == [expected]
        assert parser._config[expected]["_raw"] == given
        assert parser._config[expected]["body"] == []

    @pytest.mark.parametrize("given, expected", [*test_parse_invalid_section])
    def test_parse_invalid_section(self, parser, given, expected):
        parser._parse_section(given)

        # Check that the internal state of the parser is correct
        assert parser.section_name == expected
        assert parser.in_option_block is False
        assert parser._all_sections == []
        assert parser._config == {}

    def test_parse_existing_section(self, parser):
        parser._parse_section("[test_section]")
        parser._parse_section("[test_section2]")

        with pytest.raises(DuplicateSectionError) as excinfo:
            parser._parse_section("[test_section]")
            message = "Section 'test_section' is defined more than once"
            assert message in str(excinfo.value)

        # Check that the internal state of the parser is correct
        assert parser.section_name == "test_section"
        assert parser.in_option_block is False
        assert parser._all_sections == ["test_section", "test_section2"]

    @pytest.mark.parametrize(
        "given, expected_option, expected_value",
        [*test_parse_valid_option],
    )
    def test_parse_valid_option(self, parser, given, expected_option, expected_value):
        section_name = "test_section"
        parser.section_name = section_name
        parser._parse_option(given)

        # Check that the internal state of the parser is correct
        assert parser.section_name == section_name
        assert parser.in_option_block is False
        assert parser._all_options[section_name][expected_option] == expected_value

        section_option = parser._config[section_name]["body"][0]
        assert section_option["option"] == expected_option
        assert section_option["value"][0] == expected_value
        assert section_option["_raw"] == given
