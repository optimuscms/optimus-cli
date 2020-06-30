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


class TemplateParser(object):

    def __init__(self, config_dict: dict):
        self.__config_dict = config_dict

        self.__environment = Environment(
            loader=BaseLoader,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        self.__filters = TemplateFilters()
        self.__helpers = TemplateHelpers(self.__config_dict)

        self.__environment.filters = {
            **self.__environment.filters,
            'camel': self.__filters.camel,
            'kebab': self.__filters.kebab,
            'snake': self.__filters.snake,
            'pascal': self.__filters.pascal,
            'plural': self.__filters.plural,
            'singular': self.__filters.singular
        }

    def render_file(self, file_path: str) -> str:
        """Renders the contents of the file at the provided file path

        :param file_path: the path of the jinja2 file to render
        :return: the rendered template
        """
        with open(file_path, 'r') as template_file:
            template_contents = template_file.read()

        compiled_template = self.__environment.from_string(template_contents)

        return compiled_template.render(
            self.__config_dict,
            in_array=self.__helpers.in_array,
            has_feature=self.__helpers.has_feature,
            get_model_traits=self.__helpers.get_model_traits,
            get_model_parents=self.__helpers.get_model_parents
        )

    def render_string(self, to_render: str) -> str:
        """Renders the provided string as a jinja2 template

        :param to_render: the string to render
        :return: the rendered string
        """
        compiled_string = self.__environment.from_string(to_render)

        return compiled_string.render(self.__config_dict)


class TemplateFilters(object):

    def __init__(self):
        self.__camel_cache = {}
        self.__kebab_cache = {}
        self.__snake_cache = {}
        self.__pascal_cache = {}
        self.__plural_cache = {}
        self.__singular_cache = {}

    def plural(self, text: str) -> str:
        if text in self.__plural_cache:
            return self.__plural_cache[text]

        plural_text = inflection.pluralize(text)

        self.__plural_cache[text] = plural_text

        return plural_text

    def singular(self, text: str) -> str:
        if text in self.__singular_cache:
            return self.__singular_cache[text]

        singular_text = inflection.singularize(text)

        self.__singular_cache[text] = singular_text

        return singular_text

    def camel(self, text: str) -> str:
        if text in self.__camel_cache:
            return self.__camel_cache[text]

        words = text.lower().split(' ')

        camel_text = words[0] + ''.join(
            word.capitalize() for word in words[1:]
        )

        self.__camel_cache[text] = camel_text

        return camel_text

    def kebab(self, text: str) -> str:
        if text in self.__kebab_cache:
            return self.__kebab_cache[text]

        kebab_text = text.lower().replace(' ', '-')

        self.__kebab_cache[text] = kebab_text

        return kebab_text

    def pascal(self, text: str) -> str:
        if text in self.__pascal_cache:
            return self.__pascal_cache[text]

        pascal_text = text.replace(' ', '')

        self.__pascal_cache[text] = pascal_text

        return pascal_text

    def snake(self, text: str) -> str:
        if text in self.__snake_cache:
            return self.__snake_cache[text]

        snake_text = text.lower().replace(' ', '_')

        self.__snake_cache[text] = snake_text

        return snake_text


class TemplateHelpers(object):
    def __init__(self, config_dict: dict):
        self.__config_dict = config_dict
        self.__feature_cache = {}

    def get_model_parents(self):
        parents = []

        if self.has_feature('menu'):
            parents.append('Linkable')
            parents.append('SynchronisesMenuItemUrls')

        if self.has_feature('sort'):
            parents.append('Sortable')

        return ','.join(parents)

    def get_model_traits(self):
        traitMap = {
            'draft': 'Draftable',
            'slug': 'HasSlug',
            'media': 'HasMedia',
            'seo': 'HasSeoFields',
            'menu': 'LinkableTrait',
            'sort': 'SortableTrait'
        }

        traits = []

        for (feature, trait) in traitMap.items():
            if self.has_feature(feature):
                traits.append(trait)

        return ','.join(traits)

    def has_feature(self, feature_type: str) -> bool:
        if feature_type in self.__feature_cache:
            return self.__feature_cache[feature_type]
    
        matching_features = list(
            filter(lambda feature: feature['type'] ==
                   feature_type, self.__config_dict['features'])
        )

        module_has_feature = len(matching_features) != 0

        self.__feature_cache[feature_type] = module_has_feature

        return module_has_feature

    def in_array(self, text: str, array: list) -> bool:
        return text in array
