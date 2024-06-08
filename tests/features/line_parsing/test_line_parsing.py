import pytest

from src.simple_config_parser.simple_config_parser import (
    DuplicateSectionError,
    SimpleConfigParser,
)


class TestLineParsing:
    def setup_method(self):
        self.parser = SimpleConfigParser()

    def teardown_method(self):
        self.parser = None

    @pytest.mark.parametrize(
        "given, expected",
        [
            ("[test_section]", "test_section"),
            ("[test_section two]", "test_section two"),
            ("[section1] # inline comment", "section1"),
            ("[section2] ; second comment", "section2"),
        ],
    )
    def test_parse_valid_section(self, given, expected):
        self.parser._parse_section(given)

        # Check that the internal state of the parser is correct
        assert self.parser.section_name == expected
        assert self.parser.in_option_block is False
        assert self.parser._all_sections == [expected]
        assert self.parser._config[expected]["_raw"] == given
        assert self.parser._config[expected]["body"] == []

    @pytest.mark.parametrize(
        "given, expected",
        [
            ("not_a_section", ""),
            ("[invavid: section]", ""),
            ("section: invalid", ""),
        ],
    )
    def test_parse_invalid_section(self, given, expected):
        self.parser._parse_section(given)

        # Check that the internal state of the parser is correct
        assert self.parser.section_name == expected
        assert self.parser.in_option_block is False
        assert self.parser._all_sections == []
        assert self.parser._config == {}

    def test_parse_existing_section(self):
        self.parser._parse_section("[test_section]")
        self.parser._parse_section("[test_section2]")

        with pytest.raises(DuplicateSectionError) as excinfo:
            self.parser._parse_section("[test_section]")
            message = "Section 'test_section' is defined more than once"
            assert message in str(excinfo.value)

        # Check that the internal state of the parser is correct
        assert self.parser.section_name == "test_section"
        assert self.parser.in_option_block is False
        assert self.parser._all_sections == ["test_section", "test_section2"]

    @pytest.mark.parametrize(
        "given, expected_option, expected_value",
        [
            ("option: value", "option", "value"),
            ("option : value", "option", "value"),
            ("option :value", "option", "value"),
            ("option= value", "option", "value"),
            ("option = value", "option", "value"),
            ("option =value", "option", "value"),
            ("option: value\n", "option", "value"),
            ("option: value # inline comment", "option", "value"),
            ("option: value # inline comment\n", "option", "value"),
        ],
    )
    def test_parse_valid_option(self, given, expected_option, expected_value):
        section_name = "test_section"
        self.parser.section_name = section_name
        self.parser._parse_option(given)

        # Check that the internal state of the parser is correct
        assert self.parser.section_name == section_name
        assert self.parser.in_option_block is False
        assert self.parser._all_options[section_name][expected_option] == expected_value

        section_option = self.parser._config[section_name]["body"][0]
        assert section_option["option"] == expected_option
        assert section_option["value"][0] == expected_value
        assert section_option["_raw"] == given
