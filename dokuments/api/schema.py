import builtins
from dokuments.scalars import FileLike
from dokuments.traits import HasDownloadAccessor
from enum import Enum
from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from rath.scalars import ID, IDCoercible
from typing import Annotated, AsyncIterator, Iterable, Iterator, Literal


class GraphQLDefault:
    """Records a GraphQL field schema default value. The client omits the field so the server applies its own default; this preserves the value for introspection."""

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "GraphQLDefault(" + repr(self.value) + ")"


class UnsetType:
    """Sentinel for arguments the caller did not provide. Such fields are omitted on serialization so the GraphQL server applies its own default."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return "UNSET"

    def __bool__(self):
        return False


UNSET = UnsetType()


class CreateDocumentInput(BaseModel):
    """No documentation"""

    file: ID | None = None
    title: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreatePageInput(BaseModel):
    """No documentation"""

    image: FileLike
    index: int
    document: ID
    ocr_result: "OCRPageResultInput" = Field(
        validation_alias=AliasChoices("ocr_result", "ocrResult"),
        serialization_alias="ocrResult",
    )
    content: str | None = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class FinishMediaUploadInput(BaseModel):
    """No documentation"""

    store_id: str = Field(
        validation_alias=AliasChoices("store_id", "storeId"),
        serialization_alias="storeId",
    )
    valid: Annotated[bool | None, GraphQLDefault("True")] = None
    "Default: True"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class FromFileLike(BaseModel):
    """No documentation"""

    file: FileLike
    dataset: ID | None = None
    origins: tuple[ID, ...] | None = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class OCRPageResultInput(BaseModel):
    """No documentation"""

    angle: float = Field(description="Estimated rotation angle of the page")
    lines: tuple["OCRTextLineInput", ...]
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class OCRTextLineInput(BaseModel):
    """No documentation"""

    text: str
    score: float
    angle: float
    bbox: tuple[tuple[int, ...], ...]
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestMediaAccessInput(BaseModel):
    """No documentation"""

    store_id: str = Field(
        validation_alias=AliasChoices("store_id", "storeId"),
        serialization_alias="storeId",
    )
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestMediaUploadInput(BaseModel):
    """No documentation"""

    original_file_name: str = Field(
        validation_alias=AliasChoices("original_file_name", "originalFileName"),
        serialization_alias="originalFileName",
    )
    file_size: int | None = Field(
        validation_alias=AliasChoices("file_size", "fileSize"),
        serialization_alias="fileSize",
        default=None,
    )
    content_type: str | None = Field(
        validation_alias=AliasChoices("content_type", "contentType"),
        serialization_alias="contentType",
        default=None,
    )
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class MediaUploadGrant(BaseModel):
    """Temporary S3 credentials for uploading a media object."""

    typename: Literal["MediaUploadGrant"] = Field(
        alias="__typename", default="MediaUploadGrant", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    session_token: str = Field(alias="sessionToken")
    path: str
    key: str
    bucket: str
    region: str
    expires_in: int = Field(alias="expiresIn")
    max_bytes: int = Field(alias="maxBytes")
    store: str
    model_config = ConfigDict(frozen=True)

    class Meta:
        """Meta class for MediaUploadGrant"""

        document = "fragment MediaUploadGrant on MediaUploadGrant {\n  accessKey\n  secretKey\n  sessionToken\n  path\n  key\n  bucket\n  region\n  expiresIn\n  maxBytes\n  store\n  __typename\n}"
        name = "MediaUploadGrant"
        type = "MediaUploadGrant"


class MediaAccessGrant(BaseModel):
    """Temporary S3 credentials for reading a media object."""

    typename: Literal["MediaAccessGrant"] = Field(
        alias="__typename", default="MediaAccessGrant", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    session_token: str = Field(alias="sessionToken")
    path: str
    key: str
    bucket: str
    region: str
    expires_in: int = Field(alias="expiresIn")
    store: str | None = Field(default=None)
    model_config = ConfigDict(frozen=True)

    class Meta:
        """Meta class for MediaAccessGrant"""

        document = "fragment MediaAccessGrant on MediaAccessGrant {\n  accessKey\n  secretKey\n  sessionToken\n  path\n  key\n  bucket\n  region\n  expiresIn\n  store\n  __typename\n}"
        name = "MediaAccessGrant"
        type = "MediaAccessGrant"


class Page(BaseModel):
    """No documentation"""

    typename: Literal["Page"] = Field(alias="__typename", default="Page", exclude=True)
    id: ID
    index: int
    content: str
    "The content of the page as a flat string."
    model_config = ConfigDict(frozen=True)

    class Meta:
        """Meta class for Page"""

        document = "fragment Page on Page {\n  id\n  index\n  content\n  __typename\n}"
        name = "Page"
        type = "Page"


class MediaStore(HasDownloadAccessor, BaseModel):
    """No documentation"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    id: ID
    key: str
    bucket: str
    path: str
    size_bytes: int | None = Field(default=None, alias="sizeBytes")
    "How many bytes this store actually holds, measured when its upload was finished. Null while unfinished, or for stores written before this was recorded"
    original_file_name: str | None = Field(default=None, alias="originalFileName")
    content_type: str | None = Field(default=None, alias="contentType")
    model_config = ConfigDict(frozen=True)

    class Meta:
        """Meta class for MediaStore"""

        document = "fragment MediaStore on MediaStore {\n  id\n  key\n  bucket\n  path\n  sizeBytes\n  originalFileName\n  contentType\n  __typename\n}"
        name = "MediaStore"
        type = "MediaStore"


