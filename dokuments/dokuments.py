"""The dokuments client."""

from collections.abc import AsyncGenerator, Generator
from typing import Any

from koil import unkoil, unkoil_gen
from koil.composition import Composition
from rath.origin import origin_context
from rath.turms.funcs import TOperation

from dokuments.api.schema import DokumentsApi
from dokuments.datalayer import DataLayer
from dokuments.rath import DokumentsRath


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

    @staticmethod
    def _serialize(operation: type[TOperation], variables: dict[str, Any]) -> dict[str, Any]:
        # dokuments sends every argument, set or not (no exclude_unset), as it always has.
        return operation.Arguments(**variables).model_dump(by_alias=True)

    def execute(self, operation: type[TOperation], variables: dict[str, Any]) -> TOperation:
        """Executes a query or mutation in a blocking way."""
        return unkoil(self.aexecute, operation, variables)

    async def aexecute(
        self, operation: type[TOperation], variables: dict[str, Any]
    ) -> TOperation:
        """Executes a query or mutation in a non-blocking way."""
        x = await self.rath.aquery(operation.Meta.document, self._serialize(operation, variables))
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
