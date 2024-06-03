# ======================================================================= #
#  Copyright (C) 2020 - 2024 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  https://github.com/dw-0/simple-config-parser                           #
#                                                                         #
#  This file may be distributed under the terms of the GNU GPLv3 license  #
# ======================================================================= #

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, List, Tuple, TypedDict

_UNSET = object()


class Section(TypedDict):
    _raw: str
    options: List[Option]


class Option(TypedDict, total=False):
    is_multiline: bool
    option: str
    value: List[str]
    _raw: str
    _raw_value: List[str]


class NoSectionError(Exception):
    """Raised when a section is not defined"""

    def __init__(self, section: str):
        msg = f"Section '{section}' is not defined"
        super().__init__(msg)


class NoOptionError(Exception):
    """Raised when an option is not defined in a section"""

    def __init__(self, option: str, section: str):
        msg = f"Option '{option}' in section '{section}' is not defined"
        super().__init__(msg)


class DuplicateSectionError(Exception):
    """Raised when a section is defined more than once"""

    def __init__(self, section: str):
        msg = f"Section '{section}' is defined more than once"
        super().__init__(msg)


class DuplicateOptionError(Exception):
    """Raised when an option is defined more than once"""

    def __init__(self, option: str, section: str):
        msg = f"Option '{option}' in section '{section}' is defined more than once"
        super().__init__(msg)


