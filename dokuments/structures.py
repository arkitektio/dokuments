"""The types dokuments sends by id, each expanded by the ``Dokuments`` client.

Imported by ``dokuments/__init__``: an app using ``Dokuments`` takes every one of them.
"""

from arkitekt_spec.declare.structures.declare import structure
from arkitekt_spec.declare.widgets import SearchWidget

from dokuments.api.schema import File, SearchFilesQuery
from dokuments.dokuments import Dokuments


@structure(
    "@dokuments/file",
    widget=SearchWidget(query=SearchFilesQuery.Meta.document, ward="dokuments"),
)
async def expand_file(id: str, dokuments: Dokuments) -> File:
    """A file, by id."""
    return await dokuments.aget_file(id)