class Document(BaseModel):
    """No documentation"""

    typename: Literal["Document"] = Field(
        alias="__typename", default="Document", exclude=True
    )
    id: ID
    title: str
    pages: tuple[Page, ...]
    model_config = ConfigDict(frozen=True)

    class Meta:
        """Meta class for Document"""

        document = "fragment Page on Page {\n  id\n  index\n  content\n  __typename\n}\n\nfragment Document on Document {\n  id\n  title\n  pages {\n    ...Page\n    __typename\n  }\n  __typename\n}"
        name = "Document"
        type = "Document"


class File(BaseModel):
    """No documentation"""

    typename: Literal["File"] = Field(alias="__typename", default="File", exclude=True)
    id: ID
    store: MediaStore | None = Field(default=None)
    model_config = ConfigDict(frozen=True)

    class Meta:
        """Meta class for File"""

        document = "fragment MediaStore on MediaStore {\n  id\n  key\n  bucket\n  path\n  sizeBytes\n  originalFileName\n  contentType\n  __typename\n}\n\nfragment File on File {\n  id\n  store {\n    ...MediaStore\n    __typename\n  }\n  __typename\n}"
        name = "File"
        type = "File"


class CreateDocumentMutation(BaseModel):
    """No documentation found for this operation."""

    create_document: Document = Field(alias="createDocument")
    "Create a new document"

    class Arguments(BaseModel):
        """Arguments for CreateDocument"""

        input: CreateDocumentInput

    class Meta:
        """Meta class for CreateDocument"""

        document = "fragment Page on Page {\n  id\n  index\n  content\n  __typename\n}\n\nfragment Document on Document {\n  id\n  title\n  pages {\n    ...Page\n    __typename\n  }\n  __typename\n}\n\nmutation CreateDocument($input: CreateDocumentInput!) {\n  createDocument(input: $input) {\n    ...Document\n    __typename\n  }\n}"


class From_file_likeMutation(BaseModel):
    """No documentation found for this operation."""

    from_file_like: File = Field(alias="fromFileLike")
    "Create a file from file-like data"

    class Arguments(BaseModel):
        """Arguments for from_file_like"""

        input: FromFileLike

    class Meta:
        """Meta class for from_file_like"""

        document = "fragment MediaStore on MediaStore {\n  id\n  key\n  bucket\n  path\n  sizeBytes\n  originalFileName\n  contentType\n  __typename\n}\n\nfragment File on File {\n  id\n  store {\n    ...MediaStore\n    __typename\n  }\n  __typename\n}\n\nmutation from_file_like($input: FromFileLike!) {\n  fromFileLike(input: $input) {\n    ...File\n    __typename\n  }\n}"


