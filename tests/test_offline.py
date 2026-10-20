import io

from dokuments import Dokuments, dokuments_service
from dokuments.scalars import FileLike


def test_the_service_module_imports() -> None:
    """The service and its structures load, with every link they compose."""
    assert dokuments_service is not None and Dokuments is not None


def test_a_file_like_keeps_its_name_and_type() -> None:
    content = io.BytesIO(b"%PDF-1.4")
    content.name = "folder/report.pdf"
    file = FileLike.validate(content)
    assert file.file_name == "report.pdf"
    assert file.mime_type == "application/pdf"
