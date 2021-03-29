#!/usr/bin/env python
import argparse
import csv
import logging
import pathlib
import sys
from subprocess import PIPE, Popen

PASSWORD_STORE_PATH = pathlib.Path('~/.password-store').expanduser()

logger = logging.getLogger('chrome2pass')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=argparse.FileType('r'))
    parser.add_argument('-p', '--parent-dir', default='chrome')
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='be verbose'
    )
    args = parser.parse_args()
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.WARNING,
    )
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    gpg_id_path = PASSWORD_STORE_PATH / '.gpg-id'
    with gpg_id_path.open('r') as fp:
        gpg_id = fp.read().strip()
    reader = csv.reader(args.file)
    next(reader)
    for name, _, username, password in reader:
        entry_path = PASSWORD_STORE_PATH / args.parent_dir / name
        entry_path.mkdir(parents=True, exist_ok=True)
        entry_path /= f"{username}.gpg"
        with entry_path.open('wb') as fp:
            cmd = ["gpg", "--encrypt", "-r", gpg_id]
            p = Popen(
                cmd,
                stdin=PIPE,
                stdout=PIPE,
            )
            p.stdin.write(password.encode())
            out = p.communicate()[0]
            p.stdin.close()
            fp.write(out)
            logger.debug("saved %s", entry_path)


if __name__ == '__main__':
    main()
