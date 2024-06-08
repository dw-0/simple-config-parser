import pytest
from data.test_line_is_comment import testcases as test_line_is_comment
from data.test_line_is_empty import testcases as test_line_is_empty
from data.test_line_is_multiline_option import (
    testcases as test_line_is_multiline_option,
)
from data.test_line_is_option import testcases as test_line_is_option
from data.test_line_is_section import testcases as test_line_is_section

from src.simple_config_parser.simple_config_parser import SimpleConfigParser


class TestLineTypeDetection:
    def setup_method(self):
        self.parser = SimpleConfigParser()

    def teardown_method(self):
        self.parser = None

    @pytest.mark.parametrize("given, expected", [*test_line_is_section])
    def test_line_is_section(self, given, expected):
        assert self.parser._is_section(given) is expected

    @pytest.mark.parametrize("given, expected", [*test_line_is_option])
    def test_line_is_option(self, given, expected):
        assert self.parser._is_option(given) is expected

    @pytest.mark.parametrize("given, expected", [*test_line_is_multiline_option])
    def test_line_is_multiline_option(self, given, expected):
        assert self.parser._is_multiline_option(given) is expected

    @pytest.mark.parametrize("given, expected", [*test_line_is_comment])
    def test_line_is_comment(self, given, expected):
        assert self.parser._is_comment(given) is expected

    @pytest.mark.parametrize("given, expected", [*test_line_is_empty])
    def test_line_is_empty(self, given, expected):
        assert self.parser._is_empty_line(given) is expected
