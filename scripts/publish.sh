#!/bin/bash

# Exit script if any command fails
set -e

# Ensure a commit message was provided
if [ -z "$1" ]
then
    echo "Please provide a commit message."
    exit 1
fi

commit_message=$1

# Switch to master branch
git checkout main

# Merge private into main
# git merge private
git merge --no-ff --no-commit private

# Remove agent.js
if git rev-parse --verify --quiet juno/js/src >/dev/null; then
    git reset HEAD -- juno/js/src
fi

if git rev-parse --verify --quiet juno/js/package.json >/dev/null; then
    git reset HEAD juno/js/package.json
fi

if git rev-parse --verify --quiet juno/js/package-lock.json >/dev/null; then
    git reset HEAD juno/js/package-lock.json
fi

# git commit -m "merged dev"

if git rev-parse --verify --quiet juno/js/src >/dev/null; then
    git rm -rf juno/js/src
    rm -rf juno/js/src
fi

if git rev-parse --verify --quiet juno/js/package.json >/dev/null; then
    git rm juno/js/package.json
fi

if git rev-parse --verify --quiet juno/js/package-lock.json >/dev/null; then
    git rm juno/js/package-lock.json
fi

# Commit the changes
git commit -m "$commit_message"

# Push changes to both repositories
git push juno-private main

cd ../
git clone --branch main git@github.com:alexi/juno-private.git juno-filter-repo
cd juno-filter-repo
git remote remove origin
git remote add origin git@github.com:alexi/juno.git
git filter-repo --path juno/js/src --path juno/js/package.json --path juno/js/package-lock.json --invert-paths --force


git push origin main --force
cd ../
rm -rf juno-filter-repo
cd ./juno