"""Create (or replace) a store's API key and print it once.

Usage: python -m scripts.create_store_key STORE_ID [--db PATH]
"""
import argparse
import os

from src.store_auth import StoreKeys


def main(argv=None):
    parser = argparse.ArgumentParser(description='Create or replace a store API key.')
    parser.add_argument('store_id')
    parser.add_argument('--db', default=os.environ.get('MOTIVE_STORE_DB', 'motive-store.sqlite3'))
    args = parser.parse_args(argv)
    print(StoreKeys(args.db).create_key(args.store_id))


if __name__ == '__main__':
    main()
