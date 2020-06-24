import json
import os
import re
import inflection

from functools import reduce

from jinja2 import BaseLoader
from jinja2 import Environment
from jinja2 import Template
from jinja2 import nodes
from jinja2.ext import Extension

# Strategy
# ========
# Read file
# Validate contents against schema
# Merge


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
