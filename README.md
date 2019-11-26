# gtbump
git tag bump: A simple utility to bump semver git tags.

## Install
```shell
pip install gtbump
```

### Usage
```shell
# cd to your git repo.

# see the last tag.
$ gtbump --show
no tags found. Run --init to add v0.1.0

# add a tag for the first time.
$ gtbump --init
bumped v0.0.0 -> v0.1.0

# bump major | minor | patch
$ gtbump --minor
bumped v0.1.0 -> v0.2.0

$ gtbump --major
bumped v0.2.0 -> v1.2.0

# delete the last tag
$ gtbump --delete-last
deleted v1.2.0
```

Check `gtbump --help` for more options.

Licensed under the MIT license.
