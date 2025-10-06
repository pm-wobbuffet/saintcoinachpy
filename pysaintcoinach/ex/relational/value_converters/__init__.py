from typing import List, Dict
import json
from collections import OrderedDict

from ...datasheet import IDataRow
from ..sheet import IRelationalRow
from ..valueconverter import IValueConverter
from ..excollection import ExCollection
from .complexlinkconverter import ComplexLinkConverter
from ..definition import SheetDefinition
from ..definition.exdschema import SchemaField


class ColorConverter(IValueConverter):
    @property
    def includes_alpha(self) -> bool:
        return self.__includes_alpha

    @includes_alpha.setter
    def includes_alpha(self, value):
        self.__includes_alpha = value

    @property
    def target_type_name(self):
        return "Color"

    @property
    def target_type(self):
        return type(int)

    def __init__(self):
        self.__includes_alpha = False

    def __repr__(self):
        return "%s(IncludesAlpha=%r)" % (self.__class__.__name__, self.includes_alpha)

    def convert(self, row: IDataRow, raw_value: object):
        argb = raw_value  # type: int
        if not self.includes_alpha:
            argb = argb | 0xFF000000

        return argb

    def to_json(self):
        obj = OrderedDict()
        obj["type"] = "color"
        return obj

    @staticmethod
    def from_json(obj: dict):
        return ColorConverter()

    def resolve_references(self, sheet_def: SheetDefinition):
        return


class GenericReferenceConverter(IValueConverter):
    @property
    def target_type_name(self):
        return "Row"

    @property
    def target_type(self):
        return type(IRelationalRow)

    def __repr__(self):
        return "%s()" % (self.__class__.__name__)

    def convert(self, row: IDataRow, raw_value: object):
        coll = row.sheet.collection
        key = int(raw_value)
        return coll.find_reference(key)

    def to_json(self):
        obj = OrderedDict()
        obj["type"] = "generic"
        return obj

    @staticmethod
    def from_json(obj: dict):
        return GenericReferenceConverter()

    def resolve_references(self, sheet_def: SheetDefinition):
        return


class IconConverter(IValueConverter):
    @property
    def target_type_name(self):
        return "Image"

    @property
    def target_type(self):
        return type(object)

    def __repr__(self):
        return "%s()" % (self.__class__.__name__)

    def convert(self, row: IDataRow, raw_value: object):
        from .... import imaging

        nr = int(raw_value)
        if nr <= 0 or nr > 999999:
            return None

        sheet = row.sheet
        return imaging.IconHelper.get_icon(
            sheet.collection.pack_collection, nr, sheet.language
        )

    def to_json(self):
        obj = OrderedDict()
        obj["type"] = "icon"
        return obj

    @staticmethod
    def from_json(obj: dict):
        return IconConverter()

    def resolve_references(self, sheet_def: SheetDefinition):
        return


class MultiReferenceConverter(IValueConverter):
    @property
    def targets(self) -> List[str]:
        return self.__targets

    @targets.setter
    def targets(self, value):
        self.__targets = value

    @property
    def target_type_name(self):
        return "Row"

    @property
    def target_type(self):
        return type(IRelationalRow)

    def __repr__(self):
        return "%s(Targets=%r)" % (self.__class__.__name__, self.targets)

    def convert(self, row: IDataRow, raw_value: object):
        key = int(raw_value)
        if self.targets is None:
            return None

        for target in self.targets:
            sheet = row.sheet.collection.get_sheet(target)
            if not any(filter(lambda r: key in r, sheet.header.data_file_ranges)):
                continue
            if key in sheet:
                return sheet[key]
        return None

    def to_json(self):
        obj = OrderedDict()
        obj["type"] = "multiref"
        obj["targets"] = self.targets or []
        return obj

    @staticmethod
    def from_json(obj: dict):
        converter = MultiReferenceConverter()
        converter.targets = [str(t) for t in obj.get("targets", [])]
        return converter

    @staticmethod
    def from_yaml(obj: SchemaField):
        converter = MultiReferenceConverter()
        converter.targets = [str(t) for t in obj.targets]
        return converter

    def resolve_references(self, sheet_def: SheetDefinition):
        return


