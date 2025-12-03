import argparse
import json
import os
import subprocess
import sys
from urllib import error, request


def get_bibtex(doi, ispreprint):
    if ispreprint:
        url = f"https://arxiv.org/bibtex/{doi}"
    else:
        url = f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex"
    req = request.Request(url)

    try:
        with request.urlopen(req) as response:
            return response.read().decode()
    except error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        sys.exit(1)
    except error.URLError as e:
        print(f"URL Error: {e.reason}")
        sys.exit(1)


def bibtex_to_csljson(bibtex):
    pandoc_cmd = ["pandoc", "-f", "bibtex", "-t", "csljson"]
    jq_cmd = ["jq", ".[]"]

    pandoc_result = subprocess.run(
        pandoc_cmd, input=bibtex, text=True, capture_output=True
    )
    jq_result = subprocess.run(
        jq_cmd, input=pandoc_result.stdout, text=True, capture_output=True
    )
    return jq_result.stdout


def add(args):
    # NOTE: pandoc bibtex to csljson is more reliable and arxiv api does not support csljson
    bibtex = get_bibtex(args.doi, args.arxiv)
    csljson = json.loads(bibtex_to_csljson(bibtex))
    if args.tags:
        csljson["tags"] = args.tags

    # TODO: check if already exists, then edit instead
    item = os.path.join(VAULT)
    if os.path.exists(item):
        pass  # do nothing
    else:
        with open(
            os.path.join(VAULT, csljson["id"]),
            mode="a",
        ) as file:
            file.write(json.dumps(csljson))

    not args.no_edit and subprocess.run([os.getenv("EDITOR"), item])


def main():
    parser = argparse.ArgumentParser(description="Aru's Bibliography Management System")

    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add", help="add new paper")
    add_parser.add_argument("doi", type=str, help="DOI")
    add_parser.add_argument(
        "--arxiv", action="store_true", default=False, help="Arxiv pre-print DOI"
    )
    add_parser.add_argument("-t", "--tags", nargs="*", help="Specify tag(s)")
    add_parser.add_argument(
        "-x",
        "--no-edit",
        action="store_true",
        default=False,
        help="Do not open in editor",
    )
    add_parser.set_defaults(func=add)

    ls_parser = subparsers.add_parser("ls", help="list existing items")
    ls_parser.set_defaults(func=ls)

    args = parser.parse_args()

    db = Db()
