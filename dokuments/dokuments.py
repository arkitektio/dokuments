"""The dokuments client."""

import os
from collections.abc import AsyncGenerator, Generator
from typing import Annotated, Any, Self

from arkitekt_spec.declare.client import client
from arkitekt_spec.declare.tested import tested_against
from fakts import Alias, Require, TokenLoader
from koil import unkoil, unkoil_gen
from koil.composition import Composition
from rath.origin import origin_context
from rath.turms.funcs import TOperation

from dokuments.api.schema import DokumentsApi
from dokuments.datalayer import DataLayer
from dokuments.rath import DokumentsRath

TESTED = tested_against("dokuments")
"""The dokuments server this release wants: the one its release job tested it against."""

_API = os.path.join(os.path.dirname(__file__), "api")


@client(
    schema=os.path.join(_API, "schema.graphql"),
    turms=os.path.join(_API, "project.json"),
)
class Dokuments(Composition, DokumentsApi):
    """The dokuments client.

    Every dokuments operation is a method of it (``dokuments.aget_room(id)``),
    mixed in from the generated ``DokumentsApi``; each hands its operation to
    the four methods below, which run it over this client's rath. What a call
    returns remembers this client. Actions ask for it by annotation
    (``dokuments: Dokuments``) and are handed their app's client.
    """

    rath: DokumentsRath
    datalayer: DataLayer

    @classmethod
    def from_fakts(
        cls,
        dokuments: Annotated[
            Alias,
            Require(
                "live.arkitekt.dokuments",
                "Where the user's documents live",
                version=TESTED,
            ),
        ],
        datalayer: Annotated[
            Alias, Require("live.arkitekt.s3", "Where the documents' files are stored")
        ],
        tokens: TokenLoader,
    ) -> Self:
        """Built by a run: talks to the resolved dokuments, uploading to its datalayer."""
        from fakts.contrib.rath.auth import FaktsAuthLink
        from rath.links.aiohttp import AIOHttpLink
        from rath.links.compose import compose
        from rath.links.dictinglink import DictingLink
        from rath.links.file import FileExtraction
        from rath.links.graphql_ws import GraphQLWSLink
        from rath.links.split import SplitLink

        from dokuments.links.upload import UploadLink
        from graphql import OperationType

        store = DataLayer.from_alias(datalayer)
        return cls(
            datalayer=store,
            rath=DokumentsRath(
                link=compose(
                    FileExtraction(),
                    DictingLink(),
                    # TODO: a ContextLink (gone from rekuest) used to sit here;
                    # replace it if anything relied on the context it sent.
                    # Before the auth link: the upload uses it too.
                    UploadLink(datalayer=store),
                    FaktsAuthLink(token_loader=tokens),
                    SplitLink(
                        left=AIOHttpLink(
                            endpoint_url=dokuments.to_http_path("graphql"),
                            proxy=dokuments.proxy,
                            ssl_context=dokuments.ssl_context(),
                        ),
                        right=GraphQLWSLink(
                            ws_endpoint_url=dokuments.to_ws_path("graphql"),
                            proxy=dokuments.proxy,
                            ssl_context=dokuments.ssl_context(),
                        ),
                        split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                    ),
                ),
            ),
        )

    @staticmethod
    def _serialize(
        operation: type[TOperation], variables: dict[str, Any]
    ) -> dict[str, Any]:
        # dokuments sends every argument, set or not (no exclude_unset), as it always has.
        return operation.Arguments(**variables).model_dump(by_alias=True)

    def execute(
        self, operation: type[TOperation], variables: dict[str, Any]
    ) -> TOperation:
        """Executes a query or mutation in a blocking way."""
        return unkoil(self.aexecute, operation, variables)

    async def aexecute(
        self, operation: type[TOperation], variables: dict[str, Any]
    ) -> TOperation:
        """Executes a query or mutation in a non-blocking way."""
        x = await self.rath.aquery(
            operation.Meta.document, self._serialize(operation, variables)
        )
        return operation.model_validate(
            x.data, context=origin_context(client=self, rath=self.rath)
        )

    def subscribe(
        self, operation: type[TOperation], variables: dict[str, Any]
    ) -> Generator[TOperation, None, None]:
        """Subscribes to an operation in a blocking way."""
        return unkoil_gen(self.asubscribe, operation, variables)

    async def asubscribe(
        self, operation: type[TOperation], variables: dict[str, Any]
    ) -> AsyncGenerator[TOperation, None]:
        """Subscribes to an operation in a non-blocking way."""
        async for event in self.rath.asubscribe(
            operation.Meta.document, self._serialize(operation, variables)
        ):
            yield operation.model_validate(
                event.data, context=origin_context(client=self, rath=self.rath)
            )
