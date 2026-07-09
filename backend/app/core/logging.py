import logging

from pythonjsonlogger import jsonlogger


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(
        jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")  # type: ignore[attr-defined]
    )
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
