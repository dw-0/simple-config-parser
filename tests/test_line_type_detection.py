import pytest

from src.simple_config_parser.simple_config_parser import SimpleConfigParser


class TestLineTypeDetection:
    def setup_method(self):
        self.parser = SimpleConfigParser()

    def teardown_method(self):
        self.parser = None

    @pytest.mark.parametrize(
        "given, expected",
        [
            ("[example_section]", True),
            ("[example_section two]", True),
            ("not_a_valid_section", False),
            ("section: invalid", False),
        ],
    )
    def test_line_is_section(self, given, expected):
        assert self.parser._is_section(given) is expected

    @pytest.mark.parametrize(
        "given, expected",
        [
            ("valid_option: value", True),
            ("valid_option: value\n", True),
            ("valid_option: value ; inline comment", True),
            ("valid_option: value # inline comment", True),
            ("valid_option: value # inline comment\n", True),
            ("valid_option : value", True),
            ("valid_option :value", True),
            ("valid_option= value", True),
            ("valid_option = value", True),
            ("valid_option =value", True),
            ("invalid_option:", False),
            ("invalid_option=", False),
            ("invalid_option:: value", False),
            ("invalid_option :: value", False),
            ("invalid_option ::value", False),
            ("invalid_option== value", False),
            ("invalid_option == value", False),
            ("invalid_option ==value", False),
            ("invalid_option:= value", False),
            ("invalid_option := value", False),
            ("invalid_option :=value", False),
            ("[that_is_a_section]", False),
            ("[that_is_section two]", False),
            ("not_a_valid_option", False),
        ],
    )
    def test_line_is_option(self, given, expected):
        assert self.parser._is_option(given) is expected

    @pytest.mark.parametrize(
        "given, expected",
        [
            ("valid_option:", True),
            ("valid_option:\n", True),
            ("valid_option: ; inline comment", True),
            ("valid_option: # inline comment", True),
            ("valid_option :", True),
            ("valid_option=", True),
            ("valid_option= ", True),
            ("valid_option =", True),
            ("valid_option = ", True),
            ("invalid_option ==", False),
            ("invalid_option :=", False),
            ("not_a_valid_option", False),
        ],
    )
    def test_line_is_multiline_option(self, given, expected):
        assert self.parser._is_multiline_option(given) is expected

    @pytest.mark.parametrize(
        "given, expected",
        [
            ("# an arbitrary comment", True),
            ("; another arbitrary comment", True),
            ("  ; indented comment", True),
            ("  # indented comment", True),
            ("not_a: comment", False),
            ("also_not_a= comment", False),
            ("[definitely_not_a_comment]", False),
        ],
    )
    def test_line_is_comment(self, given, expected):
        assert self.parser._is_comment(given) is expected

    @pytest.mark.parametrize(
        "given, expected",
        [
            ("", True),
            (" ", True),
            ("not empty", False),
            ("  # indented comment", False),
            ("not: empty", False),
            ("also_not= empty", False),
            ("[definitely_not_empty]", False),
        ],
    )
    def test_line_is_empty(self, given, expected):
        assert self.parser._is_empty_line(given) is expected
