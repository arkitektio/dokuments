from .dokuments import Dokuments

try:
    from .arkitekt import DokumentsService
    from .rekuest import structure_reg
except ImportError:
    pass


__all__ = [
    "Dokuments",
    "DokumentsService",
    "structure_reg",
]