class RequestMediaUploadMutation(BaseModel):
    """No documentation found for this operation."""

    request_media_upload: MediaUploadGrant = Field(alias="requestMediaUpload")
    "Request temporary S3 credentials to upload one file (a document, or a page's image)."

    class Arguments(BaseModel):
        """Arguments for RequestMediaUpload"""

        input: RequestMediaUploadInput

    class Meta:
        """Meta class for RequestMediaUpload"""

        document = "fragment MediaUploadGrant on MediaUploadGrant {\n  accessKey\n  secretKey\n  sessionToken\n  path\n  key\n  bucket\n  region\n  expiresIn\n  maxBytes\n  store\n  __typename\n}\n\nmutation RequestMediaUpload($input: RequestMediaUploadInput!) {\n  requestMediaUpload(input: $input) {\n    ...MediaUploadGrant\n    __typename\n  }\n}"


class FinishMediaUploadMutation(BaseModel):
    """No documentation found for this operation."""

    finish_media_upload: MediaStore = Field(alias="finishMediaUpload")
    "Finalize an upload after the client has written the object."

    class Arguments(BaseModel):
        """Arguments for FinishMediaUpload"""

        input: FinishMediaUploadInput

    class Meta:
        """Meta class for FinishMediaUpload"""

        document = "fragment MediaStore on MediaStore {\n  id\n  key\n  bucket\n  path\n  sizeBytes\n  originalFileName\n  contentType\n  __typename\n}\n\nmutation FinishMediaUpload($input: FinishMediaUploadInput!) {\n  finishMediaUpload(input: $input) {\n    ...MediaStore\n    __typename\n  }\n}"


class RequestMediaAccessMutation(BaseModel):
    """No documentation found for this operation."""

    request_media_access: MediaAccessGrant = Field(alias="requestMediaAccess")
    "Request temporary S3 read credentials for an uploaded file."

    class Arguments(BaseModel):
        """Arguments for RequestMediaAccess"""

        input: RequestMediaAccessInput

    class Meta:
        """Meta class for RequestMediaAccess"""

        document = "fragment MediaAccessGrant on MediaAccessGrant {\n  accessKey\n  secretKey\n  sessionToken\n  path\n  key\n  bucket\n  region\n  expiresIn\n  store\n  __typename\n}\n\nmutation RequestMediaAccess($input: RequestMediaAccessInput!) {\n  requestMediaAccess(input: $input) {\n    ...MediaAccessGrant\n    __typename\n  }\n}"


class CreatePageMutation(BaseModel):
    """No documentation found for this operation."""

    create_page: Page = Field(alias="createPage")
    "Create a new page in a document"

    class Arguments(BaseModel):
        """Arguments for CreatePage"""

        input: CreatePageInput

    class Meta:
        """Meta class for CreatePage"""

        document = "fragment Page on Page {\n  id\n  index\n  content\n  __typename\n}\n\nmutation CreatePage($input: CreatePageInput!) {\n  createPage(input: $input) {\n    ...Page\n    __typename\n  }\n}"


class GetFileQuery(BaseModel):
    """No documentation found for this operation."""

    file: File

    class Arguments(BaseModel):
        """Arguments for GetFile"""

        id: ID

    class Meta:
        """Meta class for GetFile"""

        document = "fragment MediaStore on MediaStore {\n  id\n  key\n  bucket\n  path\n  sizeBytes\n  originalFileName\n  contentType\n  __typename\n}\n\nfragment File on File {\n  id\n  store {\n    ...MediaStore\n    __typename\n  }\n  __typename\n}\n\nquery GetFile($id: ID!) {\n  file(id: $id) {\n    ...File\n    __typename\n  }\n}"


