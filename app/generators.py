import os
import re
import json
from app import config
from app.template import TemplateParser
from app.schema import ModuleConfigParser
from app.schema import PageTemplateConfigParser

from datetime import datetime


class Generator(object):

    @classmethod
    def build(cls, config_path: str):
        """Builds new and existing project files for the provided json config"""

        # Ensure the provided config file exists
        if not os.path.exists(config_path):
            return print('Config file does not exist, please check the provided path and try again')

        # Read the config file and convert to JSON
        with open(config_path, 'r') as config_file:
            try:
                config_dict = json.loads(config_file.read())
            except:
                return print('Could not parse provided config as JSON, please check input file and try again')

        # Ensure the JSON config is valid
        try:
            cls._get_config_parser().parse(config_dict)
        except Exception as exception:
            return print('The following error detected in was detected in your config file, please fix it and run the generator again:\n\n%s' % str(exception))

        parser = TemplateParser(config_path)

        # Generate new files
        cls.__generate_templates(parser)

        # Update existing files
        cls.__update_dynamic_files(parser)

        # Run php-cs-fixer and eslint
        os.system('php-cs-fixer fix &>/dev/null && yarn lint --fix &>/dev/null')

        print('New files generated successfully.')

    @classmethod
    def _get_dynamic_files(cls) -> list:
        """Returns a list of dynamic files which are updated when the generator is run

        :return: a nested array containing the source path, destination tag and destination path of the dynamic file
        """
        return []

    @classmethod
    def _get_template_files(cls) -> list:
        """Returns a list of templates used to generate new files in the project

        :return: a nested array containing the source and destination path of the template.
        """
        return []

    @classmethod
    def _get_template_subdirectory(cls) -> str:
        return ''

    @classmethod
    def _get_config_parser(cls):
        return None

    @classmethod
    def __generate_templates(cls, parser: TemplateParser):
        """Generate new project files defined by _get_template_files

        :return: if the operation completed successfully
        """
        for (source_path, destination_path) in cls._get_template_files():
            destination_path = parser.render_string(destination_path)
            destination_directory = os.path.dirname(destination_path)

            # Create the destination folder if it doesn't exist already
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)

            # Abort if the destination file already exists to prevent overwriting
            # if os.path.isfile(destination_path):
            #     print('File %s already exists, aborting...' % destination_path)
            #     return

            # Render and write the template to the destination file
            with open(destination_path, 'w') as destination_file:
                rendered_template = parser.render_file(
                    '%s/%s/%s' % (config.TEMPLATE_DIR,
                                  cls._get_template_subdirectory(), source_path)
                )

                destination_file.write(rendered_template)

            # Run prettier if destination file is PHP
            if destination_path.endswith('.php'):
                os.system('prettier %s --write &>/dev/null' % destination_path)

        return True

    @classmethod
    def __update_dynamic_files(cls, parser: TemplateParser):
        """Updates existing project files defined by _get_dynamic_files

        :return: if the operation completed successfully
        """
        for (source_path, tag, destination_path) in cls._get_dynamic_files():
            destination_path = parser.render_string(destination_path)
            destination_directory = os.path.dirname(destination_path)

            # Ensure the destination folder exists
            if not os.path.exists(destination_directory):
                print('Couldn\'t find the directory "%s" to update append, aborting...' %
                      destination_directory)

            # Ensure the destination file exists
            if not os.path.isfile(destination_path):
                print('Couldn\'t find the file "%s" to update, aborting...' %
                      destination_path)

            # Read the current contents of the destination file and locate tags
            with open(destination_path, 'r') as destination_file:
                destination_contents = destination_file.read()

                code_tags = re.findall(
                    r'\/\*--OPTIMUS-CLI:([\w-]*)--\*\/', destination_contents)

                view_tags = re.findall(
                    r'<\!--OPTIMUS-CLI:([\w-]*)-->', destination_contents)

                destination_tags = code_tags + view_tags

            # Ensure the tag we are updating is in the destination file
            if tag not in destination_tags:
                print('Could not find marker tag %s in file %s, aborting...' %
                      (tag, destination_path))

            # Ensure there is only one occurrence of the tag we are updating
            if destination_tags.count(tag) > 1:
                print('Duplicate marker tag %s in file %s, aborting...' %
                      (tag, destination_path))

            # Render and write the dynamic content and place it in the destination file
            with open(destination_path, 'w') as destination_file:
                rendered_content = cls.__parser.render_file(
                    '%s/%s/%s' % (config.TEMPLATE_DIR,
                                  cls._get_template_subdirectory(), source_path)
                )

                updated_contents = destination_contents.replace(
                    '/*--OPTIMUS-CLI:%s--*/' % tag, rendered_content
                )

                updated_contents = updated_contents.replace(
                    '<!--OPTIMUS-CLI:%s-->' % tag, rendered_content
                )

                destination_file.write(updated_contents)

            # Run prettier if destination file is PHP
            if destination_path.endswith('.php'):
                os.system('prettier %s --write &>/dev/null' % destination_path)


