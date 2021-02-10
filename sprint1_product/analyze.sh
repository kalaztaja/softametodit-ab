#!/bin/bash

git_url=$1

# Git url parameter is empty
if [ -z "$git_url" ]
then
    echo "You must specify a Git url."
    exit 1
fi

# Note that the folder is not empty and hence the repo cannot be cloned
echo "Creating the Git repository."
cd input
git init
git remote add origin $git_url
git fetch
git checkout -t origin/master -f
cd ..

echo "Building service stack."
docker-compose up --build -d

echo "Ready! Now wait for the analysis to finish."
