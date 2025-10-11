from enum import Enum
from typing import Iterable, List, cast

from ..text import XivString
from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet


class NotoriousMonsterRank(Enum):
    """Friendly name mapping for monster ranks"""

    B = 1
    A = 2
    S = 3
    MINION = 4
    SS = 5


@xivrow
class NotoriousMonster(XivRow):
    """
    An A, S, or B rank notorious monster mob
    """

    @property
    def rank(self) -> NotoriousMonsterRank:
        return NotoriousMonsterRank(self.as_int16("Rank"))

    @property
    def numeric_rank(self) -> int:
        return self.as_int16("Rank")

    @property
    def bnpc_base(self) -> "BNpcBase":
        return self.as_T("BNpcBase", "BNpcBase")

    @property
    def name(self) -> XivString:
        return self.as_string("BNpcName")

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super().__init__(sheet, source_row)

    def __repr__(self):
        return f"{self.__class__.__name__}#{self.key}(Name={self.name}, Rank={self.rank.name})"
