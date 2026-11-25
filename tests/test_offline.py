import io

from arkitekt_spec.declare.client import client_of

from dokuments import Dokuments
from dokuments.scalars import FileLike


def test_dokuments_declares_its_client_and_structures() -> None:
    declaration = client_of(Dokuments)
    assert declaration is not None and declaration.name == "dokuments"
    assert [s.identifier for s in declaration.structures] == ["@dokuments/file"]


def test_a_file_like_keeps_its_name_and_type() -> None:
    content = io.BytesIO(b"%PDF-1.4")
    content.name = "folder/report.pdf"
    file = FileLike.validate(content)
    assert file.file_name == "report.pdf"
    assert file.mime_type == "application/pdf"
