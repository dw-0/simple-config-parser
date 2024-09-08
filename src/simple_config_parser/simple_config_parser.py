# ======================================================================= #
#  Copyright (C) 2024 Dominik Willner <th33xitus@gmail.com>               #
#                                                                         #
#  https://github.com/dw-0/simple-config-parser                           #
#                                                                         #
#  This file may be distributed under the terms of the GNU GPLv3 license  #
# ======================================================================= #

from __future__ import annotations

from typing import Dict, List

from src.simple_config_parser.constants import SECTION_RE


# noinspection PyMethodMayBeStatic
class SimpleConfigParser:
    """A customized config parser targeted at handling Klipper style config files"""

    def __init__(self):
        self._config: Dict = {}
        self._header: List[str] = []
        self._all_sections: List[str] = []
        self._all_options: Dict = {}
        self.section_name: str = ""
        self.in_option_block: bool = False  # whether we are in a multiline option block

    def _match_section(self, line: str) -> None:
        """Wheter or not the given line matches the definition of a section"""

        return SECTION_RE.match(line) is not None
