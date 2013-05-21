#!/bin/sh

# Don't forget to add file with name "git-daemon-export-ok" to .git path

git daemon --verbose --base-path=${HOME}
