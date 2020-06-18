import os
import re
from app import config
from app.util import TemplateParser
from datetime import datetime


class Generator(object):
    def __init__(self, template_path):
        self.__template_path = template_path
        self.__parser = TemplateParser(template_path)
        self.__identifiers = self.__parser.get_template_data()['identifiers']

    def build(self):
        """Builds new and existing project files from the provided templates and partials"""
        if self.__generate_templates() and self.__generate_appends():
            print('Successfully generated files for %s, formatting...' %
                  self.__template_path)

        # Run prettier
        os.system('prettier --write "**/*.php" "!vendor/" &>/dev/null')

        # Run php-cs-fixer and eslint
        os.system('php-cs-fixer fix &>/dev/null && yarn lint --fix &>/dev/null')

        print('New files formatted successfully.')

    def _get_partial_files(self):
        """Returns a list of partials used to update existing files in the project

        :return: a nested array containing the source path, destination tag and destination path of the partial
        """
        return []

    def _get_template_files(self):
        """Returns a list of templates used to generate new files in the project

        :return: a nested array containing the source and destination path of the template.
        """
        return []

    def _get_template_subdirectory(self):
        return ''

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

            #Abort if the destination file already exists to prevent overwriting
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

        return True

    def __generate_appends(self):
        """Updates existing project files defined by _get_appended_files

        :return: if the operation completed successfully
        """
        for (source_path, tag, destination_path) in self._get_partial_files():
            destination_path = self.__parse_file_path(destination_path)
            destination_directory = os.path.dirname(destination_path)

            # Ensure the destination folder exists
            if not os.path.exists(destination_directory):
                print('Couldn\'t find the directory %s to update, aborting...' %
                      destination_directory)
                return False

            # Ensure the destination file exists
            if not os.path.isfile(destination_path):
                print('Couldn\'t find the file %s to update, aborting...' %
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

            # Render and the partial and replace the tag contents
            with open(destination_path, 'w') as destination_file:
                rendered_partial = self.__parser.render_file(
                    '%s/%s/%s' % (config.TEMPLATE_DIR,
                                  self._get_template_subdirectory(), source_path)
                )

                updated_contents = destination_contents.replace(
                    '/*--OPTIMUS-CLI:%s--*/' % tag, rendered_partial
                )

                updated_contents = updated_contents.replace(
                    '<!--OPTIMUS-CLI:%s-->' % tag, rendered_partial
                )

                destination_file.write(updated_contents)

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

    def _get_template_files(self):
        return [
            [
                'back/Controller.php.j2',
                'app/Http/Controllers/Back/Api/{{ identifiers.pascal_plural }}Controller.php'
            ],
            [
                'back/Model.php.j2',
                'app/Models/{{ identifiers.pascal_singular }}.php'
            ],
            [
                'back/Resource.php.j2',
                'app/Http/Resources/{{ identifiers.pascal_singular }}Resource.php'
            ],
            [
                'back/Migration.php.j2',
                'database/migrations/%s_create_{{ identifiers.snake_plural }}_table.php' % self.__get_datetime()
            ],
            [
                'front/api.js.j2',
                'resources/js/back/modules/{{ identifiers.kebab_plural }}/routes/api.js'
            ],
            [
                'front/app.js.j2',
                'resources/js/back/modules/{{ identifiers.kebab_plural }}/routes/app.js'
            ],
            [
                'front/Create.vue.j2',
                'resources/js/back/modules/{{ identifiers.kebab_plural }}/views/Create.vue'
            ],
            [
                'front/Edit.vue.j2',
                'resources/js/back/modules/{{ identifiers.kebab_plural }}/views/Edit.vue'
            ],
            [
                'front/Index.vue.j2',
                'resources/js/back/modules/{{ identifiers.kebab_plural }}/views/Index.vue'
            ],
            [
                'front/Form.vue.j2',
                'resources/js/back/modules/{{ identifiers.kebab_plural }}/views/partials/Form.vue'
            ]
        ]

    def _get_partial_files(self):
        return [
            [
                'back/appends/Routes.php.j2',
                'routes',
                'routes/admin.php'
            ],
            [
                'back/appends/OptimusImports.php.j2',
                'imports',
                'app/Providers/OptimusServiceProvider.php'
            ],
            [
                'back/appends/OptimusLinkableTypes.php.j2',
                'linkable-types',
                'app/Providers/OptimusServiceProvider.php'
            ],
            [
                'back/appends/OptimusMediaConversions.php.j2',
                'media-conversions',
                'app/Providers/OptimusServiceProvider.php'
            ],
            [
                'front/appends/Dashboard.vue.j2',
                'navigation',
                'resources/js/back/components/ui/Dashboard.vue'
            ],
            [
                'front/appends/RouterImports.js.j2',
                'imports',
                'resources/js/back/router/index.js'
            ],
            [
                'front/appends/RouterRoutes.js.j2',
                'routes',
                'resources/js/back/router/index.js'
            ],
        ]

    def __get_datetime(self):
        return datetime.utcnow().strftime('%Y_%m_%d_%H%M%S')


class PageGenerator(Generator):
    def _get_template_subdirectory(self):
        return 'page'

    def _get_template_files(self):
        return [
            [
                'back/Template.php.hbs',
                'app/PageTemplates/{{identifiers.file_name}}Template.php'
            ],
            [
                'front/Form.vue.hbs',
                'resources/js/back/modules/pages/views/templates/{{identifiers.file_name}}.vue'
            ]
        ]

    # todo - better name
    def _get_appended_files(self):
        return [
            [
                'back/appends/OptimusImports.php.hbs',
                'imports',
                'app/Providers/OptimusServiceProvider.php'
            ],
            [
                'back/appends/OptimusPageTemplates.php.hbs',
                'page-templates',
                'app/Providers/OptimusServiceProvider.php'
            ]
        ]
