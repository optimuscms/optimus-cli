import sys
from app.generators import ModuleGenerator, PageGenerator

COMMANDS = [
    {
        'name': 'generate:module',
        'callback': lambda args: ModuleGenerator(args[1]).build()
    },
    {
        'name': 'generate:page',
        'callback': lambda args: PageGenerator(args[1]).build()
    },
]

# Directory to load templates from (no trailing slash)
TEMPLATE_DIR = sys.path[0] + '/templates'
