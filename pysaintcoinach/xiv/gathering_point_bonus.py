import math
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
        # Start with the base condition, which we always know is true
        s = [self.condition]
        if (
            self.condition_upper_value == 0
            or self.bonus_upper_value == 0
            or self.condition_value == self.condition_upper_value
        ):
            return s
        midpt = math.floor(
            (self.condition_upper_value - self.condition_value) / 2
            + self.condition_value
        )
        midpt_bonus = math.floor(
            (self.bonus_upper_value - self.bonus_value) / 2 + self.bonus_value
        )
        if midpt_bonus > self.bonus_value:
            # There's a middle step value
            pass

        return s

    @property
    def condition(self) -> "GatheringCondition":
        gc = self.as_T(GatheringCondition, "Condition")
        gc.format(self)
        return gc

    @property
    def condition_value(self) -> int:
        return self.as_int32("ConditionValue")

    @property
    def condition_upper_value(self) -> int:
        return self.as_int32("Unknown1")

    @property
    def bonus_type(self) -> "GatheringPointBonusType":
        return self.as_T(GatheringPointBonusType, "BonusType")

    @property
    def bonus_value(self) -> int:
        return self.as_int32("BonusValue")

    @property
    def bonus_upper_value(self) -> int:
        return self.as_int32("Unknown2")

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(GatheringPointBonus, self).__init__(sheet, source_row)

    def __repr__(self):
        return f"GatheringPointBonus#{self.key}(Condition={self.condition})"
