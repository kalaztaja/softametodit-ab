#!/bin/bash

git_url=$1

# Git url parameter is empty
if [ -z "$git_url" ]
then
    echo "You must specify a Git url."
    exit 1
fi

echo "Creating the Git repository."
rm -rf input
git clone $git_url input
chmod -R 777 input
cp ./services/sonar-project-config/sonar-project.properties input/

echo "Building service stack."
docker-compose up --build -d

echo "Ready! Now wait for the analysis to finish."
