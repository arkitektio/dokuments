"""Download a stored file with a scoped read grant (``requestMediaAccess``); there are no presigned URLs."""

import asyncio
import os
from typing import TYPE_CHECKING

import obstore
from koil import unkoil
from rath.scalars import ID

from dokuments.io.s3 import create_s3_store

if TYPE_CHECKING:
    from dokuments.dokuments import Dokuments


async def adownload_file(dokuments: "Dokuments", store_id: str, file_name: str) -> str:
    """Write the media store ``store_id`` to ``file_name`` and return the path."""
    grant = await dokuments.arequest_media_access(store_id=ID.validate(store_id))
    store = create_s3_store(
        await dokuments.datalayer.get_endpoint_url(),
        grant,
        proxy=dokuments.datalayer.proxy,
        certificates=dokuments.datalayer.certificates,
    )

    parent = os.path.dirname(file_name)
    if parent:
        os.makedirs(parent, exist_ok=True)
    response = await obstore.get_async(store, grant.key)
    # Opening, writing and closing block: each runs on a worker thread, so a
    # large download does not stall the event loop.
    file = await asyncio.to_thread(open, file_name, "wb")
    try:
        async for chunk in response.stream():
            await asyncio.to_thread(file.write, chunk)
    finally:
        await asyncio.to_thread(file.close)
    return file_name


def download_file(dokuments: "Dokuments", store_id: str, file_name: str) -> str:
    return unkoil(adownload_file, dokuments, store_id, file_name)
