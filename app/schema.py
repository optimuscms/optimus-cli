import os
import json
import jsonschema


class ConfigParser():

    def parse(self, config: dict) -> dict:
        self._validate_config(config)

        return self._merge_default_settings(config)

    def _validate_config(self, config: dict) -> None:
        jsonschema.validate(
            config,
            self._get_config_schema(config),
        )

    def _get_config_schema(self, config: dict) -> dict:
        pass

    def _merge_default_settings(self, config: dict) -> dict:
        pass


class ModuleConfigParser(ConfigParser):

    def _get_config_schema(self, config: dict) -> dict:
        file_path = os.path.join(
            os.path.dirname(__file__),
            'schema/module_config.json'
        )

        with open(file_path, 'r') as schema_file:
            return json.loads(schema_file.read())

    def _merge_default_settings(self, config: dict) -> dict:
        if 'fields' not in config:
            config['fields'] = []

        # Field defaults

        for field in enumerate(config['fields']):
            if 'label' not in field:
                field['label'] = field['name']

            if 'show_on_admin_index' not in field:
                field['show_on_admin_index'] = False

            default_rules = {
                'required': False,
                'nullable': False,
            }

            if 'rules' not in field:
                field['rules'] = default_rules
            else:
                for rule_key in default_rules:
                    if rule_key not in field['rules']:
                        field['rules'][rule_key] = default_rules[rule_key]

            # Type specific defaults

            if field['type'] == 'media':
                if 'conversions' not in field['options']:
                    field['options']['conversions'] = []

        # Feature defaults

        if 'features' not in config:
            config['features'] = []

        for feature in enumerate(config['features']):
            if 'options' not in feature['options']:
                feature['options'] = {}

            options = feature['options']

            if (
                feature['type'] == 'sort' and
                'order_column_name' not in options
            ):
                options['order_column_name'] = 'order'

            if feature['type'] == 'media':
                for media_group in enumerate(options['media_groups']):
                    if 'conversions' not in media_group:
                        media_group['conversions'] = []

                if 'conversions' not in options:
                    options['conversions'] = []

            if (
                feature['type'] == 'draft' and
                'published_at_column_name' not in options
            ):
                options['published_at_column_name'] = 'published_at'

        return config


class PageTemplateConfigParser(ConfigParser):

    def _get_config_schema(self, config: dict) -> dict:
        file_path = os.path.join(
            os.path.dirname(__file__),
            'schema/page_template_config.json'
        )

        with open(file_path, 'r') as schema_file:
            return json.loads(schema_file.read())

    def _merge_default_settings(self, config: dict) -> dict:
        if 'name' not in config:
            config['name'] = self.__convert_to_title(config['id'])

        if 'fields' not in config:
            config['fields'] = []

        # Field defaults

        for field in enumerate(config['fields']):
            if 'label' not in field:
                config['label'] = self.__convert_to_title(field['name'])

            default_rules = {
                'required': False,
                'nullable': False
            }

            if 'rules' not in field:
                field['rules'] = default_rules
            else:
                for rule_key in default_rules:
                    if rule_key not in field['rules']:
                        field['rules'][rule_key] = default_rules[rule_key]

            # Type specific defaults

            if field['type'] == 'media':
                if 'conversions' not in field['options']:
                    field['options']['conversions'] = []

        return config

    def __convert_to_title(self, string: str):
        for separator in ['-', '_']:
            string = string.replace(separator, ' ')

        return string.title()
