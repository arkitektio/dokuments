"""The dokuments service of an arkitekt app, and the types it sends by id.

Declared on one registry: the service first, then the structures whose expanders
ask for the ``Dokuments`` it returns. An app takes all of it in with
``App(services=[dokuments_service])``.
"""

import os
from typing import Annotated

from fakts import Alias, Require, TokenLoader
from fakts.contrib.rath.auth import FaktsAuthLink
from graphql import OperationType
from rath.links.aiohttp import AIOHttpLink
from rath.links.compose import compose
from rath.links.dictinglink import DictingLink
from rath.links.file import FileExtraction
from rath.links.graphql_ws import GraphQLWSLink
from rath.links.split import SplitLink

from arkitekt_spec.declare.app import AppRegistry
from arkitekt_spec.declare.widgets import SearchWidget

from dokuments.api.schema import File, SearchFilesQuery
from dokuments.datalayer import DataLayer
from dokuments.dokuments import Dokuments
from dokuments.links.upload import UploadLink
from dokuments.rath import DokumentsRath


def build_relative_path(*path: str) -> str:
    """Build a path relative to this file, for the files shipped beside it."""
    return os.path.join(os.path.dirname(__file__), *path)


registry = AppRegistry()
"""What dokuments brings to an app: its service, and the types it sends by id."""


@registry.service(
    schema=build_relative_path("api", "schema.graphql"),
    turms=build_relative_path("api", "project.json"),
)
def dokuments(
    dokuments: Annotated[
        Alias,
        Require("live.arkitekt.dokuments", "Where the user's documents live"),
    ],
    datalayer: Annotated[
        Alias,
        Require("live.arkitekt.s3", "Where the documents' files are stored"),
    ],
    tokens: TokenLoader,
) -> Dokuments:
    """Dokuments: the user's documents and the files behind them.

    The ``datalayer`` requirement is new only in the sense that it was always
    used and never declared: the builder resolved a ``"datalayer"`` group no
    manifest asked a deployment to provision, so the alias never resolved.
    Declaring the parameter is what fixes it.
    """
    store = DataLayer.from_alias(datalayer)

    return Dokuments(
        datalayer=store,
        rath=DokumentsRath(
            link=compose(
                FileExtraction(),
                DictingLink(),
                # TODO: a ContextLink() used to sit here, imported from
                # `rekuest.links.context`. That module and class exist nowhere in
                # rekuest any more -- this was the only reference left in the tree,
                # and it made this whole module unimportable. Dropped so the service
                # loads at all; whatever context it propagated to the server now
                # does not, and needs a replacement if anything relied on it.
                # After the upload link: the upload uses the auth link too.
                UploadLink(datalayer=store),
                FaktsAuthLink(token_loader=tokens),
                SplitLink(
                    left=AIOHttpLink(endpoint_url=dokuments.to_http_path("graphql"), proxy=dokuments.proxy),
                    right=GraphQLWSLink(ws_endpoint_url=dokuments.to_ws_path("graphql"), proxy=dokuments.proxy),
                    split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                ),
            ),
        ),
    )


def _search(query: object) -> SearchWidget:
    """The widget that picks one of these out of the deployment."""
    return SearchWidget(query=query.Meta.document, ward="dokuments")  # type: ignore[attr-defined]


@registry.structure("@dokuments/file", widget=_search(SearchFilesQuery))
async def expand_file(id: str, dokuments: Dokuments) -> File:
    """A file, by id."""
    return await dokuments.aget_file(id)
