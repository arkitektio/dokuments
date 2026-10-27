from typing import Any
from pydantic import BaseModel
from rath.origin import ContextBound, get_origin
from rath.turms.utils import NotQueriedError, get_attributes_or_error


class HasDownloadAccessor(ContextBound, BaseModel):
    """Download Accessor"""

    _dataset: Any = None

    def download(self, file_name: str | None = None) -> "str":
        """Download the file with a scoped read grant

        Args:
            file_name (str | None): The name of the file to save the downloaded file as
                If None, the store's key will be used as the file name.
        Returns:
            str: The path to the downloaded file
        """
        from dokuments.io.download import download_file

        from dokuments.dokuments import Dokuments

        origin = get_origin(self)
        client = origin.client if origin is not None else None
        if not isinstance(client, Dokuments):
            raise ValueError("This store was not fetched through a Dokuments client, so there is none to ask for a read grant.")
        store_id, key = get_attributes_or_error(self, "id", "key")
        return download_file(client, store_id, file_name or key.rsplit("/", 1)[-1])
