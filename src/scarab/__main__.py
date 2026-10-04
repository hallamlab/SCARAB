__author__ = 'Ryan J McLaughlin'

"""
SCARAB command line.
"""
import argparse
import logging
import sys
import warnings
warnings.filterwarnings('ignore')
from scarab.commands import (info, recruit)
from scarab.reassemble import reassemble

logger = logging.getLogger(__name__)

usage = """
scarab <command> [<args>]
** Commands include:
recruit        Recruit metagenomic contigs using optional trusted genomes.
reassemble     Guided short-read reassembly of recruited/trusted genome FASTAs.
** Other commands:
info           Display SCARAB version and other information.
help           Return this message.
Use '-h' to get subcommand-specific help, e.g.
"""


def main():
    commands = {"recruit": recruit, "reassemble": reassemble,
                "info": info}
    parser = argparse.ArgumentParser(description='Recruit environmental reads to reference SAG(s).',
                                     add_help=False
                                     )
    parser.add_argument('command', nargs='?')
    input_cmd = sys.argv[1:2]
    if input_cmd in (['-h'], ['--help']):
        input_cmd = ['help']
    args = parser.parse_args(input_cmd)

    if (not args.command) | (args.command == 'help'):
        sys.stderr.write(usage)
        sys.exit(0 if args.command == 'help' else 1)

    elif args.command not in commands:
        logger.error('Unrecognized command')
        sys.stderr.write(usage)
        sys.exit(1)

    cmd = commands.get(args.command)
    cmd(sys.argv[2:])
    logger.info('SCARAB has finished successfully.')


if __name__ == '__main__':
    main()
