from itertools import filterfalse, chain
from typing import cast
from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet


def flatten(listOfLists):
    """Flatten one level of nesting"""
    return chain.from_iterable(listOfLists)


def unique_everseen(iterable, key=None):
    """
    List unique elements, preserving order. Remember all elements ever seen.
    """
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


class ItemBase(XivRow):

    NUMBER_OF_STAT_COLUMNS = 6

    @property
    def name(self) -> str:
        return self.get_raw("Name")

    @property
    def description(self) -> str:
        return self.get_raw("Description")

    @property
    def equip_level(self) -> int:
        return self.as_int32("LevelEquip")

    @property
    def item_level(self) -> int:
        return self.as_T("ItemLevel", "LevelItem").key

    @property
    def stats(self):
        stats = {"HQ": {}, "NQ": {}}
        for i in range(self.NUMBER_OF_STAT_COLUMNS):
            if self.as_T("BaseParam", "BaseParam", i).key != 0:
                bp = self.as_T("BaseParam", "BaseParam", i)["Name"]
                if bp not in stats["NQ"]:
                    stats["NQ"][bp] = 0
                if bp not in stats["HQ"]:
                    stats["HQ"][bp] = 0
                stats["NQ"][bp] += self.as_int32("BaseParamValue", i)
                stats["HQ"][bp] += self.as_int32("BaseParamValue", i)

            if self.as_T("BaseParam", "BaseParamSpecial", i).key != 0:
                bonus = self.as_T("BaseParam", "BaseParamSpecial", i)
                if bonus.key != 0:
                    if bonus["Name"] not in stats["HQ"]:
                        stats["HQ"][bonus["Name"]] = 0
                    stats["HQ"][bonus["Name"]] += self.as_int32(
                        "BaseParamValueSpecial", i
                    )
        return stats

    @property
    def unique(self) -> bool:
        return self.as_boolean("IsUnique")

    @property
    def untradable(self) -> bool:
        return self.as_boolean("IsUntradable")

    @property
    def indisposable(self) -> bool:
        return self.as_boolean("IsIndisposable")

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(ItemBase, self).__init__(sheet, source_row)


@xivrow
class Item(ItemBase):

    @property
    def bid(self):
        return self.get_raw("PriceLow")

    @property
    def ask(self):
        return self.get_raw("PriceMid")

    @property
    def can_be_hq(self) -> bool:
        return self.as_boolean("CanBeHq")

    @property
    def icon(self):
        return self.as_T("Icon", "Icon")

    @property
    def is_collectable(self):
        return self.as_boolean("IsCollectable")

    @property
    def recipes_as_material(self):
        if self.__recipes_as_material is None:
            self.__recipes_as_material = self.__build_recipes_as_material()
        return self.__recipes_as_material

    @property
    def as_shop_payment(self):
        if self.__as_shop_payment is None:
            self.__as_shop_payment = self.__build_as_shop_payment()
        return self.__as_shop_payment

    @property
    def rarity(self) -> int:
        """
        Gets the rarity of the current item.
        :return: The rarity of the current item.

        1: Common (White)
        2: Uncommon (Green)
        3: Rare (Blue)
        4: Relic (Purple)
        7: Aetherial (Pink)
        """
        return self.as_int32("Rarity")

    @property
    def is_aetherial_reducible(self) -> bool:
        return self.as_int32("AetherialReduce") > 0

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(Item, self).__init__(sheet, source_row)
        self.__recipes_as_material = None
        self.__as_shop_payment = None

    def __build_recipes_as_material(self):

        if self.key < 20:
            # elemental shards, crystals, clusters would be in a bazillion things
            return []
        recipes = self.sheet.collection.get_sheet("Recipe")
        ret = []
        for r in recipes:
            if r.contains_ingredient(self):
                ret.append(r)

        return ret

    def __build_as_shop_payment(self):
        if self.key == 1:
            return []  # XXX: DO NOT BUILD THIS FOR GIL, THAT WOULD BE BAD!

        shops = self.sheet.collection.shops

        checked_items = []
        shop_item_costs = []
        for item in flatten(
            map(
                lambda shop: filterfalse(
                    lambda _: _ in checked_items, shop.shop_listings
                ),
                shops,
            )
        ):
            shop_item_costs.extend(filter(lambda _: _.item == self, item.costs))
            checked_items.append(item)
        return list(unique_everseen(shop_item_costs))
