import logging


def setup_logging():
    logging.basicConfig(
        filename="portal.log",
        format=  # noqa
        "%(asctime)-3s :: Job Poratl :: %(name)s.%(funcName)s:%(lineno)s :: %(levelname)s :: %(message)s",  # noqa
        level="DEBUG",
    )
