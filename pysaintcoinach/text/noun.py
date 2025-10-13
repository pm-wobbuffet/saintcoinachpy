"""
Handles the processing and generation of Noun elements in varying languages

The Attributive sheet is used to map properties of a string onto language-specific replacements
for placeholders like [a], [t], etc. in an XivString
https://github.com/goatcorp/Dalamud/blob/master/Dalamud/Game/Text/Noun/NounProcessor.cs
Mostly based off this code. Note that, especially in French, many of the variables
do not have descriptive names

Placeholders:
    [t] = article or grammatical gender (EN: the, DE: der, die, das)
    [n] = amount (number)
    [a] = declension
    [p] = plural
    [pa] = ?

"""

from enum import Enum
from .article_types import (
    EnglishArticleType,
    FrenchArticleType,
    GermanArticleType,
    JapaneseArticleType,
)
from ..xiv.sheet import XivRow
from ..ex.language import Language


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

    @property
    def grammatical_case(self):
        return self._grammatical_case

    @property
    def article_type(self):
        return self._article_type

    @property
    def is_action_sheet(self) -> bool:
        return self._is_action_sheet

    @property
    def language(self) -> Language:
        return self._language

    @property
    def quantity(self) -> int:
        return self._quantity

    def __init__(
        self,
        language: Language,
        sheet_name: str,
        row_id: int,
        quantity: int,
        article_type: Enum,
        grammatical_case,
        is_action_sheet: bool,
    ) -> None:
        self._language = language
        self._sheet_name = sheet_name
        self._row_id = row_id
        self._quantity = quantity
        self._article_type = article_type
        self._grammatical_case = grammatical_case
        self._is_action_sheet = is_action_sheet


"""
Attributive sheet:
  Japanese:
    Unknown0 = Singular Demonstrative
    Unknown1 = Plural Demonstrative
  English:
    Unknown2 = Article before a singular noun beginning with a consonant sound
    Unknown3 = Article before a generic noun beginning with a consonant sound
    Unknown4 = N/A
    Unknown5 = Article before a singular noun beginning with a vowel sound
    Unknown6 = Article before a generic noun beginning with a vowel sound
    Unknown7 = N/A
  German:
    Unknown8 = Nominative Masculine
    Unknown9 = Nominative Feminine
    Unknown10 = Nominative Neutral
    Unknown11 = Nominative Plural
    Unknown12 = Genitive Masculine
    Unknown13 = Genitive Feminine
    Unknown14 = Genitive Neutral
    Unknown15 = Genitive Plural
    Unknown16 = Dative Masculine
    Unknown17 = Dative Feminine
    Unknown18 = Dative Neutral
    Unknown19 = Dative Plural
    Unknown20 = Accusative Masculine
    Unknown21 = Accusative Feminine
    Unknown22 = Accusative Neutral
    Unknown23 = Accusative Plural
  French (unsure):
    Unknown24 = Singular Article
    Unknown25 = Singular Masculine Article
    Unknown26 = Plural Masculine Article
    Unknown27 = ?
    Unknown28 = ?
    Unknown29 = Singular Masculine/Feminine Article, before a noun beginning in a vowel or an h
    Unknown30 = Plural Masculine/Feminine Article, before a noun beginning in a vowel or an h
    Unknown31 = ?
    Unknown32 = ?
    Unknown33 = Singular Feminine Article
    Unknown34 = Plural Feminine Article
    Unknown35 = ?
    Unknown36 = ?
    Unknown37 = Singular Masculine/Feminine Article, before a noun beginning in a vowel or an h
    Unknown38 = Plural Masculine/Feminine Article, before a noun beginning in a vowel or an h
    Unknown39 = ?
    Unknown40 = ?
"""


