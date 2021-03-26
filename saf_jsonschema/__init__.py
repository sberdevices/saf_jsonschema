from typing import Optional, Dict
from pathlib import Path

import jsonschema

from core.message.msg_validator import MessageValidator
import core.logging.logger_constants as log_const
from core.logging.logger_utils import log

from saf_jsonschema.resolver import SchemaStaticResolver

__all__ = [
    'default_static_resolver',
    'print_jsonschema_error',
    'ByNameMessageValidator',
]

schema_root = Path(__file__).parent / 'schemas'

default_static_resolver = SchemaStaticResolver(schema_root)


def print_jsonschema_error(ex: jsonschema.ValidationError, validator_name: Optional[str] = None):
    """
    In consistence with SmartAppFromMessage.print_validation_error
    """
    params = {
        log_const.KEY_NAME: log_const.EXCEPTION_VALUE
    }
    if ex.validator == "type":
        params["required_field_type"] = ex.validator_value
        params["required_field"] = ".".join(ex.path)
        msg = (
            "Payload validation error: Expected '%(required_field)s'"
            " of type '%(required_field_type)s'"
        )
    elif ex.validator == "required":
        params["required_field"] = ".".join([*ex.path, *ex.validator_value])
        msg = (
            "Payload validation error: Required field "
            "'%(required_field)s' is missing"
        )
    else:
        msg = f"Message validation error: Format is wrong: {ex.message}"
    if validator_name is not None:
        msg += f" by validator {validator_name}"
    log(msg, params=params, level="ERROR")


class ByNameMessageValidator(MessageValidator):
    """
    Allows to validate SmartAppFromMessage & SmartAppToMessage with JSON-Schema files.
    Uses pre-defined schemas by default, but the behaviour can be easily changed with
    constructor settings and/or overriding the _get_schema_by_message.
    """
    def __init__(
            self, name: str, name_to_schema: Optional[Dict[str, str]] = None, direct_pass: bool = True,
            static_resolver: Optional[SchemaStaticResolver] = None,
    ):
        self.name = name
        self.name_to_schema = {} if name_to_schema is None else name_to_schema
        self.direct_pass = direct_pass
        self.static_resolver = default_static_resolver if static_resolver is None else static_resolver

    def _get_schema_by_message(self, message_name: str) -> Optional[str]:
        message_name = message_name.lower()
        if message_name in self.name_to_schema:
            return self.name_to_schema[message_name]
        if self.direct_pass:
            if message_name in default_static_resolver.schema_values:
                return message_name
        return None

    def validate(self, message_name: str, payload: dict):
        schema_name = self._get_schema_by_message(message_name)
        if schema_name is not None:
            try:
                default_static_resolver.validate(payload, schema_name)
            except jsonschema.ValidationError as ex:
                print_jsonschema_error(ex, self.name)
                return False
        return True
