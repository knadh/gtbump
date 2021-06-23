#!/bin/python
import argparse
import re
from time import sleep
import subprocess
import sys

__version__ = "1.1.0"

MAJOR = "major"
MINOR = "minor"
PATCH = "patch"
SUFFIX = "suffix"

def run(cmd):
    """Executes a git shell command."""
    out = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()

    # Error on stderr?
    if stderr:
        raise Exception(stderr.strip().decode("utf-8"))

    if stdout:
        o = stdout.strip().decode("utf-8")
        if "No names found" in o:
            raise Exception("no tags found. Run --init to add v0.1.0")
        if "fatal" in o:
            raise Exception(o)
        return o


def get_last_tag():
    """Get the latest (closest) annotated git tag."""
    tag = run("git describe --abbrev=0")

    # Parse semver tag: v0.0.0-xxxx (optional suffix).
    match = re.search(r"^v(\d+)\.(\d+)\.(\d+)((\-|\+).+?)?$", tag)
    if not match or len(match.groups()) != 5:
        raise Exception("invalid tag in non-semver format: {}".format(tag))

    g = match.groups()
    return {"tag": tag,
            MAJOR: int(g[0]),
            MINOR: int(g[1]),
            PATCH: int(g[2]),
            SUFFIX: g[3] if g[3] else ""}


def get_all_tags():
    """Get all annotated (closest) tags by lexicographic order."""
    tags = run("git tag --sort=-refname").split("\n")

    # Parse semver tag: v0.0.0-xxxx (optional suffix).
    out = []
    for t in tags:
        match = re.search(r"^v(\d+)\.(\d+)\.(\d+)((\-|\+).+?)?$", t)
        if not match or len(match.groups()) != 5:
            raise Exception("invalid tag in non-semver format: {}".format(t))

        g = match.groups()
        out.append({"tag": t,
            MAJOR: int(g[0]),
            MINOR: int(g[1]),
            PATCH: int(g[2]),
            SUFFIX: g[3] if g[3] else ""})

    return out


def bump(current, part, suffix="", strip_suffix=False):
    """
    Given the current tag, part (major, minor ...) to bump and optional
    semver suffixes, bump the value and adds an annotated tag to the repo. 
    """
    fmt = "v{}.{}.{}{}"
    old_tag = fmt.format(
        current[MAJOR], current[MINOR], current[PATCH], current[SUFFIX])

    # Bump the numeric part and set the lower parts to 0.
    current[part] += 1
    if part == MAJOR:
        current[MINOR] = 0
        current[PATCH] = 0
    elif part == MINOR:
        current[PATCH] = 0

    if strip_suffix:
        current[SUFFIX] = ""

    if suffix:
        current[SUFFIX] = suffix

    new_tag = fmt.format(
        current[MAJOR], current[MINOR], current[PATCH], current[SUFFIX])
    run("git tag -a {} -m {}".format(new_tag, new_tag))
    print("bumped {} -> {}".format(old_tag, new_tag))


def main():
    """Run the CLI."""
    p = argparse.ArgumentParser(
        description="simple semver tag bump helper for git")
    p.add_argument("-ss", "--strip-suffix", action="store_true",
                   dest="strip_suffix", help="strip existing suffx from tag (eg: -beta.0)")
    p.add_argument("-s", "--suffix", action="store", type=str, metavar="",
                   dest="suffix", help="optional suffix to add to the tag (eg: -beta.0). Pass as =\"-beta\" if the first character is a dash")
    p.add_argument("-v", "--version", action="store_true", dest="version",
                   help="show version")

    g = p.add_argument_group("bump").add_mutually_exclusive_group()
    g.add_argument("-init", "--init", action="store_true",
                   dest="init", help="add tag v0.1.0 (when there are no tags)")
    g.add_argument("-show", "--show", action="store_true",
                   dest="show", help="show last tag")
    g.add_argument("-changelog", "--changelog", action="store_true",
                   dest="changelog", help="generate a Markdown changelog of commits between the last and the current version")
    g.add_argument("-push-last", "--push-last", action="store", type=str, nargs="?", const="origin", metavar="",
                   dest="push_last", help="push the last tag upstream (default: origin). IMPORTANT: This skips pre-push hooks with --no-verify. eg: --push-last, --push-last=remote_name")
    g.add_argument("-delete-last", "--delete-last", action="store_true",
                   dest="delete_last", help="delete the last tag")
    g.add_argument("-major", "--major", action="store_true",
                   dest="major", help="bump major version (vX.0.0)")
    g.add_argument("-minor", "--minor", action="store_true",
                   dest="minor", help="bump minor version (v0.X.0)")
    g.add_argument("-patch", "--patch", action="store_true",
                   dest="patch", help="bump patch version (v0.0.X)")
    args = p.parse_args()

    if args.version:
        print("v{}".format(__version__))
        quit()

    # Show the last tag.
    try:
        if args.show:
            print(get_last_tag()["tag"])
            sys.exit(0)

        elif args.init:
            # Check if a tag already exists.
            try:
                t = get_last_tag()["tag"]
                print("tag already initialized (last = {})".format(t))
                sys.exit(1)
            except Exception:
                pass

            bump({MAJOR: 0, MINOR: 0, PATCH: 0,
                  SUFFIX: ""}, MINOR, "", False)
            sys.exit(0)

        elif args.changelog:
            tags = get_all_tags()

            cmd = "git log --pretty=\"- %h %s\" {}"
            if len(tags) == 1:
                print("changelog for {}".format(tags[0]["tag"]))
                cmd = cmd.format(tags[0]["tag"])
            else:
                print("changelog for {} -> {}".format(tags[1]["tag"], tags[0]["tag"]))
                # git log --pretty="- %h %s" v1.0.0..v1.1.0
                cmd = cmd.format("{}..{}".format(tags[1]["tag"], tags[0]["tag"]))

            out = run(cmd)
            if not out:
                print("no commits")
            else:
                print(out)

            sys.exit(0)


        elif args.push_last:
            tag = get_last_tag()["tag"]
            print("pushing {} to {}".format(tag, args.push_last))
            sleep(2);
            try:
                print(run("git push --no-verify {} {}".format(args.push_last, tag)))
            except Exception as e:
                print(e)
                sys.exit(1)
            sys.exit(0)

        elif args.delete_last:
            tag = get_last_tag()["tag"]
            run("git tag -d {}".format(tag))
            print("deleted {}".format(tag))
            sys.exit(0)

        else:
            # If there's a suffix, it should start with - or +.
            if args.suffix and args.suffix != "":
                if args.suffix[0] not in ["-", "+"]:
                    print("suffix should start with a - or +")
                    sys.exit(0)

            # Get the type of bump from the args.
            parts = {MAJOR: args.major,
                     MINOR: args.minor, PATCH: args.patch}
            part = list(filter(parts.get, parts))
            if len(part) > 0:
                # Get the last tag and increment the requested part.
                current = get_last_tag()
                bump(current, part[0], args.suffix, args.strip_suffix)
                sys.exit(0)
    except Exception as e:
        print(str(e))
        sys.exit(1)

    p.print_help()
