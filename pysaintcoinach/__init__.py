from pathlib import Path
import json
import os
import logging
import yaml

try:
    _SCRIPT_PATH = os.path.abspath(__path__)
except:
    _SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

_SAINTCOINACH_HOME = Path(_SCRIPT_PATH, "..", "SaintCoinach", "SaintCoinach")
_EXDSCHEMA_HOME = Path(_SCRIPT_PATH, "..", "EXDSchema")

from .ex import Language
from .ex.relational.definition.exdschema import SchemaSheet
from .ex.relational.definition import RelationDefinition, SheetDefinition
from .xiv import XivCollection
from .pack import PackCollection
from .indexfile import Directory
from .file import File


__all__ = ["ARealmReversed"]


class ARealmReversed(object):
    """
    Central class for accessing game assets.
    """

    """File name containing the current version string."""
    _VERSION_FILE = "ffxivgame.ver"

    @property
    def game_directory(self):
        return self._game_directory

    @property
    def packs(self):
        return self._packs

    @property
    def game_data(self):
        return self._game_data

    @property
    def game_version(self):
        return self._game_version

    @property
    def definition_version(self):
        return self.game_data.definition.version

    @property
    def is_current_version(self):
        return self.game_version == self.definition_version

    def __init__(self, game_path: str, language: Language):
        self._game_directory = Path(game_path)
        self._packs = PackCollection(self._game_directory.joinpath("game", "sqpack"))
        self._game_data = XivCollection(self._packs)
        self._game_data.active_language = language

        self._game_version = self._game_directory.joinpath(
            "game", "ffxivgame.ver"
        ).read_text()
        self._game_data.definition = self.__read_definition()

        self._game_data.definition.compile()

    def __read_definition(self) -> RelationDefinition:
        version = self._game_version
        _def = RelationDefinition(version=version)
        for sheet_file_name in _EXDSCHEMA_HOME.glob("*.yml"):
            _yml = sheet_file_name.read_text()
            try:
                obj = yaml.safe_load(_yml)
                obj = self.__process_overrides(obj)
                sheet = SchemaSheet(
                    obj.get("name", ""),
                    obj.get("displayField", ""),
                    obj.get("fields", []),
                    obj.get("relations", []),
                )
                sheet_def = SheetDefinition.from_yaml(sheet)
                _def.sheet_definitions.append(sheet_def)
            except yaml.YAMLError as exc:
                logging.error("Failed to decode %s: %s", sheet_file_name, str(exc))

        return _def

    def __process_overrides(self, obj):
        from pprint import pp

        sheet_name = obj.get("name", "")
        override_file_name = Path(
            _SCRIPT_PATH, "..", "schema_overrides", f"{sheet_name}.yml"
        )
        replacements = {}
        if override_file_name.exists():
            over_yml = yaml.safe_load(override_file_name.read_text())
            for field in over_yml.get("replacements", []):
                replacements[field.get("source")] = field

            obj["fields"] = self.__do_replacements(obj.get("fields", []), replacements)

        return obj

    def __do_replacements(self, fields, replacements, parent=""):
        for i, field in enumerate(fields):
            n = field.get("name", "")
            if n in replacements or f"{parent}*" in replacements:
                rep_data = replacements[n or f"{parent}*"]
                if "add_keys" in rep_data:
                    for prop in rep_data["add_keys"]:
                        field.update(prop)

            if field.get("fields") is not None:
                self.__do_replacements(
                    field.get("fields"), replacements, field.get("name", "")
                )
        return fields


# This is an example of how to use this library.
# XIV = ARealmReversed(r"C:\Program Files (x86)\SquareEnix\FINAL FANTASY XIV - A Realm Reborn",
#                      Language.english)


def get_default_xiv():
    from . import text

    _string_decoder = text.XivStringDecoder.default()

    # Override the tag decoder for emphasis so it doesn't produce tags in string...
    def omit_tag_decoder(i, t, l):
        text.XivStringDecoder.get_integer(i)
        return text.nodes.StaticString("")

    _string_decoder.set_decoder(text.TagType.Emphasis.value, omit_tag_decoder)
    _string_decoder.set_decoder(
        text.TagType.SoftHyphen.value,
        lambda i, t, l: text.nodes.StaticString(_string_decoder.dash),
    )

    return ARealmReversed(
        r"C:\Program Files (x86)\SquareEnix\FINAL FANTASY XIV - A Realm Reborn",
        Language.english,
    )
