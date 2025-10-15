from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet, IXivRow
from .. import text
from ..imaging import ImageFile
from typing import cast


@xivrow
class CraftAction(XivRow):

    @property
    def name(self) -> str:
        return str(self.as_string("Name"))

    @property
    def description(self) -> str:
        return str(self.as_string("Description"))

    @property
    def icon(self) -> ImageFile:
        return self.as_image("Icon")

    @property
    def class_job(self):
        return self.as_T("ClassJob", "ClassJob")

    @property
    def class_job_category(self):
        return self.as_T("ClassJobCategory", "ClassJobCategory")

    @property
    def cost(self):
        return self.as_int16("Cost")

    @property
    def required_level(self) -> int:
        return self.as_int16("ClassJobLevel")

    @property
    def specialist_action(self) -> bool:
        return self.as_boolean("Specialist")

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super().__init__(sheet, source_row)
