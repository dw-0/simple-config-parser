# ======================================================================= #
#  Copyright (C) 2024 Dominik Willner <th33xitus@gmail.com>               #
#                                                                         #
#  https://github.com/dw-0/simple-config-parser                           #
#                                                                         #
#  This file may be distributed under the terms of the GNU GPLv3 license  #
# ======================================================================= #

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from src.simple_config_parser.constants import (
    COLLECTOR_IDENT,
    EMPTY_LINE_RE,
    HEADER_IDENT,
    LINE_COMMENT_RE,
    OPTION_RE,
    OPTIONS_BLOCK_START_RE,
    SECTION_RE,
)


# noinspection PyMethodMayBeStatic
class SimpleConfigParser:
    """A customized config parser targeted at handling Klipper style config files"""

    def __init__(self):
        self._init_state()

    def _init_state(self):
        """Initialize the internal state."""

        self.header: List[str] = []
        self.config: Dict = {}
        self._count: int = 0
        self.current_section: str | None = None
        self.current_opt_block: str | None = None
        self.current_collector: str | None = None
        self.in_option_block: bool = False

    def _match_section(self, line: str) -> bool:
        """Wheter or not the given line matches the definition of a section"""

        return SECTION_RE.match(line) is not None

    def _match_option(self, line: str) -> bool:
        """Wheter or not the given line matches the definition of an option"""

        return OPTION_RE.match(line) is not None

    def _match_options_block_start(self, line: str) -> bool:
        """Wheter or not the given line matches the definition of a multiline option"""

        return OPTIONS_BLOCK_START_RE.match(line) is not None

    def _match_line_comment(self, line: str) -> bool:
        """Wheter or not the given line matches the definition of a comment"""

        return LINE_COMMENT_RE.match(line) is not None

    def _match_empty_line(self, line: str) -> bool:
        """Wheter or not the given line matches the definition of an empty line"""

        return EMPTY_LINE_RE.match(line) is not None

    def _parse_line(self, line: str) -> None:
        """Parses a line and determines its type"""
        if self._match_section(line):
            self.current_collector = None
            self.current_opt_block = None
            self.current_section = SECTION_RE.match(line).group(1)
            self.config[self.current_section] = {"_raw": line}

        elif self._match_option(line):
            self.current_collector = None
            self.current_opt_block = None
            option = OPTION_RE.match(line).group(1)
            value = OPTION_RE.match(line).group(2)
            self.config[self.current_section][option] = {"_raw": line, "value": value}

        elif self._match_options_block_start(line):
            self.current_collector = None
            option = OPTIONS_BLOCK_START_RE.match(line).group(1)
            self.current_opt_block = option
            self.config[self.current_section][option] = {"_raw": line, "values": []}

        elif self.current_opt_block is not None:
            self.config[self.current_section][self.current_opt_block]["values"].append(
                line
            )

        elif self._match_empty_line(line) or self._match_line_comment(line):
            self.current_opt_block = None

            # if current_section is None, we are somewhere at the
            # beginning of the file, so we consider the part up to
            # the first section as the file header
            if not self.current_section:
                self.config.setdefault(HEADER_IDENT, []).append(line)
            else:
                section = self.config[self.current_section]

                # set the current collector to a new value, so that continuous
                # empty lines or comments are collected into the same collector
                if not self.current_collector:
                    self._count += 1
                    section_name = self.current_section.replace(" ", "_")
                    self.current_collector = (
                        f"{COLLECTOR_IDENT}{self._count}_{section_name}"
                    )
                    section[self.current_collector] = []
                section[self.current_collector].append(line)

    def read(self, file: Path):
        """Read and parse a config file"""

        self._init_state()
        with open(file, "r") as file:
            for line in file:
                self._parse_line(line)

        # print(json.dumps(self.config, indent=4))

    def sections(self) -> List[str]:
        """Return a list of all section names, but exclude HEADER_IDENT and COLLECTOR_IDENT"""

        return list(
            filter(
                lambda section: section not in {HEADER_IDENT, COLLECTOR_IDENT},
                self.config.keys(),
            )
        )

    def options(self, section: str) -> List[str]:
        """Return a list of all option names for a given section"""

        return list(
            filter(
                lambda option: option != "_raw"
                and not option.startswith(COLLECTOR_IDENT),
                self.config[section].keys(),
            )
        )
