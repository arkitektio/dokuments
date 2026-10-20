from .dokuments import Dokuments

# The service is declared with arkitekt-spec, a core dependency: it is always there.
from .arkitekt import dokuments as dokuments_service

__all__ = ["Dokuments", "dokuments_service"]
