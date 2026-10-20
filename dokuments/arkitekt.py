import json
import os
from dokuments.dokuments import Dokuments
from dokuments.rath import DokumentsRath, DokumentsLinkComposition
from fakts_next.contrib.rath.auth import FaktsAuthLink
from rath.links.split import SplitLink
from fakts_next.contrib.rath.aiohttp import FaktsAIOHttpLink
from fakts_next.contrib.rath.graphql_ws import FaktsGraphQLWSLink
from graphql import OperationType
from fakts_next import Fakts


from arkitekt_next.service_registry import (
    BaseArkitektService,
    Params,
    get_default_service_registry,
)
from fakts_next.models import Requirement


def build_relative_path(*path: str) -> str:
    return os.path.join(os.path.dirname(__file__), *path)


class DokumentsService(BaseArkitektService):
    """Dokuments Service"""

    def get_service_name(self):
        return "dokuments"

    def build_service(self, fakts: Fakts, params: Params):
        return Dokuments(
            rath=DokumentsRath(
                link=DokumentsLinkComposition(
                    auth=FaktsAuthLink(fakts=fakts),
                    split=SplitLink(
                        left=FaktsAIOHttpLink(
                            fakts_group="dokuments",
                            fakts=fakts,
                            endpoint_url="FAKE_URL",
                        ),
                        right=FaktsGraphQLWSLink(
                            fakts_group="dokuments",
                            fakts=fakts,
                            ws_endpoint_url="FAKE_URL",
                        ),
                        split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                    ),
                )
            )
        )

    def get_requirements(self):
        return [
            Requirement(
                key="dokuments",
                service="live.arkitekt.dokuments",
                description="An instance of ArkitektNext dokuments to retrieve graphs from",
            )
        ]

    def get_graphql_schema(self):
        schema_graphql_path = build_relative_path("api", "schema.graphql")
        with open(schema_graphql_path) as f:
            return f.read()

    def get_turms_project(self):
        turms_prject = build_relative_path("api", "project.json")
        with open(turms_prject) as f:
            return json.loads(f.read())


get_default_service_registry().register(DokumentsService())
