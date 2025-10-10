from typing import Iterable, List
from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet
from .interfaces import IItemSource
from .gathering_type import GatheringType


@xivrow
class GatheringPointBase(XivRow, IItemSource):

    @property
    def type(self) -> GatheringType:
        return self.as_T(GatheringType)

    @property
    def exported_point(self):
        if self.__exported_point is None:
            s = self.sheet.collection.get_sheet("ExportedGatheringPoint")
            if self.key in s:
                self.__exported_point = s[self.key]
        return self.__exported_point

    @property
    def gathering_level(self) -> int:
        return self.as_int32("GatheringLevel")

    @property
    def points(self):
        if self.__points is None:
            self.__build_points()
        return self.__points

    @property
    def _items(self):
        """The list of all item slots on this node, possibly containing None values
        for blank rows"""
        if self.__items is None:
            self.__items = self.__build_items()
        return self.__items

    # @property
    # def is_limited(self) -> bool:
    #     return self.as_boolean("IsLimited")
    # This no longer seems to exist on that sheet

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(GatheringPointBase, self).__init__(sheet, source_row)
        self.__items = None
        self.__item_source_items = None  # type: None|List["Item"]
        self.__points = None  # type: None|Iterable["GatheringPoint"]
        self.__exported_point = None

    def __build_points(self):
        from .gathering_point import GatheringPoint

        self.__points = list(
            filter(
                lambda x: x["GatheringPointBase"] == self,
                self.sheet.collection.get_sheet(GatheringPoint),
            )
        )

    def __build_items(self):
        from .gathering_item_base import GatheringItemBase

        COUNT = 8

        items = []
        for i in range(COUNT):
            gib: GatheringItemBase = self[("Item", i)]
            if (
                gib is not None
                and gib.key != 0
                and gib.item is not None
                and gib.item.key != 0
            ):
                items.append(gib)
            else:
                items.append(None)
        return items

    @property
    def items(self) -> Iterable["Item"]:  # type: ignore
        """The list of all items obtainable from this gathering point base"""
        if self.__item_source_items is None:
            self.__item_source_items = list(
                map(lambda i: i.item, filter(None, self._items))
            )
        return self.__item_source_items
