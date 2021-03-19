from typing import Optional
from pathlib import Path

import jsonschema

from core.message.msg_validator import MessageValidator
import core.logging.logger_constants as log_const
from core.logging.logger_utils import log

from saf_jsonschemer.schemer import JsonSchemer

schema_root = Path(__file__).parent / 'schemas'

default_schemer = JsonSchemer(schema_root)


def print_jsonschema_error(ex: jsonschema.ValidationError):
    """
    In consistence with SmartAppFromMessage.print_validation_error
    """
    params = {
        log_const.KEY_NAME: log_const.EXCEPTION_VALUE
    }
    if ex.validator == "type":
        params["required_field_type"] = ex.validator_value
        params["required_field"] = ex.path[0]
        msg = (
            "Payload validation error: Expected '%(required_field)s'"
            " of type '%(required_field_type)s'"
        )
    elif ex.validator == "required":
        params["required_field"] = ex.validator_value
        msg = (
            "Payload validation error: Required field "
            "'%(required_field)s' is missing"
        )
    else:
        msg = f"Message validation error: Format is wrong: {ex.message}"
    log(msg, params=params, level="ERROR")


class ByNameMessageValidator(MessageValidator):
    def __init__(self, name_to_schema=None, direct_pass=True):
        self.name_to_schema = {} if name_to_schema is None else name_to_schema
        self.direct_pass = direct_pass

    def _get_schema_by_message(self, message_name: str) -> Optional[str]:
        message_name = message_name.lower()
        if message_name in self.name_to_schema:
            return self.name_to_schema[message_name]
        if self.direct_pass:
            if message_name in default_schemer.schema_values:
                return message_name
        return None

    def validate(self, message_name: str, payload: dict):
        print(f'\n\n\n\t- validate {message_name}\n{payload}\n\n\n')
        schema_name = self._get_schema_by_message(message_name)
        if schema_name is not None:
            try:
                default_schemer.validate(payload, schema_name)
            except jsonschema.ValidationError as ex:
                print_jsonschema_error(ex)
                return False
        return True
