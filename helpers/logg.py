import logging
import os


def default_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(10)
    return logger

def configure_handlers(logger, log_dir, format = '%(asctime)s\t%(name)s\t%(message)s'):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    full_handler = create_FileHandler(f'{log_dir}full.log', level=10, format=format)
    act_handler = create_FileHandler(f'{log_dir}info.log', level=20, format=format)
    err_handler = create_FileHandler(f'{log_dir}err.log', level=40, format=format)

    for handler in [full_handler, err_handler, act_handler]:
        logger.addHandler(handler)

    return logger

def create_FileHandler(filepath, level, format = '%(asctime)s\t%(name)s\t%(message)s'):
    handler = logging.FileHandler(filepath)
    handler.setLevel(level)
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)

    return handler

def create_StreamHandler(output, level, format = '%(asctime)s\t%(name)s\t%(message)s'):
    handler = logging.StreamHandler(output)
    handler.setLevel(level)
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)

    return handler