# noinspection PyMethodMayBeStatic
class SimpleConfigParser:
    """A customized config parser targeted at handling Klipper style config files"""

    _SECTION_RE = re.compile(r"\s*\[(\w+ ?\w+)]\s*([#|;].*)*$")
    _OPTION_RE = re.compile(r"^\s*(\w+)\s*[:=][^:=]\s*(.+)\s*([#|;]*).*$")
    _ML_OPTION_RE = re.compile(r"^\s*(\w+)\s*[:=][^:=]\s*([#|;]*).*$")
    _COMMENT_RE = re.compile(r"^\s*[#;].*")
    _EMPTY_LINE_RE = re.compile(r"^\s*$")

    BOOLEAN_STATES = {
        "1": True,
        "yes": True,
        "true": True,
        "on": True,
        "0": False,
        "no": False,
        "false": False,
        "off": False,
    }

    def __init__(self):
        self._config: dict = {}
        self._header: List[str] = []
        self._sections: List[str] = []
        self._options: dict = {}
        self.curr_sect_name: str = ""
        self.in_option_block: bool = False  # whether we are in a multiline option block

    def read(self, file: Path):
        """Read the given file and store the result in the internal state"""

        try:
            with open(file, "r") as f:
                self._parse_config(f.readlines())

        except OSError:
            raise

    def write(self, filename):
        """Write the internal state to the given file"""

        content: List[str] = []

        if self._header is not None:
            content.extend(self._header)

        for section in self._config:
            content.append(self._config[section]["_raw"])

            if (sec_body := self._config[section].get("body")) is not None:
                for option in sec_body:
                    content.extend(option["_raw"])
                    if option["is_multiline"]:
                        content.extend(option["_raw_value"])

        content: str = "".join(content)

        with open(filename, "w") as f:
            f.write(content)

    def sections(self) -> List[str]:
        """Return a list of section names"""

        return self._sections

    def add_section(self, section: str) -> None:
        """Add a new section to the internal state"""

        if section in self._sections:
            raise DuplicateSectionError(section)
        self._sections.append(section)
        self._options[section] = {}
        self._config[section] = {"_raw": f"\n[{section}]\n", "body": []}

    def remove_section(self, section: str) -> None:
        """Remove the given section"""

        if section not in self._sections:
            raise NoSectionError(section)

        del self._sections[self._sections.index(section)]
        del self._options[section]
        del self._config[section]

    def options(self, section) -> List[str]:
        """Return a list of option names for the given section name"""

        return self._options.get(section)

    def get(self, section: str, option: str, fallback: str | _UNSET = _UNSET) -> str:
        """
        Return the value of the given option in the given section

        If the key is not found and 'fallback' is provided, it is used as
        a fallback value.
        """

        try:
            if section not in self._sections:
                raise NoSectionError(section)

            if option not in self._options.get(section):
                raise NoOptionError(option, section)

            return self._options[section][option]
        except (NoSectionError, NoOptionError):
            if fallback is not _UNSET:
                raise
            return fallback

    def getint(self, section: str, option: str, fallback: int | _UNSET = _UNSET) -> int:
        """Return the value of the given option in the given section as an int"""

        return self._get_conv(section, option, int, fallback=fallback)

    def getfloat(
        self, section: str, option: str, fallback: float | _UNSET = _UNSET
    ) -> float:
        return self._get_conv(section, option, int, fallback=fallback)

    def getboolean(
        self, section: str, option: str, fallback: bool | _UNSET = _UNSET
    ) -> bool:
        return self._get_conv(
            section, option, self._convert_to_boolean, fallback=fallback
        )

    def _convert_to_boolean(self, value):
        if value.lower() not in self.BOOLEAN_STATES:
            raise ValueError("Not a boolean: %s" % value)
        return self.BOOLEAN_STATES[value.lower()]

    def _get_conv(
        self,
        section: str,
        option: str,
        conv: Callable[[str], int | float | bool],
        fallback: _UNSET = _UNSET,
    ) -> int | float | bool:
        try:
            return conv(self.get(section, option, fallback))
        except:
            if fallback is not _UNSET:
                return fallback
            raise

    def items(self, section: str) -> List[Tuple[str, str]]:
        """Return a list of (option, value) tuples for a specific section"""

        if section not in self._sections:
            raise NoSectionError(section)

        result = []
        for _option in self._options[section]:
            result.append((_option, self._options[section][_option]))

        return result

    def set(
        self,
        section: str,
        option: str,
        value: str,
        multiline: bool = False,
        indent: int = 2,
    ) -> None:
        """Set the given option to the given value in the given section

        If the option is already defined, it will be overwritten. If the option
        is not defined yet, it will be added to the section body.

        The multiline parameter can be used to specify whether the value is
        multiline or not. If it is not specified, the value will be considered
        as multiline if it contains a newline character. The value will then be split
        into multiple lines. If the value does not contain a newline character, it
        will be considered as a single line value. The indent parameter can be used
        to specify the indentation of the multiline value. Indentations are with spaces.

        :param section: The section to set the option in
        :param option: The option to set
        :param value: The value to set
        :param multiline: Whether the value is multiline or not
        :param indent: The indentation for multiline values
        """

        if section not in self._sections:
            raise NoSectionError(section)

        # prepare the options value and raw value depending on the multiline flag
        if multiline or "\n" in value:
            _multiline = True
            _raw: str = f"{option}:\n"
            _value: List[str] = value.split("\n")
            _raw_value: List[str] = [f"{' ' * indent}{v}\n" for v in _value]
        else:
            _multiline = False
            _raw: str = f"{option}: {value}\n"
            _value: List[str] = [value]
            _raw_value: List[str] = [f"{value}\n"]

        # the option does not exist yet
        if option not in self._options.get(section):
            _option: Option = {
                "is_multiline": _multiline,
                "option": option,
                "value": _value,
                "_raw": _raw,
                "_raw_value": _raw_value,
            }
            self._config[section]["body"].append(_option)

        # the option exists and we need to update it
        else:
            for _option in self._config[section]["body"]:
                if _option["option"] == option:
                    _option["value"] = _value
                    _option["_raw"] = _raw
                    _option["_raw_value"] = _raw_value
                    break

        self._options[section][option] = _value

    def remove_option(self, section: str, option: str) -> None:
        """Remove the given option from the given section"""

        if section not in self._sections:
            raise NoSectionError(section)

        if option not in self._options.get(section):
            raise NoOptionError(option, section)

        for _option in self._config[section]["body"]:
            if _option["option"] == option:
                del self._options[section][option]
                self._config[section]["body"].remove(_option)
                break

    def has_section(self, section: str) -> bool:
        """Return True if the given section exists, False otherwise"""
        return section in self._sections

    def has_option(self, section: str, option: str) -> bool:
        """Return True if the given option exists in the given section, False otherwise"""
        return option in self._options.get(section)

    def _is_section(self, line: str) -> bool:
        """Check if the given line contains a section definition"""
        return self._SECTION_RE.match(line) is not None

    def _is_option(self, line: str) -> bool:
        """Check if the given line contains an option definition"""
        return self._OPTION_RE.match(line) is not None

    def _is_comment(self, line: str) -> bool:
        """Check if the given line is a comment"""
        return self._COMMENT_RE.match(line) is not None

    def _is_empty_line(self, line: str) -> bool:
        """Check if the given line is an empty line"""
        return self._EMPTY_LINE_RE.match(line) is not None

    def _is_multiline_option(self, line: str) -> bool:
        """Check if the given line starts a multiline option block"""

        # if the pattern doesn't match, we directly return False
        if self._ML_OPTION_RE.match(line) is None:
            return False

        return True

    def _parse_config(self, content: List[str]) -> None:
        """Parse the given content and store the result in the internal state"""

        _curr_multi_opt = ""

        # THE ORDER MATTERS, DO NOT REORDER THE CONDITIONS!
        for line in content:
            if self._is_section(line):
                self._parse_section(line)

            elif self._is_option(line):
                self._parse_option(line)

            # if it's not a regular option with the value inline,
            # it might be a might be a multiline option block
            elif self._is_multiline_option(line):
                self.in_option_block = True
                _curr_multi_opt = self._ML_OPTION_RE.match(line).group(1).strip()
                self._add_option_to_section_body(_curr_multi_opt, "", line)

            elif self.in_option_block:
                self._parse_multiline_option(_curr_multi_opt, line)

            # if it's nothing from above, it's probably a comment or an empty line
            elif self._is_comment(line) or self._is_empty_line(line):
                self._parse_comment(line)

    def _parse_section(self, line: str) -> None:
        """Parse a section line and store the result in the internal state"""

        self.in_option_block = False
        self.curr_sect_name = self._SECTION_RE.match(line).group(1).strip()

        # add the section to the internal section list
        if self.curr_sect_name in self._sections:
            raise DuplicateSectionError(self.curr_sect_name)
        self._sections.append(self.curr_sect_name)

        # add the section to the internal global config state
        self._config[self.curr_sect_name]: Section = {
            "_raw": line,
            "body": [],
        }

    def _parse_option(self, line: str) -> None:
        """Parse an option line and store the result in the internal state"""

        self.in_option_block = False

        if self._options.get(self.curr_sect_name) is None:
            self._options[self.curr_sect_name] = {}

        # add the option to the internal option list
        option = self._OPTION_RE.match(line).group(1).strip()
        value = self._OPTION_RE.match(line).group(2).strip()
        if option in self._options[self.curr_sect_name]:
            raise DuplicateOptionError(option, self.curr_sect_name)
        self._options[self.curr_sect_name][option] = value

        # add the option to the internal global config state
        self._add_option_to_section_body(option, value, line)

    def _parse_multiline_option(self, curr_ml_opt: str, line: str) -> None:
        """Parse a multiline option line and store the result in the internal state"""

        if self._options.get(self.curr_sect_name) is None:
            self._options[self.curr_sect_name] = {}

        if self._options[self.curr_sect_name].get(curr_ml_opt) is None:
            self._options[self.curr_sect_name][curr_ml_opt] = []

        _cleaned_line = line.strip().strip("\n")
        if not _cleaned_line == "" and not self._is_comment(line):
            self._options[self.curr_sect_name][curr_ml_opt].append(_cleaned_line)

        # add the option to the internal multiline option value state
        for _option in self._config[self.curr_sect_name]["body"]:
            if _option["option"] == curr_ml_opt:
                _option["is_multiline"] = True
                _option["_raw_value"].append(line)
                if not self._is_comment(line) and not _cleaned_line == "":
                    _option["value"].append(_cleaned_line)

    def _parse_comment(self, line: str) -> None:
        """
        Parse a comment line and store the result in the internal state

        If the there was no previous section parsed, the lines are handled as
        the file header and added to the internal header list as it means, that
        we are at the very top of the file.
        """

        self.in_option_block = False

        if not self.curr_sect_name:
            self._header.append(line)
        else:
            self._add_option_to_section_body("", "", line)

    def _add_option_to_section_body(
        self, option: str, value: str, line: str, is_multiline: bool = False
    ) -> None:
        """Add a raw option line to the internal state"""

        if self._config[self.curr_sect_name].get("body") is None:
            self._config[self.curr_sect_name]["body"]: List[Option] = []

        val = [value] if value and not self._is_comment(value) else []
        raw_val = [value] if value else []

        _option: Option = {
            "is_multiline": is_multiline,
            "option": option,
            "value": val,
            "_raw": line,
            "_raw_value": raw_val,
        }
        self._config[self.curr_sect_name]["body"].append(_option)
