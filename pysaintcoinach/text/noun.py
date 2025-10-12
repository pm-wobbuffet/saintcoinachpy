"""
Handles the processing and generation of Noun elements in varying languages

The Attributive sheet is used to map properties of a string onto language-specific replacements
for placeholders like [a], [t], etc. in an XivString
https://github.com/goatcorp/Dalamud/blob/master/Dalamud/Game/Text/Noun/NounProcessor.cs

Placeholders:
    [t] = article or grammatical gender (EN: the, DE: der, die, das)
    [n] = amount (number)
    [a] = declension
    [p] = plural
    [pa] = ?

"""


class NounParameters:

    @property
    def column_offset(self) -> int:
        """
        The column offset that marks the beginning of the Noun attribute columns (Singular field).
        """
        if self._sheet_name in [
            "BeastTribe",
            "DeepDungeonItem",
            "DeepDungeonEquipment",
            "DeepDungeonMagicStone",
            "DeepDungeonDemiclone",
        ]:
            return 1
        elif self._sheet_name == "Glasses":
            return 4
        elif self._sheet_name == "GlassesStyle":
            return 15
        return 0

    def __init__(self) -> None:
        self._language = None
        self._sheet_name = None
        self._row_id = None
        self._quantity = 1
        self._article_type = None
        self._grammatical_case = None
        self._is_action_sheet = False
        pass


class Noun:

    def __init__(self) -> None:
        pass
