import asyncio
import os


from dokuments.scalars import FileLike
from rath.links.parsing import ParsingLink
from rath.operation import Operation, opify
from typing import Any, Tuple, Type, Union
from mikro.io.upload import aupload_bigfile
from pydantic import Field
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from dokuments.datalayer import DataLayer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dokuments.datalayer import DataLayer


async def apply_recursive(
    func, obj, typeguard: Union[Type[Any], Tuple[Type[Any], ...]]
) -> Any:  # type: ignore
    """
    Recursively applies an asynchronous function to elements in a nested structure.

    Args:
        func (callable): The asynchronous function to apply.
        obj (any): The nested structure (dict, list, tuple, etc.) to process.
        typeguard (type): The type of elements to apply the function to.

    Returns:
        any: The nested structure with the function applied to elements of the specified type.
    """
    if isinstance(
        obj, dict
    ):  # If obj is a dictionary, recursively apply to each key-value pair
        return {k: await apply_recursive(func, v, typeguard) for k, v in obj.items()}  # type: ignore
    elif isinstance(obj, list):  # If obj is a list, recursively apply to each element
        return await asyncio.gather(
            *[apply_recursive(func, elem, typeguard) for elem in obj]
        )  # type: ignore
    elif isinstance(
        obj, tuple
    ):  # If obj is a tuple, recursively apply to each element and convert back to tuple
        return tuple(
            await asyncio.gather(
                *[apply_recursive(func, elem, typeguard) for elem in obj]
            )  # type: ignore
        )
    elif isinstance(obj, typeguard):
        return await func(obj)  # type: ignore
    else:  # If obj is not a dict, list, tuple, or matching the typeguard, return it as is
        return obj  # type: ignore


def _size_of(file: FileLike) -> int | None:
    """The file's size, when it can be learned without reading it: what the grant is budgeted for."""
    try:
        return os.fstat(file.value.fileno()).st_size
    except (AttributeError, OSError, ValueError):
        return None


class UploadLink(ParsingLink):
    """Data Layer Upload Link

    This link is used to upload  supported types to a DataLayer.
    It parses queries, mutatoin and subscription arguments and
    uploads the items to the DataLayer, and substitures the
    DataFrame with the S3 path.

    Args:
        ParsingLink (_type_): _description_


    """

    datalayer: DataLayer

    executor: ThreadPoolExecutor = Field(
        default_factory=lambda: ThreadPoolExecutor(max_workers=4), exclude=True
    )
    _executor_session: Any = None

    async def __aenter__(self) -> "UploadLink":
        """Enter the context manager for the UploadLink"""
        self._executor_session = self.executor.__enter__()
        return self

    async def _aexecute(self, document: str, variables: dict[str, Any]) -> Any:
        if not self.next:
            raise ValueError("No next link found. Please set the next link.")
        async for result in self.next.aexecute(opify(document, variables=variables)):
            return result.data
        raise ValueError(f"No result for {document[:40]}")

    async def aupload_bigfile(self, datalayer: "DataLayer", file: FileLike) -> str:
        """Upload a file as a media store of the caller's organization: a grant, a put, a finish."""
        from dokuments.api.schema import (
            FinishMediaUploadInput,
            FinishMediaUploadMutation,
            RequestMediaUploadInput,
            RequestMediaUploadMutation,
        )

        assert datalayer is not None, "Datalayer must be set"
        size = _size_of(file)
        granted = await self._aexecute(
            RequestMediaUploadMutation.Meta.document,
            {"input": RequestMediaUploadInput(originalFileName=file.file_name, fileSize=size, contentType=file.mime_type).model_dump(by_alias=True, exclude_none=True)},
        )
        credentials = RequestMediaUploadMutation(**granted).request_media_upload
        store = await aupload_bigfile(file, credentials, datalayer)
        await self._aexecute(
            FinishMediaUploadMutation.Meta.document,
            {"input": FinishMediaUploadInput(storeId=store, valid=True).model_dump(by_alias=True, exclude_none=True)},
        )
        return store

    async def aparse(self, operation: Operation) -> Operation:
        """Parse the operation (Async)

        Extracts the DataFrame from the operation and uploads it to the DataLayer.

        Args:
            operation (Operation): The operation to parse

        Returns:
            Operation: _description_
        """

        datalayer = operation.context.kwargs.get("datalayer", self.datalayer)

        operation.variables = await apply_recursive(
            partial(self.aupload_bigfile, datalayer),
            operation.variables,
            FileLike,
        )

        return operation

    async def adisconnect(self) -> None:
        """Disconnect the UploadLink"""
        self.executor.__exit__(None, None, None)
