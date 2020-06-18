import json
import os
import re

from jinja2 import Template
from jinja2 import nodes
from jinja2.ext import Extension


class TemplateParser(object):
    def __init__(self, file_path: str):

        with open(file_path, 'r') as template_file:
            self.__data = json.loads(template_file.read())

    def render_file(self, file_path: str) -> str:
        """Renders the contents of the file at the provided file path

        :param file_path: the path of the handlebars file to render
        :return: the rendered template
        """
        with open(file_path, 'r') as template_file:
            template_contents = template_file.read()

        compiled_template = Template(
            template_contents,
            trim_blocks=True,
            lstrip_blocks=True
        )

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
