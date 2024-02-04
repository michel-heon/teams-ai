"""
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the MIT License.
"""

from typing import List

from .layout_engine import LayoutEngine
from .prompt_section import PromptSection


class Prompt(LayoutEngine):
    """
    Top level prompt section.

    Prompts are compositional such that they can be nested to create complex prompt hierarchies.
    """

    def __init__(
        self,
        sections: List[PromptSection],
        tokens: float = -1,
        required: bool = True,
        separator: str = "\n\n",
    ):
        """
        Creates a new 'Prompt' instance.

        Args:
            sections (List[PromptSection]): Sections to render.
            tokens (float, optional): Sizing strategy for this section. Defaults to `auto`.
            required (bool, optional): Indicates if this section is required. Defaults to `true`.
            separator (str, optional): Separator to use between sections when rendering as text.
              Defaults to `\n\n`.
        """
        super().__init__(sections, tokens, required, separator)
