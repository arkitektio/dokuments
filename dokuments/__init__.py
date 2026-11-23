# The service is declared with arkitekt-spec, a core dependency: it is always there.
from .arkitekt import dokuments as dokuments_service
from .dokuments import Dokuments

__all__ = ["Dokuments", "dokuments_service"]
