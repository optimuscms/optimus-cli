import json
import jsonschema
import os
import re
import inflection

from functools import reduce

from jinja2 import BaseLoader
from jinja2 import Environment
from jinja2 import Template
from jinja2 import nodes
from jinja2.ext import Extension

class ConfigParser():

    def parse(self, config: dict) -> dict:
        self._validate_config(config)

        return self._merge_default_settings(config)

    def _validate_config(self, config: dict) -> None:
        jsonschema.validate(config, self._get_config_schema())

    def _get_config_schema(self) -> dict:
        pass

    def _merge_default_settings(self, config: dict) -> dict:
        pass

class ModuleConfigParser(ConfigParser):

    def _get_config_schema(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'name': { 'type': 'string' },
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
                            'name': { 'type': 'string' },
                            'rules': {
                                'type': 'object',
                                'properties': {
                                    'required': { 'type': 'boolean' },
                                    'nullable': { 'type': 'boolean' },
                                },
                            },
                        },
                        'required': ['name'],
                        'if': {
                            'properties': { 
                                'type': { 'const': 'media' },
                            },
                        },
                        'then': {
                            'properties': {
                                'options': {
                                    'type': 'object',
                                    'properties': {
                                        'media_group': { 'type': 'string' },
                                        'conversions': {
                                            'type': 'array',
                                            'items': { 'type': 'string' },
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
                                        'type': { 'const': 'sort' },
                                    },
                                },
                                'then': {
                                    'properties': {
                                        'options': {
                                            'type': 'object',
                                            'properties': {
                                                'order_column_name': { 'type': 'string' },
                                            },
                                        },
                                    },
                                    'required': ['options'],
                                },
                            },
                            {
                                'if': {
                                    'properties': {
                                        'type': { 'const': 'slug' },
                                    },
                                },
                                'then': {
                                    'properties': {
                                        'options': {
                                            'type': 'object',
                                            'properties': {
                                                'generate_from_field': { 'type': 'string' },
                                                'save_to_field': { 'type': 'string' },
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
                                        'type': { 'const': 'media' },
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
                                                            'name': { 'type': 'string' },
                                                            'conversions': {
                                                                'type': 'array',
                                                                'items': { 'type': 'string' },
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
                                                            'name': { 'type': 'string' },
                                                            'width': { 'type': 'integer' },
                                                            'height': { 'type': 'integer' },
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
                                        'type': { 'const': 'draft' },
                                    },
                                },
                                'then': {
                                    'properties': {
                                        'options': {
                                            'type': 'object',
                                            'properties': {
                                                'published_at_column_name': { 'type': 'string' },
                                            },
                                        },
                                    },
                                },
                            },
                            {
                                'if': {
                                    'properties': {
                                        'type': { 'const': 'menu' },
                                    },
                                },
                                'then': {
                                    'properties': {
                                        'options': {
                                            'type': 'object',
                                            'properties': {
                                                'url_field': { 'type': 'string' },
                                                'label_field': { 'type': 'string' },
                                                'search_query_field': { 'type': 'string' },
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
        # TODO: Merge the default settings into the config

        return config

class PageTemplateConfigParser(ConfigParser):

    def _get_config_schema(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'id': { 'type': 'string' },
                'name': { 'type': 'string' },
                'fields': {
                    'type': 'array',
                    'items': {
                        'oneOf': [
                            {
                                'type': 'object',
                                'properties': {
                                    'type': { 'const': 'text' },
                                    'name': { 'type': 'string' },
                                    'label': { 'type': 'string' },
                                    'rules': {
                                        'type': 'object',
                                        'properties': {
                                            'required': { 'type': 'boolean' },
                                            'nullable': { 'type': 'boolean' },
                                        },
                                    },
                                },
                                'required': ['name'],
                            },
                            {
                                'type': 'object',
                                'properties': {
                                    'type': { 'const': 'textarea' },
                                    'name': { 'type': 'string' },
                                    'label': { 'type': 'string' },
                                    'rules': {
                                        'type': 'object',
                                        'properties': {
                                            'required': { 'type': 'boolean' },
                                            'nullable': { 'type': 'boolean' },
                                        },
                                    },
                                },
                                'required': ['name'],
                            },
                            {
                                'type': 'object',
                                'properties': {
                                    'type': { 'const': 'editor' },
                                    'name': { 'type': 'string' },
                                    'label': { 'type': 'string' },
                                    'rules': {
                                        'type': 'object',
                                        'properties': {
                                            'required': { 'type': 'boolean' },
                                            'nullable': { 'type': 'boolean' },
                                        },
                                    },
                                },
                                'required': ['name'],
                            },
                            {
                                'type': 'object',
                                'properties': {
                                    'type': { 'const': 'date' },
                                    'name': { 'type': 'string' },
                                    'label': { 'type': 'string' },
                                    'rules': {
                                        'type': 'object',
                                        'properties': {
                                            'required': { 'type': 'boolean' },
                                            'nullable': { 'type': 'boolean' },
                                        },
                                    },
                                },
                                'required': ['name'],
                            },
                            {
                                'type': 'object',
                                'properties': {
                                    'type': { 'const': 'media' },
                                    'name': { 'type': 'string' },
                                    'label': { 'type': 'string' },
                                    'rules': {
                                        'type': 'object',
                                        'properties': {
                                            'required': { 'type': 'boolean' },
                                            'nullable': { 'type': 'boolean' },
                                        },
                                    },
                                    'options': {
                                        'type': 'object',
                                        'properties': {
                                            'media_group': { 'type': 'string' },
                                            'conversions': {
                                                'type': 'array',
                                                'items': {
                                                    'type': 'string',
                                                },
                                            },
                                        },
                                        'required': ['media_group'],
                                    },
                                },
                                'required': ['name', 'options'],
                            },
                        ],
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

        for i, field in enumerate(config['fields']):
            if 'label' not in field:
                config['label'] = self.__convert_to_title(field['name'])
            
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

        return config

    def __convert_to_title(self, string: str):
        for separator in ['-', '_']:
            string = string.replace(separator, ' ')

        return string.title()

class TemplateParser(object):
    def __init__(self, file_path: str):
        self.__environment = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            loader=BaseLoader
        )

        self.__filters = TemplateFilters()

        self.__environment.filters = {
            **self.__environment.filters,

            'camel': self.__filters.camel,
            'kebab': self.__filters.kebab,
            'snake': self.__filters.snake,
            'pascal': self.__filters.pascal,
            'plural': self.__filters.plural,
            'singular': self.__filters.singular
        }

        with open(file_path, 'r') as template_file:
            self.__data = json.loads(template_file.read())

    def render_file(self, file_path: str) -> str:
        """Renders the contents of the file at the provided file path

        :param file_path: the path of the handlebars file to render
        :return: the rendered template
        """
        with open(file_path, 'r') as template_file:
            template_contents = template_file.read()

        compiled_template = self.__environment.from_string(template_contents)

        return compiled_template.render(
            self.__data,
            has_feature=self.__has_feature_helper
        )

    def render_string(self, to_render: str) -> str:
        """Renders the provided string as a handlebars template

        :param to_render: the string to render
        :return: the rendered string
        """
        compiled_string = Template(to_render)

        return compiled_string.render(self.__data)

    def get_template_data(self) -> dict:
        """Retrieves the template data (JSON) provided by the user

        :return: the compiled handlebars template
        """
        return self.__data

    def __has_feature_helper(self, feature_type):
        matching_features = list(
            filter(lambda feature: feature['type'] ==
                   feature_type, self.__data['features'])
        )

        return len(matching_features) != 0


class TemplateFilters(object):
    def __init__(self):
        self.__camel_cache = {}
        self.__kebab_cache = {}
        self.__snake_cache = {}
        self.__pascal_cache = {}
        self.__plural_cache = {}
        self.__singular_cache = {}

    def plural(self, text):
        if text in self.__plural_cache:
            return self.__plural_cache[text]

        plural_text = inflection.pluralize(text)

        self.__plural_cache[text] = plural_text

        return plural_text

    def singular(self, text):
        if text in self.__singular_cache:
            return self.__singular_cache[text]

        singular_text = inflection.singularize(text)

        self.__singular_cache[text] = singular_text

        return singular_text

    def camel(self, text):
        if text in self.__camel_cache:
            return self.__camel_cache[text]

        words = text.lower().split(' ')

        camel_text = words[0] + ''.join(
            word.capitalize() for word in words[1:]
        )

        self.__camel_cache[text] = camel_text

        return camel_text

    def kebab(self, text):
        if text in self.__kebab_cache:
            return self.__kebab_cache[text]

        kebab_text = text.lower().replace(' ', '-')

        self.__kebab_cache[text] = kebab_text

        return kebab_text

    def pascal(self, text):
        if text in self.__pascal_cache:
            return self.__pascal_cache[text]

        pascal_text = text.replace(' ', '')

        self.__pascal_cache[text] = pascal_text

        return pascal_text

    def snake(self, text):
        if text in self.__snake_cache:
            return self.__snake_cache[text]

        snake_text = text.lower().replace(' ', '_')

        self.__snake_cache[text] = snake_text

        return snake_text
