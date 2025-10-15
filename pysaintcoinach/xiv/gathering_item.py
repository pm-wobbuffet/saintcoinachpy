from typing import cast
from ..ex.relational import IRelationalRow
from . import xivrow, IXivSheet
from .gathering_item_base import GatheringItemBase


@xivrow
class GatheringItem(GatheringItemBase):

    @property
    def gathering_item_level(self) -> "GatheringItemLevelConvertTable":
        return self.as_T("GatheringItemLevelConvertTable", "GatheringItemLevel")

    @property
    def gathering_level_string(self) -> str:
        """A string representation of an item's Level (i.e. 100**)"""
        return (
            f"{self.gathering_item_level["GatheringItemLevel"]}"
            + f"{'*' * int(self.gathering_item_level["Stars"])}"
        )

    @property
    def is_hidden(self) -> bool:
        return self.as_boolean("IsHidden")

    @property
    def item(self) -> "Item":
        return self.as_T("Item", "Item")

    @property
    def points(self):
        if self.__points is None:
            self._generate_points()
        return self.__points

    @property
    def required_perception(self) -> int:
        return self.as_int32("PerceptionReq")

    @property
    def required_quest(self) -> "Quest":
        """The required quest before an item will show up on nodes"""
        return self.as_T("Quest", "Unknown0")

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(GatheringItem, self).__init__(sheet, source_row)
        self.__points = None

    def _generate_points(self) -> None:
        s = self.sheet.collection.get_sheet("GatheringItemPoint")
        ret = []
        for row in filter(lambda x: x.parent_row.key == self.key, s):
            ret.append(row["GatheringPoint"])
        self.__points = ret
