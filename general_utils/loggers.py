import logging.config
from logging import Logger

from general_utils.utils import get_base_dir


def get_logger(name: str, with_file: bool = True) -> Logger:
    log_dir = get_base_dir() / "logs"
    log_dir.mkdir(exist_ok=True, parents=True)
    log_path = log_dir / f"{name}.log"

    level = "DEBUG"

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[{asctime}] {levelname:^7} | def {funcName}() | {message}",
                "datefmt": "%x %X",
                "style": "{",
            },
        },
        "handlers": {
            "file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": log_path.as_posix(),
                "encoding": "utf-8",
                "formatter": "verbose",
            },
            "console": {
                "level": level,
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "root": {
            "level": "DEBUG",
        },
        "loggers": {
            name: {
                "handlers": ["file", "console"] if with_file else ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }
    logging.config.dictConfig(config)

    return logging.getLogger(name)


LOGGER = get_logger("tg", with_file=False)
