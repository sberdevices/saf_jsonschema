from typing import Iterable, Optional
import os
import json
import yaml
from pathlib import Path
import jsonschema


class SchemaStaticResolver:
    """
    Allows to use JSON-Schema repo with many cross-linked schema files.
    jsonschema.RefResolver is referrer-dependent, while this class isn't.
    """

    def __init__(self, schema_root: Path, schema_folders: Optional[Iterable[Path]] = None):
        self.schema_urls, self.schema_values = dict(), dict()
        if schema_folders is None:
            self._index_schemas_folder(schema_root)
        else:
            self._load_schemas_repo(schema_root, schema_folders)

    def _index_schemas_folder(self, schema_folder: Path):
        """
        Add local schema instances from some folder.

        :param schema_folder: path to schema repo
        """
        # print(f"{schema_folder}:")
        for dir, _, files in os.walk(schema_folder):
            for file in files:
                schema_doc = None
                schema_path = Path(dir) / Path(file)
                if file.endswith(".json"):
                    with open(schema_path) as schema_file:
                        schema_doc = json.load(schema_file)
                if file.endswith(".yaml"):
                    with open(schema_path) as schema_file:
                        schema_doc = yaml.load(schema_file)
                if schema_doc is not None:
                    schema_url = f"/{schema_path}"
                    name = schema_path.stem
                    if name in self.schema_urls:
                        raise ValueError(
                            f"Double name {name}"
                            f" old from {self.schema_urls[name]}"
                            f" new from {schema_url}"
                        )
                    self.schema_urls[name] = schema_url
                    self.schema_values[name] = schema_doc
                    # print(f"Added '{name}' from {schema_url}")

    def _load_schemas_repo(self, schema_root: Path, schema_folders: Iterable[Path]):
        """
        Add local schema instances to a storage.

        :param schema_root: path to schema repo
        :param schema_root: an iterable of repo folder names
        """
        schema_root = Path(os.path.abspath(schema_root))
        schema_paths = [schema_root / folder for folder in schema_folders]

        for path in schema_paths:
            self._index_schemas_folder(path)

    def validate(self, instance: dict, instance_type: Optional[str] = None):
        """
        Validate an object using given or guessed schema.

        :param instance: object to validate
        :param instance_type: schema name
        """
        assert isinstance(instance, dict)
        if instance_type is None:
            if "type" in instance:
                # Usual nice case
                instance_type = instance["type"]
                # print(f"Instance type explicit: "{instance_type}"")
            else:
                # Take single nested object
                # and use its key as a type name
                assert len(instance) == 1
                instance_type = list(instance.keys())[0]
                instance = instance[instance_type]
                # print(f"Instance type by key: "{instance_type}"")

        schema = self.schema_values[instance_type]
        base_uri = f"{Path(self.schema_urls[instance_type]).parent}/"

        # print("Schema name:", instance_type)
        # print("Schema:", schema)
        # print("Base uri:", base_uri)

        # Resolver can be created only with referrer schema
        # So we need a unique resolver for each schema or data instance
        resolver = jsonschema.RefResolver(base_uri=base_uri, referrer=schema)
        for name in self.schema_values:
            resolver.store[self.schema_urls[name]] = self.schema_values[name]

        jsonschema.validate(instance, schema, resolver=resolver)