class ModuleGenerator(Generator):

    @classmethod
    def _get_template_subdirectory(cls) -> str:
        return 'module'

    @classmethod
    def _get_config_parser(cls):
        return ModuleConfigParser()

    @classmethod
    def _get_template_files(cls) -> list:
        return [
            [
                'back/Controller.php.j2',
                'app/Http/Controllers/Back/Api/{{ name | plural | pascal }}Controller.php'
            ],
            [
                'back/Model.php.j2',
                'app/Models/{{ name | singular | pascal }}.php'
            ],
            [
                'back/Resource.php.j2',
                'app/Http/Resources/{{ name | singular | pascal }}Resource.php'
            ],
            [
                'back/Migration.php.j2',
                'database/migrations/%s_create_{{ name | plural | snake }}_table.php' % cls.__get_datetime()
            ],
            [
                'front/api.js.j2',
                'resources/js/back/modules/{{ name | plural | kebab }}/routes/api.js'
            ],
            [
                'front/app.js.j2',
                'resources/js/back/modules/{{ name | plural | kebab }}/routes/app.js'
            ],
            [
                'front/Create.vue.j2',
                'resources/js/back/modules/{{ name | plural | kebab }}/views/Create.vue'
            ],
            [
                'front/Edit.vue.j2',
                'resources/js/back/modules/{{ name | plural | kebab }}/views/Edit.vue'
            ],
            [
                'front/Index.vue.j2',
                'resources/js/back/modules/{{ name | plural | kebab }}/views/Index.vue'
            ],
            [
                'front/Form.vue.j2',
                'resources/js/back/modules/{{ name | plural | kebab }}/views/partials/Form.vue'
            ]
        ]

    @classmethod
    def _get_dynamic_files(cls) -> list:
        return [
            # [
            #     'back/dynamic/Routes.php.j2',
            #     'routes',
            #     'routes/admin.php'
            # ],
            # [
            #     'back/dynamic/OptimusImports.php.j2',
            #     'imports',
            #     'app/Providers/OptimusServiceProvider.php'
            # ],
            # [
            #     'back/dynamic/OptimusLinkableTypes.php.j2',
            #     'linkable-types',
            #     'app/Providers/OptimusServiceProvider.php'
            # ],
            # [
            #     'back/dynamic/OptimusMediaConversions.php.j2',
            #     'media-conversions',
            #     'app/Providers/OptimusServiceProvider.php'
            # ],
            # [
            #     'front/dynamic/Dashboard.vue.j2',
            #     'navigation',
            #     'resources/js/back/components/ui/Dashboard.vue'
            # ],
            # [
            #     'front/dynamic/RouterImports.js.j2',
            #     'imports',
            #     'resources/js/back/router/index.js'
            # ],
            # [
            #     'front/dynamic/RouterRoutes.js.j2',
            #     'routes',
            #     'resources/js/back/router/index.js'
            # ],
        ]

    @classmethod
    def __get_datetime(cls) -> str:
        return datetime.utcnow().strftime('%Y_%m_%d_%H%M%S')


class PageGenerator(Generator):

    @classmethod
    def _get_template_subdirectory(cls) -> str:
        return 'page'

    @classmethod
    def _get_config_parser(cls):
        return PageTemplateConfigParser()

    @classmethod
    def _get_template_files(cls) -> list:
        return [
            [
                'back/Template.php.j2',
                'app/PageTemplates/{{ name | pascal }}Template.php'
            ],
            [
                'front/Form.vue.j2',
                'resources/js/back/modules/pages/views/templates/{{ name | pascal }}.vue'
            ]
        ]

    @classmethod
    def _get_dynamic_files(cls) -> list:
        return [
            [
                'back/dynamic/OptimusImports.php.j2',
                'imports',
                'app/Providers/OptimusServiceProvider.php'
            ],
            [
                'back/dynamic/OptimusPageTemplates.php.j2',
                'page-templates',
                'app/Providers/OptimusServiceProvider.php'
            ]
        ]
