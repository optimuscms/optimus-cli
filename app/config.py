import sys
from app.generators import ModuleGenerator, PageGenerator

COMMANDS = [
    {
        'min_arg_count': 1,
        'name': 'generate:module',
        'callback': lambda args: ModuleGenerator().build(args[1], args[1:])
    },
    {
        'min_arg_count': 1,
        'name': 'generate:page',
        'callback': lambda args: PageGenerator().build(args[1], args[1:])
    }
]

# Directory to load templates from (no trailing slash)
TEMPLATE_DIR = sys.path[0] + '/templates'
