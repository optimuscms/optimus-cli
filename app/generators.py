import os
import re
from app import config
from app.util import TemplateParser
from app.util import PageTemplateConfigParser
from datetime import datetime


class Generator(object):
    def __init__(self, config_path):
        self.__config_path = config_path
        self.__parser = TemplateParser(config_path)

    def build(self):
        """Builds new and existing project files from the provided templates and dynamic files"""

        # Parse JSON config
        try:
            self._get_config_parser().parse_json_file(
                self.__template_path
            )
        except Exception as exception:
            return print('Error detected in config\n%s' % str(exception))

        # Generate new files
        self.__generate_templates()

        # Update existing files
        self.__update_dynamic_files()

        # Run php-cs-fixer and eslint
        os.system('php-cs-fixer fix &>/dev/null && yarn lint --fix &>/dev/null')

        print('New files generated successfully.')

    def _get_dynamic_files(self):
        """Returns a list of dynamic files which are updated when the generator is run

        :return: a nested array containing the source path, destination tag and destination path of the dynamic file
        """
        return []

    def _get_template_files(self):
        """Returns a list of templates used to generate new files in the project

        :return: a nested array containing the source and destination path of the template.
        """
        return []

    def _get_template_subdirectory(self):
        return ''

    def _get_config_parser(self):
        return None

    def __generate_templates(self):
        """Generate new project files defined by _get_template_files

        :return: if the operation completed successfully
        """
        for (source_path, destination_path) in self._get_template_files():
            destination_path = self.__parse_file_path(destination_path)
            destination_directory = os.path.dirname(destination_path)

            # Create the destination folder if it doesn't exist already
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)

            # Abort if the destination file already exists to prevent overwriting
            if os.path.isfile(destination_path):
                print('File %s already exists, aborting...' % destination_path)
                return

            # Render and write the template to the destination file
            with open(destination_path, 'w') as destination_file:
                rendered_template = self.__parser.render_file(
                    '%s/%s/%s' % (config.TEMPLATE_DIR,
                                  self._get_template_subdirectory(), source_path)
                )

                destination_file.write(rendered_template)

            # Run prettier if destination file is PHP
            if destination_path.endswith('.php'):
                os.system('prettier %s --write &>/dev/null' % destination_path)

        return True

    def __update_dynamic_files(self):
        """Updates existing project files defined by _get_dynamic_files

        :return: if the operation completed successfully
        """
        for (source_path, tag, destination_path) in self._get_dynamic_files():
            destination_path = self.__parse_file_path(destination_path)
            destination_directory = os.path.dirname(destination_path)

            # Ensure the destination folder exists
            if not os.path.exists(destination_directory):
                print('Couldn\'t find the directory "%s" to update append, aborting...' %
                      destination_directory)
                return False

            # Ensure the destination file exists
            if not os.path.isfile(destination_path):
                print('Couldn\'t find the file "%s" to update, aborting...' %
                      destination_path)
                return False

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
                return False

            # Ensure there is only one occurrence of the tag we are updating
            if destination_tags.count(tag) > 1:
                print('Duplicate marker tag %s in file %s, aborting...' %
                      (tag, destination_path))
                return False

            # Render and write the dynamic content and place it in the destination file
            with open(destination_path, 'w') as destination_file:
                rendered_content = self.__parser.render_file(
                    '%s/%s/%s' % (config.TEMPLATE_DIR,
                                  self._get_template_subdirectory(), source_path)
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

        return True

    def __parse_file_path(self, file_path):
        """Parses variables in a template file path

        :param file_path: the file path to parse
        :return: the parsed file path
        """
        return self.__parser.render_string(file_path)


class ModuleGenerator(Generator):
    def _get_template_subdirectory(self):
        return 'module'

    def _get_config_parser(self):
        return PageTemplateConfigParser()  # todo

    def _get_template_files(self):
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
                'database/migrations/%s_create_{{ name | plural | snake }}_table.php' % self.__get_datetime()
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

    def _get_dynamic_files(self):
        return [
            [
                'back/dynamic/Routes.php.j2',
                'routes',
                'routes/admin.php'
            ],
            [
                'back/dynamic/OptimusImports.php.j2',
                'imports',
                'app/Providers/OptimusServiceProvider.php'
            ],
            [
                'back/dynamic/OptimusLinkableTypes.php.j2',
                'linkable-types',
                'app/Providers/OptimusServiceProvider.php'
            ],
            [
                'back/dynamic/OptimusMediaConversions.php.j2',
                'media-conversions',
                'app/Providers/OptimusServiceProvider.php'
            ],
            [
                'front/dynamic/Dashboard.vue.j2',
                'navigation',
                'resources/js/back/components/ui/Dashboard.vue'
            ],
            [
                'front/dynamic/RouterImports.js.j2',
                'imports',
                'resources/js/back/router/index.js'
            ],
            [
                'front/dynamic/RouterRoutes.js.j2',
                'routes',
                'resources/js/back/router/index.js'
            ],
        ]

    def __get_datetime(self):
        return datetime.utcnow().strftime('%Y_%m_%d_%H%M%S')


class PageGenerator(Generator):
    def _get_template_subdirectory(self):
        return 'page'

    def _get_config_parser(self):
        return PageTemplateConfigParser()

    def _get_template_files(self):
        return [
            [
                'back/Template.php.j2',
                'app/PageTemplates/{{ identifiers.file_name }}Template.php'
            ],
            [
                'front/Form.vue.j2',
                'resources/js/back/modules/pages/views/templates/{{ identifiers.file_name }}.vue'
            ]
        ]

    def _get_dynamic_files(self):
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