class SearchFilesQueryOptions(BaseModel):
    """No documentation"""

    typename: Literal["File"] = Field(alias="__typename", default="File", exclude=True)
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchFilesQuery(BaseModel):
    """No documentation found for this operation."""

    options: tuple[SearchFilesQueryOptions, ...]

    class Arguments(BaseModel):
        """Arguments for SearchFiles"""

        search: str | None = Field(default=None)
        values: list[ID] | None = Field(default=None)

    class Meta:
        """Meta class for SearchFiles"""

        document = "query SearchFiles($search: String, $values: [ID!]) {\n  options: files(filters: { search: $search, ids: $values }) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class WatchFilesSubscriptionFiles(BaseModel):
    """No documentation"""

    typename: Literal["FileEvent"] = Field(
        alias="__typename", default="FileEvent", exclude=True
    )
    create: File | None = Field(default=None)
    delete: ID | None = Field(default=None)
    update: File | None = Field(default=None)
    model_config = ConfigDict(frozen=True)


class WatchFilesSubscription(BaseModel):
    """No documentation found for this operation."""

    files: WatchFilesSubscriptionFiles
    "Subscribe to real-time file updates"

    class Arguments(BaseModel):
        """Arguments for WatchFiles"""

        dataset: ID | None = Field(default=None)

    class Meta:
        """Meta class for WatchFiles"""

        document = "fragment MediaStore on MediaStore {\n  id\n  key\n  bucket\n  path\n  sizeBytes\n  originalFileName\n  contentType\n  __typename\n}\n\nfragment File on File {\n  id\n  store {\n    ...MediaStore\n    __typename\n  }\n  __typename\n}\n\nsubscription WatchFiles($dataset: ID) {\n  files(dataset: $dataset) {\n    create {\n      ...File\n      __typename\n    }\n    delete\n    update {\n      ...File\n      __typename\n    }\n    __typename\n  }\n}"