class Noun:
    SINGULAR_COLUMN_IDX = 0
    ADJECTIVE_COLUMN_IDX = 1
    PLURAL_COLUMN_IDX = 2
    POSS_PRONOUN_COLUMN_IDX = 3
    STARTS_WITH_VOWEL_COLUMN_IDX = 4
    UNKNOWN5_COL_IDX = 5
    PRONOUN_COLUMN_IDX = 6
    ARTICLE_COLUMN_IDX = 7

    def __init__(self, parameters: NounParameters, row: XivRow) -> None:
        self._parameters = parameters
        self._row = row

    def process(self):
        if (
            self._parameters.grammatical_case < 0
            or self._parameters.grammatical_case > 5
        ):
            return self._row["Singular"]
        match self._parameters.language:
            case Language.english:
                return self.resolve_noun_en()
            case Language.french:
                return self.resolve_noun_fr()
            case Language.german:
                return self.resolve_noun_de()
            case Language.japanese:
                return self.resolve_noun_ja()
            case _:
                return self._row["Singular"]

    def resolve_noun_de(self):
        """
        a1->Offsets[0] = SingularColumnIdx
        a1->Offsets[1] = PluralColumnIdx
        a1->Offsets[2] = PronounColumnIdx
        a1->Offsets[3] = AdjectiveColumnIdx
        a1->Offsets[4] = PossessivePronounColumnIdx
        a1->Offsets[5] = Unknown5ColumnIdx
        a1->Offsets[6] = ArticleColumnIdx
        """
        sheet = self._row.sheet
        coll = sheet.collection
        attrib_sheet = coll.get_sheet("Attributive")

        if self._parameters.is_action_sheet:
            pass

        gender_idx_col = self._parameters.column_offset + self.PRONOUN_COLUMN_IDX
        gender_idx = self._row.get_raw(gender_idx_col)

        article_idx_col = self._parameters.column_offset + self.ARTICLE_COLUMN_IDX
        article_idx = self._row.get_raw(article_idx_col)

        case_column_offset = (4 * self._parameters.grammatical_case) + 8
        case_row_offset_column = self._parameters.column_offset + (
            self.ADJECTIVE_COLUMN_IDX
            if self._parameters.quantity == 1
            else self.POSS_PRONOUN_COLUMN_IDX
        )
        case_row_offset = (
            self._row.get_raw(case_row_offset_column)
            if case_row_offset_column >= 0
            else 0
        )

        if self._parameters.quantity != 1:
            gender_idx = 3

        text = self._row.get_raw(
            self._parameters.column_offset
            + (
                self.SINGULAR_COLUMN_IDX
                if self._parameters.quantity == 1
                else self.PLURAL_COLUMN_IDX
            )
        )
        output = ""
        if "[t]" not in text and article_idx == 0:
            grammatical_gender = attrib_sheet[
                self._parameters.article_type.value
            ].get_raw(case_column_offset + gender_idx)
            if str(grammatical_gender) != "":
                output += str(grammatical_gender)
        output += text
        if "[t]" in output:
            article = attrib_sheet[39].get_raw(case_column_offset + gender_idx)
            output = output.replace("[t]", str(article))

        plural = str(
            attrib_sheet[case_row_offset + 26].get_raw(
                case_row_offset_column + gender_idx
            )
        )
        if "[p]" in output:
            output = output.replace("[p]", plural)

        pa = attrib_sheet[24].get_raw(case_column_offset + gender_idx) or ""
        output = output.replace("[pa]", pa)

        # Determine declension row
        decl = None
        match self._parameters.article_type:
            case GermanArticleType.Possessive:
                decl = attrib_sheet[25]
            case GermanArticleType.Demonstrative:
                decl = attrib_sheet[25]
            case GermanArticleType.ZeroArticle:
                decl = attrib_sheet[38]
            case GermanArticleType.Definite:
                decl = attrib_sheet[37]
            case _:
                decl = attrib_sheet[26]
        declension = decl.get_raw(case_column_offset + gender_idx)
        output = output.replace("[a]", str(declension))
        output = output.replace("[n]", str(self._parameters.quantity))

        return output

    def resolve_noun_en(self):
        """
        a1->Offsets[0] = SingularColumnIdx
        a1->Offsets[1] = PluralColumnIdx
        a1->Offsets[2] = StartsWithVowelColumnIdx
        a1->Offsets[3] = PossessivePronounColumnIdx
        a1->Offsets[4] = ArticleColumnIdx
        """
        sheet = self._row.sheet
        coll = sheet.collection
        attrib_sheet = coll.get_sheet("Attributive")

        output = ""

        is_proper_noun = bool(
            self._row.get_raw(self._parameters.column_offset + self.ARTICLE_COLUMN_IDX)
        )
        if not is_proper_noun:
            starts_with_vowel_col = (
                self._parameters.column_offset + self.STARTS_WITH_VOWEL_COLUMN_IDX
            )
            starts_with_vowel = (
                int(self._row.get_raw(starts_with_vowel_col))
                if starts_with_vowel_col >= 0
                else ~starts_with_vowel_col
            )

            article_column = starts_with_vowel + (2 * (starts_with_vowel + 1))
            grammatical_num_col_offset = (
                self.SINGULAR_COLUMN_IDX
                if self._parameters.quantity == 1
                else self.PLURAL_COLUMN_IDX
            )
            article = attrib_sheet[self._parameters.article_type.value].get_raw(
                article_column + grammatical_num_col_offset
            )
            if str(article) != "":
                output += str(article)

        text = self._row.get_raw(
            self._parameters.column_offset
            + (
                self.SINGULAR_COLUMN_IDX
                if self._parameters.quantity == 1
                else self.PLURAL_COLUMN_IDX
            )
        )
        if str(text) != "":
            output += text

        output = output.replace("[n]", str(self._parameters.quantity))

        return output

    def resolve_noun_fr(self):
        """
        a1->Offsets[0] = SingularColumnIdx
        a1->Offsets[1] = PluralColumnIdx
        a1->Offsets[2] = StartsWithVowelColumnIdx
        a1->Offsets[3] = PronounColumnIdx
        a1->Offsets[4] = Unknown5ColumnIdx
        a1->Offsets[5] = ArticleColumnIdx
        """
        sheet = self._row.sheet
        coll = sheet.collection
        attrib_sheet = coll.get_sheet("Attributive")

        starts_with_vowel_col = (
            self._parameters.column_offset + self.STARTS_WITH_VOWEL_COLUMN_IDX
        )
        starts_with_vowel = (
            self._row.get_raw(starts_with_vowel_col)
            if starts_with_vowel_col >= 0
            else ~starts_with_vowel_col
        )

        pronoun_col = self._parameters.column_offset + self.PRONOUN_COLUMN_IDX
        pronoun = (
            int(self._row.get_raw(pronoun_col)) if pronoun_col >= 0 else ~pronoun_col
        )

        article_col = self._parameters.column_offset + self.ARTICLE_COLUMN_IDX
        article = (
            int(self._row.get_raw(article_col)) if article_col >= 0 else ~article_col
        )

        v20 = 4 * (starts_with_vowel + 6 + (2 * pronoun))
        output = ""
        if article != 0:
            v21 = attrib_sheet[self._parameters.article_type.value].get_raw(v20)
            if str(v21) != "":
                output += str(v21)
            text = self.get_default_text()
            if str(text) != "":
                output += str(text)

            if self._parameters.quantity <= 1:
                output = output.replace("[n]", str(self._parameters.quantity))

            return output

        v17 = int(
            self._row.get_raw(self._parameters.column_offset + self.UNKNOWN5_COL_IDX)
        )
        if v17 != 0 and (self._parameters.quantity > 1 or v17 == 2):
            v29 = str(
                attrib_sheet[self._parameters.article_type.value].get_raw(v20 + 2)
            )
            if v29 != "":
                output += v29
                text = str(
                    self._row.get_raw(
                        self._parameters.column_offset + self.PLURAL_COLUMN_IDX
                    )
                )
                output += text
        else:
            v27 = attrib_sheet[self._parameters.article_type.value].get_raw(
                v20 + (1 if v17 != 0 else 3)
            )
            if str(v27) != "":
                output += str(v27)

            text = str(
                self._row.get_raw(
                    self._parameters.column_offset + self.SINGULAR_COLUMN_IDX
                )
            )
            output += text

        output = output.replace("[n]", str(self._parameters.quantity))
        return output

    def resolve_noun_ja(self):
        """Resolve a japanese noun to its reference, given parameters"""
        sheet = self._row.sheet
        coll = sheet.collection
        attrib_sheet = coll.get_sheet("Attributive")

        output = ""
        ksad = attrib_sheet[self._parameters.article_type.value].get_raw(
            1 if self._parameters.quantity > 1 else 0
        )
        if str(ksad) != "":
            output += ksad
            if self._parameters.quantity > 1:
                output = output.replace("[n]", str(self._parameters.quantity))
        text = str(self._row.get_raw(self._parameters.column_offset))
        if text != "":
            output += text
        return output

    def get_default_text(self):
        return self._row.get_raw(
            self._parameters.column_offset
            + (
                self.SINGULAR_COLUMN_IDX
                if self._parameters.quantity == 1
                else self.PLURAL_COLUMN_IDX
            )
        )

    @staticmethod
    def process_row(
        row: XivRow, count: int = 1, article_type=EnglishArticleType.Definite
    ):
        if article_type is None:
            lang = row.sheet.collection.active_language
            match lang:
                case Language.french:
                    article_type = FrenchArticleType.Indefinite
                case Language.english:
                    article_type = EnglishArticleType.Indefinite
                case Language.german:
                    article_type = GermanArticleType.ZeroArticle
                case Language.japanese:
                    article_type = JapaneseArticleType.Distant
                case _:
                    article_type = EnglishArticleType.Indefinite
        settings = NounParameters(
            row.sheet.collection.active_language,
            row.sheet.name,
            row.key,
            count,
            article_type,
            0,
            False,
        )
        return Noun(settings, row)
