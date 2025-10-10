from typing import Iterable, List, cast
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

    @property
    def is_ephemeral(self) -> bool:
        s = cast("GatheringPointTransient", self.spawn_times)
        return s.as_int32("EphemeralStartTime") < 65535

    @property
    def spawn_times(self) -> "GatheringPointTransient":
        if not self.__spawn_times_processed:
            self.__build_spawn_times()
        return self.__spawn_times

    @property
    def spawn_windows(self) -> Iterable[dict[str, str | int]]:
        NUM_POSSIBLE_WINDOWS = 3
        if self.is_ephemeral:
            # These start times come from the GatheringPointTransient itself
            return [
                {
                    "start": self.spawn_times["EphemeralStartTime"],
                    "end": self.spawn_times["EphemeralEndTime"],
                }
            ]
        else:
            # These times come from the GatheringRarePropTimeTable
            rp = self.spawn_times["GatheringRarePopTimeTable"]
            times = []
            if rp.key == 0:
                return times
            for i in range(NUM_POSSIBLE_WINDOWS):
                st = rp.as_int32("StartTime", i)
                if st < 65535:
                    o = {"start": st, "end": 0}
                    # for some reason, 2 hr nodes = 160 Duration, 3 hr nodes = 300
                    window_duration = 200 if rp.as_int32("Duration", i) == 160 else 300
                    o["end"] = st + window_duration
                    times.append(o)
            return times

        return []

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(GatheringPoint, self).__init__(sheet, source_row)
        self.__bonuses = None
        self.__spawn_times = None
        self.__spawn_times_processed = False

    def __build_gathering_point_bonus(self):
        COUNT = 2

        bonuses = []
        for i in range(COUNT):
            bonus = self.as_T(GatheringPointBonus, None, i)
            if bonus.key != 0:
                bonuses.append(bonus)

        return bonuses

    def __build_spawn_times(self):
        s = self.sheet.collection.get_sheet("GatheringPointTransient")
        if self.key in s:
            self.__spawn_times = s[self.key]

        self.__spawn_times_processed = True
