"""Talking to the datalayer's S3 with a scoped grant: the store, and putting a file in it."""

import logging
from typing import TYPE_CHECKING, Protocol

import obstore
from obstore.store import S3Store

from dokuments.scalars import FileLike

if TYPE_CHECKING:
    from dokuments.datalayer import DataLayer

logger = logging.getLogger(__name__)


class S3Grant(Protocol):
    """A grant carrying S3 credentials and where the object goes."""

    @property
    def access_key(self) -> str: ...  # noqa: D102

    @property
    def secret_key(self) -> str: ...  # noqa: D102

    @property
    def session_token(self) -> str | None: ...  # noqa: D102

    @property
    def bucket(self) -> str: ...  # noqa: D102

    @property
    def key(self) -> str: ...  # noqa: D102


class UploadError(Exception):
    """A file could not be put into the datalayer."""


def create_s3_store(
    endpoint_url: str,
    grant: S3Grant,
    *,
    proxy: str | None = None,
    certificates: list[str] | None = None,
) -> S3Store:
    """An obstore S3 client for ``grant`` at ``endpoint_url``.

    ``proxy`` is the forward proxy the datalayer is only reachable through.
    ``certificates`` pin a hub's certificates: the store trusts them and nothing else
    (obstore verifies with the platform's verifier, which never reads ``SSL_CERT_FILE``).
    """
    options: dict[str, object] = {}
    if endpoint_url.startswith("http://"):
        options["allow_http"] = True
    if proxy:
        options["proxy_url"] = proxy
    if certificates:
        options["root_certificate"] = "\n".join(pem.strip() for pem in certificates)
        options["disable_system_certificates"] = True
    credentials: dict[str, str] = {
        "access_key_id": grant.access_key,
        "secret_access_key": grant.secret_key,
    }
    if grant.session_token:
        credentials["session_token"] = grant.session_token
    return S3Store(
        grant.bucket,
        endpoint=endpoint_url,
        virtual_hosted_style_request=False,
        client_options=options or None,  # type: ignore[arg-type]
        **credentials,  # type: ignore[arg-type]
    )


async def aupload_bigfile(
    file: FileLike, credentials: "S3Grant", datalayer: "DataLayer"
) -> str:
    """Put ``file`` where ``credentials`` say, and return the store id they name."""
    endpoint_url = await datalayer.get_endpoint_url()
    store = create_s3_store(
        endpoint_url,
        credentials,
        proxy=datalayer.proxy,
        certificates=datalayer.certificates,
    )
    where = f"s3://{credentials.bucket}/{credentials.key} on {endpoint_url}"
    try:
        await obstore.put_async(store, credentials.key, file.value)
    except Exception as e:
        raise UploadError(f"Error while uploading to {where}") from e
    logger.info("Uploaded %s", where)
    return credentials.store  # type: ignore[attr-defined]
