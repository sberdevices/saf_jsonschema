import os
import json
import yaml
from pathlib import Path
import jsonschema


class JsonSchemer:
    """
    Allows to use JSON-Schema repo with many linked schema files.
    """

    def __init__(self, schema_root, schema_folders=None):
        self.schema_uris, self.schema_values = dict(), dict()
        if schema_folders is None:
            self._index_schemas_folder(schema_root)
        else:
            self._load_schemas_repo(schema_root, schema_folders)

    def _index_schemas_folder(self, schema_folder, schema_ext='.json'):
        """
        Add local schema instances from some folder.

        :param schema_folder: path to schema repo
        :type schema_folder: Path
        :param schema_ext: extension of JSON-schema files
        :type schema_ext: str

        Arguments:
            schema_uris (Dict[str, str]): a map to save schema path by its name
            schema_values (Dict[str, str]): a map to save content path by its name
            schema_folder (str): the local folder of the schemas.
            schema_ext (str): filter files with this extension in the schema_folder
        """
        # print(f'{schema_folder}:')
        for dir, _, files in os.walk(schema_folder):
            for file in files:
                if file.endswith(schema_ext):
                    schema_path = Path(dir) / Path(file)
                    with open(schema_path) as schema_file:
                        schema_doc = json.load(schema_file)
                    key = f'/{schema_path}'
                    name = schema_path.name.replace(schema_ext, '')
                    if name in self.schema_uris:
                        raise ValueError(
                            f'Double name {name}'
                            f' old from {self.schema_uris[name]}'
                            f' new from {key}'
                        )
                    self.schema_uris[name] = key
                    self.schema_values[name] = schema_doc
                    # print(f'Added {name} : {key}')

    def _load_schemas_repo(self, schema_root, schema_folders):
        """
        Add local schema instances to a storage.

        :param schema_root: path to schema repo
        :type schema_root: Path
        :param schema_root: an iterable of repo folder names
        :type schema_root: Iterable[str]
        """
        schema_root = Path(os.path.abspath(schema_root))
        schema_paths = [schema_root / folder for folder in schema_folders]

        for path in schema_paths:
            self._index_schemas_folder(path)

    def validate(self, instance, instance_type=None):
        """
        Validate an object using given or guessed schema.

        :param instance: object to validate
        :type instance: dict
        :param instance_type: object type name
        :type instance_type: Optional[str]
        """
        assert isinstance(instance, dict)
        if instance_type is None:
            if 'type' in instance:
                # Usual nice case
                instance_type = instance['type']
                # print(f'Instance type explicit: "{instance_type}"')
            else:
                # Take single nested object
                # and use its key as a type name
                assert len(instance) == 1
                instance_type = list(instance.keys())[0]
                instance = instance[instance_type]
                # print(f'Instance type by key: "{instance_type}"')

        schema = self.schema_values[instance_type]
        base_uri = f'{Path(self.schema_uris[instance_type]).parent}/'

        # print('Schema name:', instance_type)
        # print('Schema:', schema)
        # print('Base uri:', base_uri)

        # Resolver can be created only with referrer schema
        # So we need a unique resolver for each schema or data instance
        resolver = jsonschema.RefResolver(base_uri=base_uri, referrer=schema)
        for name in self.schema_values:
            resolver.store[self.schema_uris[name]] = self.schema_values[name]

        jsonschema.validate(instance, schema, resolver=resolver)
