from typing import TypeVar
from koil.composition import Composition
from .rath import DokumentsRath

T = TypeVar("T")


class Dokuments(Composition):
    rath: DokumentsRath
