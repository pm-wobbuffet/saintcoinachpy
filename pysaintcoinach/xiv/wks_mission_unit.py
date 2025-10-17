from typing import Iterable, List

from pysaintcoinach.text import XivString
from ..ex.relational import IRelationalRow
from . import xivrow, XivRow, IXivSheet
from .interfaces import IItemSource


@xivrow
class WKSMissionUnit(XivRow):

    @property
    def name(self) -> XivString:
        return self.as_string("Name")

    @property
    def text(self) -> XivString:
        return self["WKSMissionText"]["Text"]

    def __init__(self, sheet: IXivSheet, source_row: IRelationalRow):
        super().__init__(sheet, source_row)
