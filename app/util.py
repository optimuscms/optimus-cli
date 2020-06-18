import json
import os
import re
from pybars import Compiler


class TemplateParser(object):
    def __init__(self, file_path: str):
        self.__compiler = Compiler()

        self.__HELPERS = {
            'if-has-feature': self.__if_has_feature_helper,
            'if-not-has-feature': self.__if_not_has_feature_helper,
            'if-type-is': self.__if_type_is_helper,
            'if-not-type-is': self.__if_not_type_is_helper,
            'no-break': self.__no_break_helper,
            'no-trailing-comma': self.__no_trailing_commma_helper,
            'lstrip': self.__left_strip_helper,
            'to-lower': self.__to_lower_helper,
            'v-render': self.__vue_render_helper
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

        compiled_template = self.__compiler.compile(template_contents)

        return compiled_template(self.__data, helpers=self.__HELPERS)

    def render_string(self, to_render: str) -> str:
        """Renders the provided string as a handlebars template

        :param to_render: the string to render
        :return: the rendered string
        """
        compiled_string = self.__compiler.compile(to_render)

        return compiled_string(self.__data, helpers=self.__HELPERS)

    def get_template_data(self) -> dict:
        """Retrieves the template data (JSON) provided by the user

        :return: the compiled handlebars template
        """
        return self.__data

    def __to_lower_helper(self, this, options):
        """Renders the provided block in lower case
        :param this: the current execution context in the handlebars template
        :param options: the handlebars options dictionary
        :return: the compiled template
        """
        compiled_block = str(options['fn'](this))

        return compiled_block.lower()

    def __no_break_helper(self, this, options):
        """Renders the provided block and removes all whitespace
        :param this: the current execution context in the handlebars template
        :param options: the handlebars options dictionary
        :return: the compiled template
        """
        compiled_block = str(options['fn'](this))

        return "\n".join([line for line in compiled_block.split('\n') if line.strip() != ''])

    def __no_trailing_commma_helper(self, this, options):
        """Renders the provided block and removes any trailing commas
        :param this: the current execution context in the handlebars template
        :param options: the handlebars options dictionary
        :return: the compiled template
        """
        compiled_block = str(options['fn'](this)).rstrip()

        if not len(compiled_block):
            return ''

        return compiled_block[:-1] if compiled_block[-1] == ',' else compiled_block

    def __left_strip_helper(self, this, options):
        """Renders the provided block and strips whitespace from the left
        :param this: the current execution context in the handlebars template
        :param options: the handlebars options dictionary
        :return: the compiled template
        """
        compiled_block = str(options['fn'](this))

        return compiled_block.lstrip()

    def __if_has_feature_helper(self, this, options, feature_type: str):
        """Renders the provided block if the JSON schema has the feature_type provided
        :param this: the current execution context in the handlebars template
        :param options: the handlebars options dictionary
        :param feature_type: the string feature type to check for
        :return: the compiled template
        """
        matching_features = list(
            filter(lambda feature: feature['type'] ==
                   feature_type, self.__data['features'])
        )

        if len(matching_features) == 0:
            return ''

        return options['fn'](this)

    def __if_not_has_feature_helper(self, this, options, feature_type):
        """Renders the provided block if the JSON schema does not have the feature_type provided
        :param this: the current execution context in the handlebars template
        :param options: the handlebars options dictionary
        :param feature_type: the string feature type to check for
        :return: the compiled template
        """
        matching_features = list(
            filter(lambda feature: feature['type'] ==
                   feature_type, self.__data['features'])
        )

        if len(matching_features) > 0:
            return ''

        return options['fn'](this)

    def __if_type_is_helper(self, this, options, context_type):
        """Renders the block if the 'type' property in the current context matches the type provided
        :param this: the current execution context in the handlebars template
        :param options: the handlebars options dictionary
        :param context_type: the type value to compare to the context
        :return: the compiled template
        """
        if this['type'] != context_type:
            return ''

        return options['fn'](this)

    def __if_not_type_is_helper(self, this, options, context_type):
        """Renders the block if the 'type' property in the current context does not match the type provided
        :param this: the current execution context in the handlebars template
        :param options: the handlebars options dictionary
        :param context_type: the type value to compare to the context
        :return: the compiled template
        """
        if this['type'] == context_type:
            return ''

        return options['fn'](this)

    def __vue_render_helper(self, this, options):
        """Renders the block context inside vue {{ template tags }}
        :param this: the current execution context in the handlebars template
        :param options: the handlebars options dictionary
        :return: the compiled template
        """
        compiled_block = options['fn'](this)

        return '{{ %s }}' % compiled_block
