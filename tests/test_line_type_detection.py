import pytest

from src.simple_config_parser.simple_config_parser import SimpleConfigParser


@pytest.fixture
def parser():
    return SimpleConfigParser()


class TestLineTypeDetection:
    def test_line_is_section(self, parser):
        assert parser._is_section("[example_section]") is True
        assert parser._is_section("[example_section two]") is True
        assert parser._is_section("not_a_section") is False
        assert parser._is_section("section: invalid") is False

    def test_line_is_option(self, parser):
        assert parser._is_option("example_option: value") is True
        assert parser._is_option("example_option= value") is True
        assert parser._is_option("example_option = value") is True
        assert parser._is_option("example_option : value") is True
        assert parser._is_option("example_option :value") is True
        assert parser._is_option("example_option =value") is True
        assert parser._is_option("example_option = value") is True
        assert parser._is_option("example_option : value") is True
        assert parser._is_option("example_option :value") is True
        assert parser._is_option("example_option =value") is True
        assert parser._is_option("not_an_option") is False
        assert parser._is_option("[not_an_option]") is False

    def test_line_is_multiline_option(self, parser):
        assert parser._is_multiline_option("example_option:") is True
        assert parser._is_multiline_option("example_option: ") is True
        assert parser._is_multiline_option("example_option: value") is False
        assert parser._is_multiline_option("example_option::") is False
        assert parser._is_multiline_option("example_option:=") is False
        assert parser._is_multiline_option("example_option==") is False
        assert parser._is_multiline_option("example_option :=") is False
        assert parser._is_multiline_option("example_option ==") is False
        assert parser._is_multiline_option("example_option: # inline comment") is True
        assert parser._is_multiline_option("example_option= # inline comment") is True

    def test_line_is_comment(self, parser):
        assert parser._is_comment("# an arbitrary comment") is True
        assert parser._is_comment("; another arbitrary comment") is True
        assert parser._is_comment("  ; indented comment") is True
        assert parser._is_comment("  # indented comment") is True
        assert parser._is_comment("example_option: value") is False
        assert parser._is_comment("example_option= value") is False
        assert parser._is_comment("example_option = value") is False
        assert parser._is_comment("example_option : value") is False
        assert parser._is_comment("example_option :value") is False
        assert parser._is_comment("example_option =value") is False

    def test_line_is_empty(self, parser):
        assert parser._is_empty_line("") is True
        assert parser._is_empty_line(" ") is True
        assert parser._is_empty_line("not empty") is False
