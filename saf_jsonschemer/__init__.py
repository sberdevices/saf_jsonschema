from typing import Optional
from pathlib import Path

from core.message.msg_validator import MessageValidator

from saf_jsonschemer.schemer import JsonSchemer

schema_root = Path(__file__).parent / 'schemas'

schema_folders = (
    'Actions', 'Bubble', 'Cards', 'Common',
    'Styles', 'Suggest', 'SystemMessage',
)
default_schemer = JsonSchemer(schema_root, schema_folders)


class ByNameMessageValidator(MessageValidator):
    def _get_schema_by_message(self, message_name: str) -> Optional[str]:
        if message_name in default_schemer.schema_values:
            return message_name
        return None

    def validate(self, message_name: str, data: dict):
        print(f'\n\n\n\t- ByNameMessageValidator\n\n\n')
        schema_name = self._get_schema_by_message(message_name)
        if schema_name is not None:
            default_schemer.validate(data, schema_name)


class ToClientMessageValidator(MessageValidator):
    def validate(self, message_name: str, data: dict):
        print(f'\n\n\n\t- ToClientMessageValidator\n\n\n')
        default_schemer.validate(data, 'from_nlp_to_client')
