from typing import Iterable, List
from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet
from .interfaces import IItemSource
from .gathering_type import GatheringType


@xivrow
class GatheringPointBase(XivRow, IItemSource):
    """The base gathering point data from which a GatheringPoint instance derives
    The GatheringPointBase contains all the items on this particular node type, along with
    the GatheringType of the node, indicating which job and tool is required to access it
    """

    @property
    def type(self) -> GatheringType:
        """The gathering type of this point (Harvesting, Logging, Mining, Quarrying)
        indicating which job and tool type is used for accessing the point"""
        return self.as_T(GatheringType)

    @property
    def exported_point(self):
        """The coordinate mapping for this gathering point, stored
        in the ExportedGatheringPoint sheet"""
        if self.__exported_point is None:
            s = self.sheet.collection.get_sheet("ExportedGatheringPoint")
            if self.key in s:
                self.__exported_point = s[self.key]
        return self.__exported_point

    @property
    def job(self):
        """
        The shorthand abbreviation for what job this gathering point base
        corresponds to
        """
        if self.key == 0 or self.key == 1:
            return "MIN"
        elif self.key == 2 or self.key == 3:
            return "BTN"
        return "FSH"

    @property
    def gathering_level(self) -> int:
        """The level of the node as seen in the overworld (i.e. Level 50 Mining Node)"""
        return self.as_int32("GatheringLevel")

    @property
    def points(self):
        """A collection of GatheringPoints that are derived from this base"""
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
        """Generate a list of all gathering points that are derived from this base"""
        from .gathering_point import GatheringPoint

        self.__points = list(
            filter(
                lambda x: x["GatheringPointBase"] == self,
                self.sheet.collection.get_sheet(GatheringPoint),
            )
        )

    def __build_items(self):
        """Build the collection of items obtainable from this node"""
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
