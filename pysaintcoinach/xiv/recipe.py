from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet
from .item import Item

from typing import Iterable
from enum import Enum
import math


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


class RecipeResultItem:

    def __init__(self, item: "Item", count: int) -> None:
        self.__item = item
        self.__count = count

    def __repr__(self) -> str:
        output = ""
        if self.__count > 1:
            output += f"{self.__count}x "
        output += str(self.__item.as_string("Name"))
        return output


class RecipeIngredient:
    """Representation of an ingredient in a Recipe"""

    @property
    def item(self) -> Item:
        """The underlying Item instance for this recipe ingredient"""
        return self.__item

    @property
    def quality_contributed(self) -> int:
        """The amount of quality that one instance of this Item will add to starting quality"""
        return self.__quality_contributed

    @quality_contributed.setter
    def quality_contributed(self, value):
        self.__quality_contributed = value

    def __init__(self, item: "Item", count: int) -> None:
        self.__item = item
        self.__count = count
        self.__contributes_quality = item.as_boolean("CanBeHq")
        self.__item_level = item["LevelItem"].key
        self.__quality_contributed = 0

    def set_quality_amount(self, recipe: "Recipe"):
        """Set the starting quality contributed for this ingredient in a given recipe"""

        if recipe.total_ingredient_item_level == 0 or not self.item.as_boolean(
            "CanBeHq"
        ):
            self.quality_contributed = 0
            return
        self.quality_contributed = math.floor(
            recipe.max_initial_quality
            * (self.__item_level / recipe.total_ingredient_item_level)
        )

    def __repr__(self) -> str:
        return (
            f"RecipeIngredient(Count={self.__count},Item={self.__item},"
            + f"ContributesQuality={self.__contributes_quality},"
            + f"ItemLevel={self.__item_level},QualityContributed={self.__quality_contributed})"
        )
        # output = ""
        # if self.__count > 1:
        #     output += f"{self.__count}x "
        # output += str(self.__item.as_string("Name"))
        # output += str(self.__item.)
        # return output


