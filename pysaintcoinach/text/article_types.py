from enum import Enum


class EnglishArticleType(Enum):
    Indefinite = 1
    Definite = 2


class FrenchArticleType(Enum):
    Indefinite = 1
    Definite = 2
    PossessiveFirstPerson = 3
    PossessiveSecondPerson = 4
    PossessiveThirdPerson = 5


class GermanArticleType(Enum):
    Indefinite = 1
    Definite = 2
    Possessive = 3
    Negative = 4
    ZeroArticle = 5
    Demonstrative = 6


class JapaneseArticleType(Enum):
    NearListener = 1
    Distant = 2
