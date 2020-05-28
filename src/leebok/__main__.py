import os
from argparse import ArgumentParser
from .leebok import Leebok


def main(args=None):
    namespace = parse_args(args)

    leebok = Leebok()
    leebok.config.read(namespace.rcfile)

    os.makedirs(leebok.config.workspace, exist_ok=True)
    getattr(leebok, namespace.action)()


def parse_args(args):
    p = ArgumentParser('leebok')

    p.add_argument(
        'action',
        choices=['create', 'submit', 'status', 'ssh', 'delete']
    )

    p.add_argument(
        '--rcfile',
        default='leebokrc',
        help='rcfile',
        metavar='<path>'
    )

    return p.parse_args(args)


if __name__ == '__main__':
    main()
