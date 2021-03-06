"""
Generage a changelog straight from your git commits.

Usage: auto-changelog [options]

Options:
    -r=REPO --repo=REPO     Path to the repository's root directory [Default: .]
    -t=TITLE --title=TITLE  The changelog's title [Default: Changelog]
    -d=DESC --description=DESC
                            Your project's description
    -o=OUTFILE --output=OUTFILE
                            The place to save the generated changelog 
                            [Default: CHANGELOG.md]
    -t=TEMPLATEDIR --template-dir=TEMPLATEDIR
                            The directory containing the templates used for
                            rendering the changelog
    -b --body               Include the message body in the output
    -f --footer             Include the message footer in the outputgit st
    -a --assume=version     Assume 'unreleased' commits will be in version
    -n --new                Only emit content for the 'unreleased' version (applying -a,
                            if applicable)
    -h --help               Print this help text
    -V --version            Print the version number
"""

import os
import sys

import docopt

from .parser import traverse
from .generator import generate_changelog
from . import __version__


def main():
    args = docopt.docopt(__doc__, version=__version__)

    if args.get('--template-dir'):
        template_dir = args['--template-dir']
    else:
        # The templates are sitting at ./templates/*.jinja2
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(base_dir, 'templates')

    # Convert the repository name to an absolute path
    repo = os.path.abspath(args['--repo'])

    try:
        # Traverse the repository and group all commits to master by release
        tags, unreleased = traverse(repo)
    except ValueError as e:
        print('ERROR:', e)
        sys.exit(1)
    
    changelog = generate_changelog(
            template_dir=template_dir,
            title=args['--title'],
            description=args.get('--description'),
            unreleased=unreleased,
            tags=tags,
            body=args['--body'],
            footer=args['--footer'],
            assume=args['--assume'],
            new=args['--new'],
    )

    with open(args['--output'], 'w') as f:
        f.write(changelog)


if __name__ == "__main__":
    main()
