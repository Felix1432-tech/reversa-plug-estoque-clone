from app.connectors.base import BaseConnector

CONNECTOR_REGISTRY: dict[str, type[BaseConnector]] = {}


def register_connector(distributor_type: str):
    def decorator(cls: type[BaseConnector]):
        CONNECTOR_REGISTRY[distributor_type] = cls
        return cls
    return decorator


def get_connector(distributor_type: str, credentials: dict, settings: dict | None = None) -> BaseConnector:
    cls = CONNECTOR_REGISTRY.get(distributor_type)
    if cls is None:
        raise ValueError(f"No connector registered for type: {distributor_type}")
    return cls(credentials=credentials, settings=settings)
