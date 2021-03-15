from typing import Optional
from pathlib import Path

import jsonschema

from core.message.msg_validator import MessageValidator
import core.logging.logger_constants as log_const
from core.logging.logger_utils import log

from saf_jsonschemer.schemer import JsonSchemer

schema_root = Path(__file__).parent / 'schemas'

schema_folders = (
    'Actions', 'Bubble', 'Cards', 'Common',
    'Styles', 'Suggest', 'SystemMessage',
)
default_schemer = JsonSchemer(schema_root, schema_folders)


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
    def _get_schema_by_message(self, message_name: str) -> Optional[str]:
        if message_name in default_schemer.schema_values:
            return message_name
        return None

    def validate(self, message_name: str, data: dict):
        schema_name = self._get_schema_by_message(message_name)
        if schema_name is not None:
            try:
                default_schemer.validate(data, schema_name)
            except jsonschema.ValidationError as ex:
                print_jsonschema_error(ex)
                return False


class ToClientMessageValidator(MessageValidator):
    def validate(self, message_name: str, data: dict):
        try:
            default_schemer.validate(data, 'from_nlp_to_client')
        except jsonschema.ValidationError as ex:
            print_jsonschema_error(ex)
            return False

