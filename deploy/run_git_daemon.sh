#!/bin/sh

# Don't forget to add file with name "git-daemon-export-ok" to .git path
# or run "touch git-daemon-export-ok" in .git path

git daemon --verbose --base-path=${HOME}
