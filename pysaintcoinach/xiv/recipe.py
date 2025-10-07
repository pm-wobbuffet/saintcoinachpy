from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet
from .item import Item
from .interfaces import IShop, IItemSource, IShopListing, IShopListingItem

from typing import Iterable
import math


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

    @property
    def item(self) -> Item:
        return self.__item

    @property
    def quality_contributed(self) -> int:
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
        return f"RecipeIngredient(Count={self.__count},Item={self.__item},ContributesQuality={self.__contributes_quality},ItemLevel={self.__item_level},QualityContributed={self.__quality_contributed})"
        # output = ""
        # if self.__count > 1:
        #     output += f"{self.__count}x "
        # output += str(self.__item.as_string("Name"))
        # output += str(self.__item.)
        # return output


@xivrow
class Recipe(XivRow, IItemSource):

    @property
    def received_item(self):
        return self.__received_item

    @property
    def craft_type(self):
        return self.__craft_type

    @property
    def total_ingredient_item_level(self):
        return self.__total_item_level

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
    def max_initial_quality(self) -> int:
        return math.floor(self.quality * self.as_int32("MaterialQualityFactor") / 100)

    @property
    def ingredients(self) -> Iterable[RecipeIngredient] | None:
        if self.__ingredients is None:
            self._build_ingredients()
        return self.__ingredients

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(Recipe, self).__init__(sheet, source_row)
        self.__received_item = RecipeResultItem(
            self.as_T(Item, "ItemResult"), self.as_int32("AmountResult")
        )
        self._sheet = sheet
        self._row = source_row
        self.__craft_type = self.as_T("CraftType", "CraftType")["Name"]
        self.__recipe_level = self.as_T("RecipeLevelTable", "RecipeLevelTable")
        self.__ingredients = None
        self.__total_item_level = 0
        self.__uses_secondary_tool = self.as_boolean("IsSecondary")
        self.__can_quick_synth = self.as_boolean("CanQuickSynth")
        self.__required_craftsmanship = self.as_int32("RequiredCraftsmanship")
        self.__required_control = self.as_int32("RequiredControl")
        self.__required_status = self.as_T("Status", "StatusRequired")
        self.__required_item = self.as_T(Item, "ItemRequired")
        self.__difficulty_factor = self.as_int32("DifficultyFactor")
        self.__quality_factor = self.as_int32("QualityFactor")
        self.__durability_factor = self.as_int32("DurabilityFactor")
        self.__material_quality_factor = self.as_int32("MaterialQualityFactor")
        self.__is_specialist_recipe = False
        self.__is_expert_recipe = False

    def _build_ingredients(self):
        INGREDIENT_COUNT = 8
        self.__ingredients = []  # type: Iterable[RecipeIngredient]
        self.__total_item_level = 0
        for i in range(INGREDIENT_COUNT):
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
        print(self, self.max_initial_quality)

    # def __repr__(self) -> str:
    #     return f"Recipe(Result={self.__received_item}, Crafter={self.__craft_type})"

    # def __str__(self):
    #     return self.__repr__()