class DokumentsApi:
    """Every operation of this API as a method. Generated by turms.

    Each method hands its operation to ``execute``, ``aexecute``, ``subscribe``, ``asubscribe`` of ``self``, which the class this one is mixed into (or a base of it) provides.
    """

    async def acreate_document(
        self, title: str, file: IDCoercible | None | UnsetType = UNSET
    ) -> Document:
        """CreateDocument

        Create a new document

        Args:
            file: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
            title: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)

        Returns:
            Document
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        if file is not UNSET:
            _input["file"] = file
        _input["title"] = title
        variables["input"] = _input
        return (await self.aexecute(CreateDocumentMutation, variables)).create_document

    def create_document(
        self, title: str, file: IDCoercible | None | UnsetType = UNSET
    ) -> Document:
        """CreateDocument

        Create a new document

        Args:
            file: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
            title: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)

        Returns:
            Document
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        if file is not UNSET:
            _input["file"] = file
        _input["title"] = title
        variables["input"] = _input
        return self.execute(CreateDocumentMutation, variables).create_document

    async def afrom_file_like(
        self,
        file: FileLike,
        dataset: IDCoercible | None | UnsetType = UNSET,
        origins: Iterable[IDCoercible] | None | UnsetType = UNSET,
    ) -> File:
        """from_file_like

        Create a file from file-like data

        Args:
            file: The `FileLike` scalar type represents a reference to a big file storage previously created by the user n a datalayer (required)
            dataset: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
            origins: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)

        Returns:
            File
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["file"] = file
        if dataset is not UNSET:
            _input["dataset"] = dataset
        if origins is not UNSET:
            _input["origins"] = origins
        variables["input"] = _input
        return (await self.aexecute(From_file_likeMutation, variables)).from_file_like

    def from_file_like(
        self,
        file: FileLike,
        dataset: IDCoercible | None | UnsetType = UNSET,
        origins: Iterable[IDCoercible] | None | UnsetType = UNSET,
    ) -> File:
        """from_file_like

        Create a file from file-like data

        Args:
            file: The `FileLike` scalar type represents a reference to a big file storage previously created by the user n a datalayer (required)
            dataset: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
            origins: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)

        Returns:
            File
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["file"] = file
        if dataset is not UNSET:
            _input["dataset"] = dataset
        if origins is not UNSET:
            _input["origins"] = origins
        variables["input"] = _input
        return self.execute(From_file_likeMutation, variables).from_file_like

    async def arequest_media_upload(
        self,
        original_file_name: str,
        file_size: int | None | UnsetType = UNSET,
        content_type: str | None | UnsetType = UNSET,
    ) -> MediaUploadGrant:
        """RequestMediaUpload

        Request temporary S3 credentials to upload one file (a document, or a page's image).

        Args:
            original_file_name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
            file_size: A number of bytes. 64-bit, unlike Int: serialized as a JSON number, and accepted as a number or a numeric string.
            content_type: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.

        Returns:
            MediaUploadGrant
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["originalFileName"] = original_file_name
        if file_size is not UNSET:
            _input["fileSize"] = file_size
        if content_type is not UNSET:
            _input["contentType"] = content_type
        variables["input"] = _input
        return (
            await self.aexecute(RequestMediaUploadMutation, variables)
        ).request_media_upload

    def request_media_upload(
        self,
        original_file_name: str,
        file_size: int | None | UnsetType = UNSET,
        content_type: str | None | UnsetType = UNSET,
    ) -> MediaUploadGrant:
        """RequestMediaUpload

        Request temporary S3 credentials to upload one file (a document, or a page's image).

        Args:
            original_file_name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
            file_size: A number of bytes. 64-bit, unlike Int: serialized as a JSON number, and accepted as a number or a numeric string.
            content_type: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.

        Returns:
            MediaUploadGrant
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["originalFileName"] = original_file_name
        if file_size is not UNSET:
            _input["fileSize"] = file_size
        if content_type is not UNSET:
            _input["contentType"] = content_type
        variables["input"] = _input
        return self.execute(RequestMediaUploadMutation, variables).request_media_upload

    async def afinish_media_upload(self, store_id: str, valid: bool) -> MediaStore:
        """FinishMediaUpload

        Finalize an upload after the client has written the object.

        Args:
            store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
            valid: The `Boolean` scalar type represents `true` or `false`. (required)

        Returns:
            MediaStore
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["storeId"] = store_id
        _input["valid"] = valid
        variables["input"] = _input
        return (
            await self.aexecute(FinishMediaUploadMutation, variables)
        ).finish_media_upload

    def finish_media_upload(self, store_id: str, valid: bool) -> MediaStore:
        """FinishMediaUpload

        Finalize an upload after the client has written the object.

        Args:
            store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
            valid: The `Boolean` scalar type represents `true` or `false`. (required)

        Returns:
            MediaStore
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["storeId"] = store_id
        _input["valid"] = valid
        variables["input"] = _input
        return self.execute(FinishMediaUploadMutation, variables).finish_media_upload

    async def arequest_media_access(self, store_id: str) -> MediaAccessGrant:
        """RequestMediaAccess

        Request temporary S3 read credentials for an uploaded file.

        Args:
            store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)

        Returns:
            MediaAccessGrant
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["storeId"] = store_id
        variables["input"] = _input
        return (
            await self.aexecute(RequestMediaAccessMutation, variables)
        ).request_media_access

    def request_media_access(self, store_id: str) -> MediaAccessGrant:
        """RequestMediaAccess

        Request temporary S3 read credentials for an uploaded file.

        Args:
            store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)

        Returns:
            MediaAccessGrant
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["storeId"] = store_id
        variables["input"] = _input
        return self.execute(RequestMediaAccessMutation, variables).request_media_access

    async def acreate_page(
        self,
        image: FileLike,
        index: int,
        document: IDCoercible,
        ocr_result: OCRPageResultInput,
        content: str | None | UnsetType = UNSET,
    ) -> Page:
        """CreatePage

        Create a new page in a document

        Args:
            image: The `FileLike` scalar type represents a reference to a big file storage previously created by the user n a datalayer (required)
            index: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
            document: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
            ocr_result:  (required)
            content: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.

        Returns:
            Page
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["image"] = image
        _input["index"] = index
        _input["document"] = document
        _input["ocrResult"] = ocr_result
        if content is not UNSET:
            _input["content"] = content
        variables["input"] = _input
        return (await self.aexecute(CreatePageMutation, variables)).create_page

    def create_page(
        self,
        image: FileLike,
        index: int,
        document: IDCoercible,
        ocr_result: OCRPageResultInput,
        content: str | None | UnsetType = UNSET,
    ) -> Page:
        """CreatePage

        Create a new page in a document

        Args:
            image: The `FileLike` scalar type represents a reference to a big file storage previously created by the user n a datalayer (required)
            index: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
            document: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
            ocr_result:  (required)
            content: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.

        Returns:
            Page
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["image"] = image
        _input["index"] = index
        _input["document"] = document
        _input["ocrResult"] = ocr_result
        if content is not UNSET:
            _input["content"] = content
        variables["input"] = _input
        return self.execute(CreatePageMutation, variables).create_page

    async def aget_file(self, id: IDCoercible) -> File:
        """GetFile


        Args:
            id (ID): The unique identifier of an object

        Returns:
            File
        """
        variables: dict[str, builtins.object] = {}
        variables["id"] = id
        return (await self.aexecute(GetFileQuery, variables)).file

    def get_file(self, id: IDCoercible) -> File:
        """GetFile


        Args:
            id (ID): The unique identifier of an object

        Returns:
            File
        """
        variables: dict[str, builtins.object] = {}
        variables["id"] = id
        return self.execute(GetFileQuery, variables).file

    async def asearch_files(
        self,
        search: str | None | UnsetType = UNSET,
        values: list[IDCoercible] | None | UnsetType = UNSET,
    ) -> tuple[SearchFilesQueryOptions, ...]:
        """SearchFiles


        Args:
            search (str | None, optional): No description.
            values (list[ID] | None, optional): No description.

        Returns:
            list[SearchFilesQueryFiles]
        """
        variables: dict[str, builtins.object] = {}
        if search is not UNSET:
            variables["search"] = search
        if values is not UNSET:
            variables["values"] = values
        return (await self.aexecute(SearchFilesQuery, variables)).options

    def search_files(
        self,
        search: str | None | UnsetType = UNSET,
        values: list[IDCoercible] | None | UnsetType = UNSET,
    ) -> tuple[SearchFilesQueryOptions, ...]:
        """SearchFiles


        Args:
            search (str | None, optional): No description.
            values (list[ID] | None, optional): No description.

        Returns:
            list[SearchFilesQueryFiles]
        """
        variables: dict[str, builtins.object] = {}
        if search is not UNSET:
            variables["search"] = search
        if values is not UNSET:
            variables["values"] = values
        return self.execute(SearchFilesQuery, variables).options

    async def awatch_files(
        self, dataset: IDCoercible | None | UnsetType = UNSET
    ) -> AsyncIterator[WatchFilesSubscriptionFiles]:
        """WatchFiles

        Subscribe to real-time file updates

        Args:
            dataset (ID | None, optional): No description.

        Returns:
            WatchFilesSubscriptionFiles
        """
        variables: dict[str, builtins.object] = {}
        if dataset is not UNSET:
            variables["dataset"] = dataset
        async for event in self.asubscribe(WatchFilesSubscription, variables):
            yield event.files

    def watch_files(
        self, dataset: IDCoercible | None | UnsetType = UNSET
    ) -> Iterator[WatchFilesSubscriptionFiles]:
        """WatchFiles

        Subscribe to real-time file updates

        Args:
            dataset (ID | None, optional): No description.

        Returns:
            WatchFilesSubscriptionFiles
        """
        variables: dict[str, builtins.object] = {}
        if dataset is not UNSET:
            variables["dataset"] = dataset
        for event in self.subscribe(WatchFilesSubscription, variables):
            yield event.files


CreatePageInput.model_rebuild()
OCRPageResultInput.model_rebuild()
