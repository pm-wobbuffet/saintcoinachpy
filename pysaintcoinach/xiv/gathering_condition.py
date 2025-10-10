from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet
from .. import text


@xivrow
class GatheringCondition(XivRow):

    @property
    def text(self) -> text.XivString:
        return self.as_string("Text")

    def format(self, parent_bonus: "GatheringPointBonus") -> str:
        if self.__formatted_str is None:
            self.__formatted_str = (
                str(self.text)
                .replace(
                    "<Value(IntegerParameter(1))/>", str(parent_bonus.condition_value)
                )
                .replace("<num(lnum1)>", str(parent_bonus.condition_value))
            )
        return self.__formatted_str

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super(GatheringCondition, self).__init__(sheet, source_row)
        self.__formatted_str = None

    def __str__(self):
        return str(self.__formatted_str)
