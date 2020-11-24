import json
import jsonschema
import logging
import logging.config
import os
from typing import Dict


def main():
    #  Set up logging config
    dict_log_config = {
        "version": 1,
        "handlers": {
            "fileHandler": {
                "class": "logging.FileHandler",
                "formatter": "Formatter",
                "filename": "validation.log"
            }
        },
        "loggers": {
            "App": {
                "handlers": ["fileHandler"],
                "level": "INFO",
            }
        },
        "formatters": {
            "Formatter": {
                "format": "\n%(message)s\n"
            }
        }
    }

    logging.config.dictConfig(dict_log_config)
    logger = logging.getLogger("App")

    #  Load events from event dir
    events: Dict[str, dict] = {}  # Dict for mapping event filenames to event instances
    for filename in os.listdir('event'):
        with open(os.path.join('event', filename)) as file:
            events[filename] = json.load(file)

    #  Load schemas from schema dir
    schemes: Dict[str, dict] = {}  # Dict for mapping schema filenames (without .schema) to schema instances
    for filename in os.listdir('schema'):
        with open(os.path.join('schema', filename)) as file:
            schemes[filename[:filename.find('.')]] = json.load(file)

    for ix, (event_filename, event) in enumerate(events.items(), start=1):
        if event is None:
            logger.info(f"{ix}. '{event_filename}' has not corresponding json schema!")
        else:
            event_name = event.get('event', None)
        if event_name is None:
            logger.info(f"{ix}. Field 'event' is absent in '{event_filename}'!")
        elif event_name not in schemes:
            logger.info(f"{ix}. {event_filename} has not corresponding json schema!"
                        f" Check the 'event' field in {event_filename}")
        else:
            schema = schemes[event_name]
            try:
                jsonschema.validate(event, schema)
            except jsonschema.exceptions.ValidationError as err:
                logger.info(f"{ix}. Validation error when tried to apply"
                            f" '{event_name}.schema' schema on '{event_filename}'!"
                            f" {err.message}")


if __name__ == '__main__':
    main()