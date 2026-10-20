from typing import Any
from pydantic import BaseModel
from rath.turms.utils import NotQueriedError, get_attributes_or_error


class HasDownloadAccessor(BaseModel):
    """Download Accessor"""

    _dataset: Any = None

    def download(self, file_name: str | None = None) -> "str":
        """Download the file from the presigned URL

        Args:
            file_name (str | None): The name of the file to save the downloaded file as
                If None, the key from the presigned URL will be used as the file name.
        Returns:
            str: The path to the downloaded file
        """
        from dokuments.io.download import download_file

        url, key = get_attributes_or_error(self, "presigned_url", "key")
        return download_file(url, file_name=file_name or key)
