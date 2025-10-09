from typing import Iterable
from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet
from .gathering_condition import GatheringCondition
from .gathering_point_bonus_type import GatheringPointBonusType


@xivrow
class GatheringPointBonus(XivRow):

    @property
    def conditions(self) -> Iterable[GatheringCondition]:
        """
        A particular condition can have multiple 'tiers' of bonus
        if Unknown 1 > 0, the value in Unknown 2 is the upper bound for the bonus
        Example option: GatheringPointBonus#144:
           * If gathering > 3900, Yield + 1
           * If gathering > 4100, Yield + 3
        TODO: research how all this is calculated/if intermediate values exist like +2 in
        the example above
        """
        return [self.condition]

    @property
    def condition(self) -> "GatheringCondition":
        return self.as_T(GatheringCondition, "Condition")

    @property
    def condition_value(self) -> int:
        return self.as_int32("ConditionValue")

    @property
    def bonus_type(self) -> "GatheringPointBonusType":
        return self.as_T(GatheringPointBonusType, "BonusType")

    @property
    def bonus_value(self) -> int:
        return self.as_int32("BonusValue")

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(GatheringPointBonus, self).__init__(sheet, source_row)

    def __repr__(self):
        return f"GatheringPointBonus#{self.key}(Condition={self.condition})"
