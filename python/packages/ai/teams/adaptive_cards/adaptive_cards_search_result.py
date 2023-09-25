"""
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the MIT License.
"""

from dataclasses import dataclass


@dataclass
class AdaptiveCardsSearchResult:
    title: str
    value: str