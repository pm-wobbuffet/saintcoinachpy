from enum import Enum
from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet


class RecipeCondition(Enum):
    """Enumeration of possible recipe step conditions"""

    NORMAL = 0
    GOOD = 1
    EXCELLENT = 2
    POOR = 3
    CENTERED = 4
    STURDY = 5
    PLIANT = 6
    MALLEABLE = 7
    PRIMED = 8
    GOOD_OMEN = 9

    def __str__(self) -> str:
        return f"{self.name.capitalize()}"

    def __repr__(self) -> str:
        return f"{self.name.capitalize()}"


@xivrow
class RecipeLevelTable(XivRow):
    """
    The RecipeLevelTable sheet contains basic stats for all recipes with the given
    Level. It serves as a base for recipe properties when combined with individual
    multipliers found within the Recipe sheet to determine final quality, progress,
    and durability.
    """

    @property
    def conditions_flag(self) -> int:
        """The raw integer representing the conditions list"""
        return self.as_int32("ConditionsFlag")

    @property
    def conditions_list(self) -> list:
        """The listing of possible conditions based on ConditionsFlag"""
        s = f"{self.conditions_flag:b}"[::-1]  # Convert to reverse binary string
        return [RecipeCondition(i) for i, char in enumerate(s) if char == "1"]

    @property
    def difficulty(self) -> int:
        """The base progress for this Level, before any recipe modifiers"""
        return self.as_int32("DIfficulty")

    @property
    def display_level(self) -> str:
        """The level of the recipe as shown in game, i.e. 90** for master recipes"""
        return f"{str(self.level)}{'*' * self.stars }"

    def durability(self) -> int:
        """Base Durability (needs to be multiplied by a recipe-specific multiplier for final durability)"""
        return self.as_int32("Durability")

    @property
    def level(self) -> int:
        """The base level of the recipe, roughly a job level"""
        return self.as_int32("ClassJobLevel")

    @property
    def progress_divider(self) -> int:
        return self.as_int32("ProgressDivider")

    @property
    def progress_modifier(self) -> int:
        return self.as_int32("ProgressModifier")

    @property
    def quality(self) -> int:
        """The base quality for this Level, before any recipe modifiers"""
        return self.as_int32("Quality")

    @property
    def quality_divider(self) -> int:
        return self.as_int32("QualityDivider")

    @property
    def quality_modifier(self) -> int:
        return self.as_int32("QualityModifier")

    @property
    def stars(self) -> int:
        """The number of stars assigned to a recipe at a given Level"""
        return self.as_int16("Stars")

    @property
    def suggested_craftsmanship(self) -> int:
        """The craftsmanship suggested at this recipe level"""
        return self.as_int32("SuggestedCraftsmanship")

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super().__init__(sheet, source_row)
