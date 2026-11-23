import io
import mimetypes
import os
from pathlib import Path
from typing import IO, TypeAlias

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

FileCoercible: TypeAlias = str | bytes | Path | io.BufferedReader


class FileLike:
    """A custom scalar for ensuring a common format to support write to the
    parquet api supported by mikro It converts the passed value into
    a compliant format.."""

    def __init__(self, value: IO[bytes], name: str = "") -> None:
        """Initialize the FileLike scalar with a file-like object."""
        self.value = value
        self.file_name = os.path.basename(name)
        self.mime_type = mimetypes.guess_type(self.file_name)[0]

    def __get__(self, instance: object, owner: type | None) -> "FileLike": ...  # type: ignore

    def __set__(self, instance: object, value: FileCoercible) -> None: ...  # type: ignore

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: object,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_after_validator_function(
            cls.validate, handler(object)
        )

    @classmethod
    def validate(cls, v: FileCoercible) -> "FileLike":
        """Validate the validator function"""

        if isinstance(v, str):
            file = open(v, "rb")
            name = v
        elif isinstance(v, io.IOBase):
            file = v
            name = v.name
        elif isinstance(v, Path):
            file = open(v, "rb")
            name = str(v)
        else:
            raise ValueError(
                f"Unsupported type {type(v)}. Please provide a string or a Path object. Or a file object that is opened in binary mode."
            )

        if not isinstance(file, io.IOBase):  # type: ignore
            raise ValueError("This needs to be a instance of a file")

        return cls(file, name=name)

    def __repr__(self) -> str:
        """Return a string representation of the FileLike scalar."""
        return f"FileLike({self.value})"
