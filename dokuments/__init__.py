from .dokuments import Dokuments

__all__ = ["Dokuments"]

# Marks every type dokuments sends by id, so an app using `Dokuments` finds them.
from . import structures as _structures  # noqa: E402, F401
