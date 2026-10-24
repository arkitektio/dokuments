import io

import pytest

from dokuments.api.schema import File

from .conftest import DeployedDokuments


def upload(deployed_app: DeployedDokuments) -> File:
    content = io.BytesIO(b"%PDF-1.4 a tiny document")
    content.name = "tiny.pdf"
    return deployed_app.dokuments.from_file_like(file=content)


@pytest.mark.integration
def test_a_file_is_uploaded_and_found_again(deployed_app: DeployedDokuments) -> None:
    """A file goes to the datalayer through the upload link, and the server keeps its store."""
    file = upload(deployed_app)

    again = deployed_app.dokuments.get_file(file.id)
    assert again.id == file.id
    assert again.store.key and again.store.bucket
    assert file.id in [option.value for option in deployed_app.dokuments.search_files(values=[file.id])]


@pytest.mark.integration
def test_a_document_is_created_from_a_file(deployed_app: DeployedDokuments) -> None:
    """A document of an uploaded file, with no pages yet.

    The schema calls ``file`` optional, but the server's table requires it: a document
    created without one fails with a not-null violation (a server bug).
    """
    document = deployed_app.dokuments.create_document(title="Test Document", file=upload(deployed_app).id)
    assert document.title == "Test Document"
    assert document.pages == ()


@pytest.mark.integration
def test_an_uploaded_file_downloads_with_a_read_grant(deployed_app: DeployedDokuments, tmp_path) -> None:  # noqa: ANN001
    """The bytes come back through ``requestMediaAccess``: there are no presigned URLs."""
    file = upload(deployed_app)
    assert file.store is not None
    path = file.store.download(str(tmp_path / "back.pdf"))
    assert open(path, "rb").read() == b"%PDF-1.4 a tiny document"