class QuadConverter(IValueConverter):
    @property
    def target_type_name(self):
        return "Quad"

    @property
    def target_type(self):
        return type(int)

    def convert(self, row: IDataRow, raw_value: object):
        return int(raw_value)

    def to_json(self):
        obj = OrderedDict()
        obj["type"] = "quad"
        return obj

    @staticmethod
    def from_json(obj: object):
        return QuadConverter()

    def resolve_references(self, sheet_def: SheetDefinition):
        return


class SheetLinkConverter(IValueConverter):
    @property
    def target_sheet(self) -> str:
        return self.__target_sheet

    @target_sheet.setter
    def target_sheet(self, value):
        self.__target_sheet = value

    @property
    def target_type_name(self):
        return self.target_sheet

    @property
    def target_type(self):
        return type(IRelationalRow)

    def __repr__(self):
        return "%s(TargetSheet=%r)" % (self.__class__.__name__, self.target_sheet)

    def convert(self, row: IDataRow, raw_value: object):
        coll = row.sheet.collection
        if not coll.sheet_exists(self.target_sheet):
            return None

        sheet = coll.get_sheet(self.target_sheet)

        key = int(raw_value)
        return sheet[key] if key in sheet else None

    def to_json(self):
        obj = OrderedDict()
        obj["type"] = "link"
        obj["target"] = self.target_sheet
        return obj

    @staticmethod
    def from_json(obj: dict):
        converter = SheetLinkConverter()
        converter.target_sheet = obj.get("target", None)
        return converter

    @staticmethod
    def from_yaml(obj: SchemaField):
        converter = SheetLinkConverter()
        converter.target_sheet = obj.targets[0]
        return converter

    def resolve_references(self, sheet_def: SheetDefinition):
        return


class SpecialShopItemReferenceConverter(IValueConverter):
    from .... import xiv

    __tomestone_map = None
    __scrip_map = None

    @property
    def target_type_name(self):
        return "Item"

    @property
    def target_type(self):
        return type(IRelationalRow)

    def __repr__(self):
        return "%s()" % (self.__class__.__name__)

    def convert(self, row: IDataRow, raw_value: object):
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

    def _detect_target_mapping(self, row: IDataRow, raw_value: object):
        """Try to be clever and figure out the proper target
        The UseCurrency column value appears to be mostly useless"""

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


class TomestoneOrItemReferenceConverter(IValueConverter):
    from .... import xiv

    __tomestone_key_by_reward_index = None  # type: Dict[int, xiv.IXivRow]

    @property
    def target_type_name(self):
        return "Item"

    @property
    def target_type(self):
        return type(IRelationalRow)

    def __repr__(self):
        return "%s()" % (self.__class__.__name__)

    def convert(self, row: IDataRow, raw_value: object):
        if self.__tomestone_key_by_reward_index is None:
            self.__tomestone_key_by_reward_index = self._build_tomestone_reward_index(
                row.sheet.collection
            )

        key = int(raw_value)
        if key in self.__tomestone_key_by_reward_index:
            return self.__tomestone_key_by_reward_index[key]

        items = row.sheet.collection.get_sheet("Item")
        return items[key] if key in items else raw_value

    def _build_tomestone_reward_index(
        self, coll: ExCollection
    ) -> Dict[int, "xiv.IXivRow"]:
        index = {}  # type: 'Dict[int, xiv.IXivRow]'

        sheet = coll.get_sheet("TomestonesItem")
        for row in sheet:
            reward_index = int(row.get_raw(2))  # For compatibility only
            if reward_index > 0:
                index[reward_index] = row["Item"]

        return index

    def to_json(self):
        obj = OrderedDict()
        obj["type"] = "tomestone"
        return obj

    @staticmethod
    def from_json(obj: dict):
        return TomestoneOrItemReferenceConverter()

    def resolve_references(self, sheet_def: SheetDefinition):
        return
