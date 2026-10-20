from dokuments.datalayer import current_dokuments_datalayer, DataLayer
import aiohttp
from koil import unkoil


async def adownload_file(
    presigned_url: str,
    file_name: str,
    datalayer: DataLayer | None = None,
):
    datalayer = datalayer or current_dokuments_datalayer.get()
    if not datalayer:
        raise ValueError("Datalayer is not set")
    endpoint_url = await datalayer.get_endpoint_url()

    async with aiohttp.ClientSession() as session:
        # ``proxy=None`` is aiohttp's own default, so an unproxied datalayer is unchanged.
        async with session.get(
            endpoint_url + presigned_url, proxy=datalayer.proxy
        ) as response:
            with open(file_name, "wb") as file:
                while True:
                    chunk = await response.content.read(
                        1024
                    )  # read the response by chunks of 1024 bytes
                    if not chunk:
                        break
                    file.write(chunk)

    return file_name


def download_file(
    presigned_url: str, file_name: str, datalayer: DataLayer | None = None
):
    return unkoil(
        adownload_file, presigned_url, file_name=file_name, datalayer=datalayer
    )
