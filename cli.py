import sys
from app import config

ARGUMENTS = sys.argv[1:]


def main():
    # Exit if a valid command was not provided
    if len(ARGUMENTS) == 0:
        return print('Please supply at least one command line argument')

    # Find all matching commands form the config file
    matched_commands = list(
        filter(lambda command: command['name']
               == ARGUMENTS[0], config.COMMANDS)
    )

    # Exit if the provided command was not recognised
    if len(matched_commands) < 1:
        return print('Sorry, the provided command was not recognised.')

    command = matched_commands[0]

    # Exit if insufficient arguments were provided to the given command
    if len(ARGUMENTS) - 1 < command['min_arg_count']:
        return print('Sorry, the command "%s" requires at least %d argument(s)' % (
            command['name'], command['min_arg_count'])
        )

    # Execute the command callback with the provided arguments
    command['callback'](ARGUMENTS)


if __name__ == '__main__':
    main()
