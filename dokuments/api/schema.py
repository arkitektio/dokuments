import builtins
from dokuments.scalars import FileLike
from dokuments.traits import HasDownloadAccessor
from enum import Enum
from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from rath.scalars import ID, IDCoercible
from typing import AsyncIterator, Iterable, Iterator, Literal


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


class RequestFileAccessInput(BaseModel):
    """No documentation"""

    store: ID
    duration: int | None = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestFileUploadInput(BaseModel):
    """No documentation"""

    file_name: str = Field(
        validation_alias=AliasChoices("file_name", "fileName"),
        serialization_alias="fileName",
    )
    datalayer: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class Credentials(BaseModel):
    """Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)"""

    typename: Literal["Credentials"] = Field(
        alias="__typename", default="Credentials", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    status: str
    secret_key: str = Field(alias="secretKey")
    bucket: str
    key: str
    session_token: str = Field(alias="sessionToken")
    store: str
    model_config = ConfigDict(frozen=True)

    class Meta:
        """Meta class for Credentials"""

        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n  __typename\n}"
        name = "Credentials"
        type = "Credentials"


class AccessCredentials(BaseModel):
    """Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)"""

    typename: Literal["AccessCredentials"] = Field(
        alias="__typename", default="AccessCredentials", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    bucket: str
    key: str
    session_token: str = Field(alias="sessionToken")
    path: str
    model_config = ConfigDict(frozen=True)

    class Meta:
        """Meta class for AccessCredentials"""

        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n  __typename\n}"
        name = "AccessCredentials"
        type = "AccessCredentials"


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


class BigFileStore(HasDownloadAccessor, BaseModel):
    """No documentation"""

    typename: Literal["BigFileStore"] = Field(
        alias="__typename", default="BigFileStore", exclude=True
    )
    id: ID
    key: str
    bucket: str
    path: str
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)

    class Meta:
        """Meta class for BigFileStore"""

        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}"
        name = "BigFileStore"
        type = "BigFileStore"


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
    store: BigFileStore
    model_config = ConfigDict(frozen=True)

    class Meta:
        """Meta class for File"""

        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment File on File {\n  id\n  store {\n    ...BigFileStore\n    __typename\n  }\n  __typename\n}"
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

        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment File on File {\n  id\n  store {\n    ...BigFileStore\n    __typename\n  }\n  __typename\n}\n\nmutation from_file_like($input: FromFileLike!) {\n  fromFileLike(input: $input) {\n    ...File\n    __typename\n  }\n}"


class RequestFileUploadMutation(BaseModel):
    """No documentation found for this operation."""

    request_file_upload: Credentials = Field(alias="requestFileUpload")
    "Request credentials to upload a new file"

    class Arguments(BaseModel):
        """Arguments for RequestFileUpload"""

        input: RequestFileUploadInput

    class Meta:
        """Meta class for RequestFileUpload"""

        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n  __typename\n}\n\nmutation RequestFileUpload($input: RequestFileUploadInput!) {\n  requestFileUpload(input: $input) {\n    ...Credentials\n    __typename\n  }\n}"


class RequestFileAccessMutation(BaseModel):
    """No documentation found for this operation."""

    request_file_access: AccessCredentials = Field(alias="requestFileAccess")
    "Request credentials to access a file"

    class Arguments(BaseModel):
        """Arguments for RequestFileAccess"""

        input: RequestFileAccessInput

    class Meta:
        """Meta class for RequestFileAccess"""

        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n  __typename\n}\n\nmutation RequestFileAccess($input: RequestFileAccessInput!) {\n  requestFileAccess(input: $input) {\n    ...AccessCredentials\n    __typename\n  }\n}"


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

        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment File on File {\n  id\n  store {\n    ...BigFileStore\n    __typename\n  }\n  __typename\n}\n\nquery GetFile($id: ID!) {\n  file(id: $id) {\n    ...File\n    __typename\n  }\n}"


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

        document = "query SearchFiles($search: String, $values: [ID!]) {\n  options: files(filters: {search: $search, ids: $values}) {\n    value: id\n    label: name\n    __typename\n  }\n}"


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

        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment File on File {\n  id\n  store {\n    ...BigFileStore\n    __typename\n  }\n  __typename\n}\n\nsubscription WatchFiles($dataset: ID) {\n  files(dataset: $dataset) {\n    create {\n      ...File\n      __typename\n    }\n    delete\n    update {\n      ...File\n      __typename\n    }\n    __typename\n  }\n}"


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

    async def arequest_file_upload(self, file_name: str, datalayer: str) -> Credentials:
        """RequestFileUpload

        Request credentials to upload a new file

        Args:
            file_name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
            datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)

        Returns:
            Credentials
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["fileName"] = file_name
        _input["datalayer"] = datalayer
        variables["input"] = _input
        return (
            await self.aexecute(RequestFileUploadMutation, variables)
        ).request_file_upload

    def request_file_upload(self, file_name: str, datalayer: str) -> Credentials:
        """RequestFileUpload

        Request credentials to upload a new file

        Args:
            file_name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
            datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)

        Returns:
            Credentials
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["fileName"] = file_name
        _input["datalayer"] = datalayer
        variables["input"] = _input
        return self.execute(RequestFileUploadMutation, variables).request_file_upload

    async def arequest_file_access(
        self, store: IDCoercible, duration: int | None | UnsetType = UNSET
    ) -> AccessCredentials:
        """RequestFileAccess

        Request credentials to access a file

        Args:
            store: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
            duration: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.

        Returns:
            AccessCredentials
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["store"] = store
        if duration is not UNSET:
            _input["duration"] = duration
        variables["input"] = _input
        return (
            await self.aexecute(RequestFileAccessMutation, variables)
        ).request_file_access

    def request_file_access(
        self, store: IDCoercible, duration: int | None | UnsetType = UNSET
    ) -> AccessCredentials:
        """RequestFileAccess

        Request credentials to access a file

        Args:
            store: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
            duration: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.

        Returns:
            AccessCredentials
        """
        variables: dict[str, builtins.object] = {}
        _input: dict[str, builtins.object] = {}
        _input["store"] = store
        if duration is not UNSET:
            _input["duration"] = duration
        variables["input"] = _input
        return self.execute(RequestFileAccessMutation, variables).request_file_access

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
