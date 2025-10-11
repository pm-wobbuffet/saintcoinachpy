from enum import Enum
from typing import Iterable, List, cast

from ..text import XivString
from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet
from .notorious_monster import NotoriousMonsterRank, NotoriousMonster
from .territory_type import TerritoryType


@xivrow
class NotoriousMonsterTerritory(XivRow):
    """A listing of all the notorious monsters in a given Territory"""

    MOB_COUNT = 10  # Number of mob columns in the sheet

    @property
    def mobs(self) -> Iterable[NotoriousMonster]:
        if not self.__mobs_processed:
            self.__collect_mobs()

        return self.__mobs

    @property
    def has_double_s(self) -> bool:
        """
        Whether this zone has a SS rank mob event attached to it
        Kind of simple logic, just looks to see if there is a mob assigned to the
        final column, if so it contains more than the standard 1 B + 2 A + 1 S

        Would need to re-evaluate this logic if their layout changes
        """
        return self["NotoriousMonsters[9]"].key > 0

    @property
    def territory(self) -> TerritoryType:
        """The underlying territory that this NMTerritory is assigned to"""
        t = self.sheet.collection.get_sheet("TerritoryType")
        return cast(
            TerritoryType, t.indexed_lookup("NotoriousMonsterTerritory", self.key)
        )

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super().__init__(sheet, source_row)
        self.__mobs = []
        self.__mobs_processed = False

    def __collect_mobs(self) -> None:

        for i in range(self.MOB_COUNT):
            mob = self.as_T(NotoriousMonster, "NotoriousMonsters", i)
            if mob.key != 0:
                self.__mobs.append(mob)
        self.__mobs_processed = True
