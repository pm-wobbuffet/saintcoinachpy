"""
Handles the item/currency conversions for Items in the SpecialShop Sheet
"""

from typing import Dict

from ...datasheet import IDataRow
from ..sheet import IRelationalRow
from ..valueconverter import IValueConverter
from ..excollection import ExCollection
from pathlib import Path
import os

try:
    _SCRIPT_PATH = os.path.abspath(__path__)
except:
    _SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))


class SpecialShopItemReferenceConverter(IValueConverter):
    from .... import xiv

    __tomestone_map = None
    __scrip_map = None
    __csv_map = None  # type: Dict[int, str] | None
    _t = None

    @property
    def target_type_name(self):
        return "Item"

    @property
    def target_type(self):
        return type(IRelationalRow)

    def __repr__(self):
        return "%s()" % (self.__class__.__name__)

    def convert(self, row: IDataRow, raw_value: object):
        if self.__csv_map is None:
            self._load_csv_mappings()
        if self.__tomestone_map is None:
            self.__tomestone_map = self._build_tomestone_mapping(row.sheet.collection)
        if self.__scrip_map is None:
            self.__scrip_map = self._build_scrip_mapping(row.sheet.collection)

        key = int(raw_value)
        use_map = self._detect_target_mapping(row, raw_value)
        if key in use_map:
            return use_map[key]

        items = row.sheet.collection.get_sheet("Item")
        return items[key] if key in items else raw_value

    def _load_csv_mappings(self):
        import csv

        p = Path(_SCRIPT_PATH, "../../../..", "schema_overrides", "SpecialShop.csv")
        self.__csv_map = {}
        if p.exists():
            with open(p, mode="r") as f:
                csvfile = csv.reader(f)
                next(csvfile)  # skipping header row
                for line in csvfile:
                    self.__csv_map[int(line[0])] = line[2]

    def _detect_target_mapping(self, row: IDataRow, raw_value: object):
        """Try to be clever and figure out the proper target
        The UseCurrency column value appears to be mostly useless"""
        # Is there a pre-existing known mapping for this, stored in SpecialShop.csv?
        shop_key = int(row.key)
        if shop_key in self.__csv_map:
            r = self.__csv_map[shop_key]
            if r == "tome":
                return self.__tomestone_map
            elif r == "scrip":
                return self.__scrip_map
            elif r == "item":
                return {}

        if (int(raw_value)) == 1:
            # 1 is always used for Tomestone shops. Gil shops have their own Sheet
            return self.__tomestone_map
        if any(
            sub in str(row["Name"]).lower()
            for sub in ["crafter", "gatherer", "scrip exchange"]
        ):
            return self.__scrip_map

        # Take a peek at the first thing for sale and see if it's associated with
        # a crafter/gatherer
        if int(row[1]["ItemUICategory"].key) in range(12, 33):
            return self.__scrip_map
        # See if the gear has Craft/Control/CP/Gathering/Perception/GP
        if int(row[1]["BaseParam[0]"].key in [70, 71, 72, 73, 10, 11]):
            return self.__scrip_map

        # Fallback, if the value is less than 10, it's going to be one of the special
        # currency types, might as well just guess Tomestones
        if int(raw_value) < 10:
            return self.__tomestone_map
        return {}

    def _build_tomestone_mapping(self, coll: ExCollection):
        index = {}  # type: 'Dict[int, xiv.IXivRow]'

        sheet = coll.get_sheet("TomestonesItem")
        # Column 2 ("Tomestones" in EXDSchema) contains the int used
        # to represent a particular tomestone in special shops, etc
        for row in sheet:
            reward_index = int(row.get_raw(2))
            if reward_index > 0:
                index[reward_index] = row["Item"]

        return index

    def _build_scrip_mapping(self, coll: ExCollection):
        """
        Build a list of scrip rewards. Unlike Tomestones, there does not appear
        to be a client-side sheet that contains these references.
        Need to build it ourselves, either via hard coding, or best guess
        index values:
        - 1: obsolete crafters' scrip
        - 2: lower tier crafters' scrip
        - 3: obsolete gatherers' scrip
        - 4: lower tier gatherers' scrip
        - 6: endgame crafters' scrip
        - 7: endgame gatherers' scrip

        """
        sheet = coll.get_sheet("Item")
        index = {
            2: sheet[33913],
            4: sheet[33914],
            6: sheet[41784],
            7: sheet[41785],
        }
        return index
        # This ended up being stupidly slow, will come back to it.
        # sheet = coll.get_sheet("Item")
        # # Get the first four items that have "gatherer/crafters' scrip" in their name
        # # in reverse key id order, assuming they'll keep adding new currency at the end
        # # of the items sheet as expansions go on.
        # scrip_items = sorted(
        #     filter(
        #         lambda row: row.key > 0
        #         and (
        #             "gatherers' scrip" in str(row["Name"]).lower()
        #             or "crafters' scrip" in str(row["Name"]).lower()
        #         ),
        #         sheet,
        #     ),
        #     key=lambda x: int(x.key),
        #     reverse=True,
        # )[0:4]

        # for i, itemshell in enumerate(scrip_items):
        #     if "gatherer" in str(itemshell["Name"]).lower():
        #         if i < 2:
        #             # endgame scrip
        #             index[7] = itemshell
        #         else:
        #             # leveling scrip
        #             index[4] = itemshell
        #     elif "crafter" in str(itemshell["Name"]).lower():
        #         if i < 2:
        #             index[6] = itemshell
        #         else:
        #             index[2] = itemshell
        # return index
