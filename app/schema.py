import json
import jsonschema


class ConfigParser():

    def parse(self, config: dict) -> dict:
        self._validate_config(config)

        return self._merge_default_settings(config)

    def _validate_config(self, config: dict) -> None:
        jsonschema.validate(
            config,
            self._get_config_schema(),
        )

    def _get_config_schema(self) -> dict:
        pass

    def _merge_default_settings(self, config: dict) -> dict:
        pass


class ModuleConfigParser(ConfigParser):

    def _get_config_schema(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'fields': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'type': {
                                'type': 'string',
                                'enum': [
                                    'text',
                                    'textarea',
                                    'editor',
                                    'date',
                                    'media',
                                ],
                            },
                            'name': {'type': 'string'},
                            'label': {'type': 'string'},
                            'rules': {
                                'type': 'object',
                                'properties': {
                                    'required': {'type': 'boolean'},
                                    'nullable': {'type': 'boolean'},
                                },
                            },
                            'show_on_admin_index': {'type': 'boolean'},
                        },
                        'required': ['name'],
                        'if': {
                            'properties': {
                                'type': {'const': 'media'},
                            },
                        },
                        'then': {
                            'properties': {
                                'options': {
                                    'type': 'object',
                                    'properties': {
                                        'media_group': {'type': 'string'},
                                        'conversions': {
                                            'type': 'array',
                                            'items': {'type': 'string'},
                                        },
                                    },
                                    'required': ['media_group'],
                                },
                            },
                            'required': ['name', 'options'],
                        }
                    },
                },
                'features': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'type': {
                                'type': 'string',
                                'enum': [
                                    'sort',
                                    'slug',
                                    'seo',
                                    'media',
                                    'draft',
                                    'menu',
                                ],
                            },
                        },
                        'required': ['type'],
                        'allOf': [
                            {
                                'if': {
                                    'properties': {
                                        'type': {'const': 'sort'},
                                    },
                                },
                                'then': {
                                    'properties': {
                                        'options': {
                                            'type': 'object',
                                            'properties': {
                                                'order_column_name': {'type': 'string'},
                                            },
                                        },
                                    },
                                    'required': ['options'],
                                },
                            },
                            {
                                'if': {
                                    'properties': {
                                        'type': {'const': 'slug'},
                                    },
                                },
                                'then': {
                                    'properties': {
                                        'options': {
                                            'type': 'object',
                                            'properties': {
                                                'generate_from_field': {'type': 'string'},
                                                'save_to_field': {'type': 'string'},
                                            },
                                            'required': [
                                                'generate_from_field',
                                                'save_to_field',
                                            ],
                                        },
                                    },
                                    'required': ['options'],
                                },
                            },
                            {
                                'if': {
                                    'properties': {
                                        'type': {'const': 'media'},
                                    },
                                },
                                'then': {
                                    'properties': {
                                        'options': {
                                            'type': 'object',
                                            'properties': {
                                                'media_groups': {
                                                    'type': 'array',
                                                    'items': {
                                                        'type': 'object',
                                                        'properties': {
                                                            'name': {'type': 'string'},
                                                            'conversions': {
                                                                'type': 'array',
                                                                'items': {'type': 'string'},
                                                            },
                                                        },
                                                        'required': ['name'],
                                                    },
                                                },
                                                'conversions': {
                                                    'type': 'array',
                                                    'items': {
                                                        'type': 'object',
                                                        'properties': {
                                                            'name': {'type': 'string'},
                                                            'width': {'type': 'integer'},
                                                            'height': {'type': 'integer'},
                                                        },
                                                        'required': ['name', 'width', 'height'],
                                                    },
                                                },
                                            },
                                            'required': ['media_groups'],
                                        },
                                    },
                                    'required': ['options'],
                                },
                            },
                            {
                                'if': {
                                    'properties': {
                                        'type': {'const': 'draft'},
                                    },
                                },
                                'then': {
                                    'properties': {
                                        'options': {
                                            'type': 'object',
                                            'properties': {
                                                'published_at_column_name': {'type': 'string'},
                                            },
                                        },
                                    },
                                },
                            },
                            {
                                'if': {
                                    'properties': {
                                        'type': {'const': 'menu'},
                                    },
                                },
                                'then': {
                                    'properties': {
                                        'options': {
                                            'type': 'object',
                                            'properties': {
                                                'url_field': {'type': 'string'},
                                                'label_field': {'type': 'string'},
                                                'search_query_field': {'type': 'string'},
                                            },
                                            'required': [
                                                'url_field',
                                                'label_field',
                                                'search_query_field',
                                            ],
                                        },
                                    },
                                    'required': ['options'],
                                },
                            },
                        ],
                    },
                },
            },
            'required': ['name'],
        }

    def _merge_default_settings(self, config: dict) -> dict:
        if 'fields' not in config:
            config['fields'] = []

        # Field defaults

        for i, field in enumerate(config['fields']):
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

            config['fields'][i] = field

        # Feature defaults

        if 'features' not in config:
            config['features'] = []

        for i, feature in enumerate(config['features']):
            options = {}

            if 'options' in feature:
                options = feature['options']

            if (
                feature['type'] == 'sort' and
                'order_column_name' not in options
            ):
                options['order_column_name'] = 'order'

            if feature['type'] == 'media':
                for j, media_group in enumerate(options['media_groups']):
                    if 'conversions' not in media_group:
                        media_group['conversions'] = []

                    options['media_groups'][j] = media_group

                if 'conversions' not in options:
                    options['conversions'] = []

            if (
                feature['type'] == 'draft' and
                'published_at_column_name' not in options
            ):
                options['published_at_column_name'] = 'published_at'

            feature['options'] = options
            config['features'][i] = feature

        return config


class PageTemplateConfigParser(ConfigParser):

    def _get_config_schema(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'id': {'type': 'string'},
                'name': {'type': 'string'},
                'fields': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'type': {
                                'type': 'string',
                                'enum': [
                                    'text',
                                    'textarea',
                                    'editor',
                                    'date',
                                    'media',
                                ],
                            },
                            'name': {'type': 'string'},
                            'label': {'type': 'string'},
                            'rules': {
                                'type': 'object',
                                'properties': {
                                    'required': {'type': 'boolean'},
                                    'nullable': {'type': 'boolean'},
                                },
                            },
                        },
                        'required': ['name'],
                        'if': {
                            'properties': {
                                'type': {'const': 'media'},
                            },
                        },
                        'then': {
                            'properties': {
                                'options': {
                                    'type': 'object',
                                    'properties': {
                                        'media_group': {'type': 'string'},
                                        'conversions': {
                                            'type': 'array',
                                            'items': {'type': 'string'},
                                        },
                                    },
                                    'required': ['media_group'],
                                },
                            },
                            'required': ['name', 'options'],
                        },
                    },
                },
            },
            'required': ['id'],
        }

    def _merge_default_settings(self, config: dict) -> dict:
        if 'name' not in config:
            config['name'] = self.__convert_to_title(config['id'])

        if 'fields' not in config:
            config['fields'] = []

        # Field defaults

        for i, field in enumerate(config['fields']):
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

            config['fields'][i] = field

        return config

    def __convert_to_title(self, string: str):
        for separator in ['-', '_']:
            string = string.replace(separator, ' ')

        return string.title()