@xivrow
class Recipe(XivRow):

    INGREDIENT_COUNT = 8

    @property
    def can_quicksynth(self) -> bool:
        """Whether a recipe is valid for quick synthesis"""
        return self.__can_quick_synth

    @property
    def conditions_flag(self):
        """The raw conditions flag integer. Mostly useless as is.
        Requires converting into a binary string and reversing the order
        to determine Conditions (see conditions_list)"""
        return int(self.__recipe_level["ConditionsFlag"])

    @property
    def conditions_list(self) -> Iterable[RecipeCondition] | None:
        """The listing of possible conditions based on ConditionsFlag"""
        s = f"{self.conditions_flag:b}"[::-1]
        return [RecipeCondition(i) for i, char in enumerate(s) if char == "1"]

    @property
    def craft_type(self) -> "CraftType":  # type: ignore
        """Returns the CraftType of a craft, used for linking to a particular crafter class"""
        return self.__craft_type

    @property
    def durability(self) -> int:
        """The total max durability for a craft"""
        return math.floor(
            self.__recipe_level["Durability"] * self.__durability_factor / 100
        )

    @property
    def ingredients(self) -> Iterable[RecipeIngredient] | None:
        """The list of ingredients required to craft a particular recipe"""
        if self.__ingredients is None:
            self._build_ingredients()
        return self.__ingredients

    @property
    def is_expert_recipe(self) -> bool:
        """Whether a recipe is Expert or not"""
        return self.as_boolean("IsExpert")

    @property
    def is_specialist_recipe(self) -> bool:
        """Whether the recipe requires a specialist job stone before crafting can begin"""
        return self.as_boolean("IsSpecializationRequired")

    @property
    def master_book(self) -> Item | None:
        """The master recipe book that contains this recipe"""
        return self.__master_recipe_book["Item"]

    @property
    def max_initial_quality(self) -> int:
        """The numerical max starting quality possible for a recipe"""
        return math.floor(self.quality * self.__material_quality_factor / 100)

    @property
    def progress(self) -> int:
        """Total required progress for fully finishing craft"""
        return math.floor(
            self.__recipe_level["Difficulty"] * self.__difficulty_factor / 100
        )

    @property
    def quality(self) -> int:
        """Total quality possible for the craft"""
        return math.floor(self.__recipe_level["Quality"] * self.__quality_factor / 100)

    @property
    def received_item(self):
        """The final item received from crafting this recipe"""
        return self.__received_item

    @property
    def received_item_amount(self):
        """The number of recieved_item received at the end of the craft"""
        return self.__received_item_count

    @property
    def required_control(self) -> int:
        """The amount of control a player must have before crafting can begin"""
        return self.__required_control

    @property
    def required_craftsmanship(self) -> int:
        """The amount of craftsmanship a player must have before crafting can begin"""
        return self.__required_craftsmanship

    @property
    def required_item(self) -> Item:
        """The item that must be equipped before crafting can begin"""
        return self.__required_item

    @property
    def required_status(self) -> "Status":  # type: ignore
        """The required status(buff) that the player must have before crafting can begin
        (think Ixal allied society daily quests)"""
        return self.__required_status

    @property
    def total_ingredient_item_level(self) -> int:
        """The sum of the ingredient item levels in the recipe,
        used in calculating the quality contributed by individual items."""
        return self.__total_item_level

    @property
    def uses_secondary_tool(self) -> bool:
        """Whether the crafting animation uses the secondary (offhand tool)"""
        return self.__uses_secondary_tool

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super().__init__(sheet, source_row)
        self.__received_item = RecipeResultItem(
            self.as_T(Item, "ItemResult"), self.as_int32("AmountResult")
        )
        self.__received_item_count = self.as_int16("AmountResult")
        self._sheet = sheet
        self._row = source_row
        self.__craft_type = self.as_T("CraftType", "CraftType")["Name"]  # type: ignore
        self.__recipe_level = self.as_T("RecipeLevelTable", "RecipeLevelTable")  # type: ignore
        self.__ingredients = None  # type: ignore
        self.__total_item_level = 0
        self.__uses_secondary_tool = self.as_boolean("IsSecondary")
        self.__can_quick_synth = self.as_boolean("CanQuickSynth")
        self.__required_craftsmanship = self.as_int32("RequiredCraftsmanship")
        self.__required_control = self.as_int32("RequiredControl")
        self.__required_status = self.as_T("Status", "StatusRequired")  # type:ignore
        self.__required_item = self.as_T(Item, "ItemRequired")
        self.__difficulty_factor = self.as_int32("DifficultyFactor")
        self.__quality_factor = self.as_int32("QualityFactor")
        self.__durability_factor = self.as_int32("DurabilityFactor")
        self.__material_quality_factor = self.as_int32("MaterialQualityFactor")
        self.__master_recipe_book = self.as_T(
            "SecretRecipeBook", "SecretRecipeBook"  # type: ignore
        )

    def _build_ingredients(self):

        self.__ingredients = []  # type: Iterable[RecipeIngredient]
        self.__total_item_level = 0
        for i in range(self.INGREDIENT_COUNT):
            item = self.as_T(Item, f"Ingredient[{i}]")
            amount = self.as_int32(f"AmountIngredient[{i}]")
            if not item or item.key < 1:
                continue
            if item.as_boolean("CanBeHq"):
                self.__total_item_level += item["LevelItem"].key * amount
            self.__ingredients.append(
                RecipeIngredient(
                    self.as_T(Item, f"Ingredient[{i}]"),
                    self.as_int32(f"AmountIngredient[{i}]"),
                )
            )
        for i in self.__ingredients:
            i.set_quality_amount(self)

    # def __repr__(self) -> str:
    #     return f"Recipe(Result={self.__received_item}, Crafter={self.__craft_type})"

    # def __str__(self):
    #     return self.__repr__()
