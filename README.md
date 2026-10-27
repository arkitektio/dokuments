# dokuments

[![PyPI version](https://badge.fury.io/py/dokuments.svg)](https://pypi.org/project/dokuments/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/dokuments.svg)](https://pypi.python.org/pypi/dokuments/)
![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)

The python client for dokuments, the [Arkitekt](https://arkitekt.live) document
service: files uploaded to the deployment's S3 datalayer, and documents made of
pages, each page an image with its OCR result (text lines and page rotation).

## Installation

```sh
pip install dokuments
```

## Usage

Every dokuments operation is a method of the `Dokuments` client, in a blocking
and an `a`-prefixed async flavour: `from_file_like` (upload a file),
`get_file`, `search_files`, `watch_files`, `create_document`, `create_page`,
`request_file_access`, ….

### In an arkitekt app

The client is injected by annotation. Add the service to your app and ask for
`dokuments: Dokuments`:

```python
from arkitekt import App, run
from dokuments import Dokuments, dokuments_service
from dokuments.api.schema import File

app = App("scanner", "0.1.0", services=[dokuments_service])


@app.action
def upload_scan(path: str, dokuments: Dokuments) -> File:
    """Upload Scan"""
    return dokuments.from_file_like(file=path)


if __name__ == "__main__":
    run(app)
```

Files travel between actions by id (`@dokuments/file`), so an action can take
and return them directly.

### From a script

```python
from arkitekt import easy
from dokuments import dokuments_service

with easy("my-script", dokuments_service) as dokuments:
    file = dokuments.from_file_like(file="scan.pdf")  # a path, a Path or a binary file object
    document = dokuments.create_document(title="My scan", file=file.id)
    print(document.id, file.store.download())  # the bytes, through a scoped read grant
```

Uploads go straight to the datalayer: the client asks the server for upload
credentials and writes the file to S3 before the mutation is sent.

## Development

The generated API (`dokuments/api/schema.py`) comes from the checked-in
`schema.graphql` and the documents in `graphql/`; see `graphql.config.yaml`.
