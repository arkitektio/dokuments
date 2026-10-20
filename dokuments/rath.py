"""The rath dokuments talks to its server through."""

from pydantic import Field
from rath import rath
from rath.links.auth import AuthTokenLink
from rath.links.compose import TypedComposedLink
from rath.links.dictinglink import DictingLink
from rath.links.shrink import ShrinkingLink
from rath.links.split import SplitLink


class DokumentsLinkComposition(TypedComposedLink):
    shrinking: ShrinkingLink = Field(default_factory=ShrinkingLink)
    dicting: DictingLink = Field(default_factory=DictingLink)
    auth: AuthTokenLink
    split: SplitLink


class DokumentsRath(rath.Rath):
    """The rath of a :class:`~dokuments.dokuments.Dokuments` client.

    Nothing is looked up from a context: the client that owns it runs every
    operation over it.
    """
