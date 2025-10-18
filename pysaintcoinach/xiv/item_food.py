from typing import Iterable
from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet


class ItemFoodParameter:

    @property
    def base_param(self):
        return self.__base_param

    @property
    def max(self):
        return self.__max

    @property
    def max_hq(self):
        return self.__max_hq

    @property
    def value(self):
        return self.__value

    @property
    def value_hq(self):
        return self.__value_hq

    @property
    def is_relative(self) -> bool:
        return self.__is_relative

    @property
    def hq(self) -> str:
        """Return a string representing the values given by the food in HQ form"""
        ret = ""
        ret += f"{self.base_param} +{self.value_hq}{'%' if self.is_relative else ''}"
        if self.is_relative:
            ret += f" (Max {self.max_hq})"
        return ret

    @property
    def nq(self) -> str:
        """Return a string representing the values given by the food in HQ form"""
        ret = ""
        ret += f"{self.base_param} +{self.value}{'%' if self.is_relative else ''}"
        if self.is_relative:
            ret += f" (Max {self.max})"
        return ret

    def __init__(self, base_param, is_relative, value, max, value_hq, max_hq) -> None:
        self.__base_param = base_param
        self.__is_relative = is_relative
        self.__value = value
        self.__max = max
        self.__value_hq = value_hq
        self.__max_hq = max_hq

    def __repr__(self) -> str:
        return f"NQ:{self.nq}, HQ:{self.hq}"

    def __str__(self) -> str:
        return self.__repr__()


@xivrow
class ItemFood(XivRow):
    """A Row representing the stat augments or buffs applied by a given Food item"""

    NUM_PARAMS = 3

    @property
    def exp(self) -> str:
        """The experience point percentage gain supplied by consuming this food"""
        return f"{self.as_int32('EXPBonusPercent')}%"

    @property
    def params(self) -> Iterable[ItemFoodParameter]:
        """The List of stats affected by this buff"""
        if self.__params is None or len(self.__params) < 1:
            self._build_params()
        return self.__params

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super().__init__(sheet, source_row)
        self.__params = []

    def _build_params(self):
        for i in range(self.NUM_PARAMS):
            bparam = self.as_T("BaseParam", "BaseParam", i)
            if bparam.key >= 0 and str(bparam) != "":
                self.__params.append(
                    ItemFoodParameter(
                        bparam,
                        self.as_boolean("IsRelative", i),
                        self.as_int16("Value", i),
                        self.as_int16("Max", i),
                        self.as_int16("ValueHQ", i),
                        self.as_int16("MaxHQ", i),
                    )
                )
