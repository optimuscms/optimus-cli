import sys
from app import config

ARGUMENTS = sys.argv[1:]


def main():
    print()

    if len(ARGUMENTS) == 0:
        print('Please supply at least one command line argument')
        return

    matched_commands = list(
        filter(lambda command: command['name']
               == ARGUMENTS[0], config.COMMANDS)
    )

    if len(matched_commands) < 1:
        print('Sorry, the provided command was not recognised.')
        return

    matched_commands[0]['callback'](ARGUMENTS)


if __name__ == '__main__':
    main()
