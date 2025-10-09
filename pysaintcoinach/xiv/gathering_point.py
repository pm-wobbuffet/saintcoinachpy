from typing import List
from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet
from .gathering_point_base import GatheringPointBase
from .territory_type import TerritoryType
from .placename import PlaceName
from .gathering_sub_category import GatheringSubCategory
from .gathering_point_bonus import GatheringPointBonus


@xivrow
class GatheringPoint(XivRow):

    @property
    def base(self) -> GatheringPointBase:
        return self.as_T(GatheringPointBase)

    @property
    def count(self) -> int:
        """The default integrity of a node, prior to bonuses"""
        return self.as_int32("Count")

    @property
    def territory_type(self) -> TerritoryType:
        return self.as_T(TerritoryType)

    @property
    def place_name(self) -> PlaceName:
        return self.as_T(PlaceName)

    @property
    def gathering_point_bonus(self) -> List["GatheringPointBonus"]:
        if self.__bonuses is None:
            self.__bonuses = self.__build_gathering_point_bonus()
        return self.__bonuses

    @property
    def gathering_sub_category(self) -> "GatheringSubCategory":
        return self.as_T(GatheringSubCategory)

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(GatheringPoint, self).__init__(sheet, source_row)
        self.__bonuses = None

    def __build_gathering_point_bonus(self):
        COUNT = 2

        bonuses = []
        for i in range(COUNT):
            bonus = self.as_T(GatheringPointBonus, None, i)
            if bonus.key != 0:
                bonuses.append(bonus)

        return bonuses
