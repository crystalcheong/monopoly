#!/usr/bin/env bash

git pull

if [ -z "$1" ]; then
	echo "Please provide a tag."
	echo "Usage: ./release.sh [v]X.Y.Z[-suffix]"
	exit
fi

input_version=$1
normalized_version="${input_version#v}"
normalized_version="${normalized_version#V}"

if [ -z "$normalized_version" ]; then
	echo "Invalid version: $input_version"
	exit 1
fi

release_tag="v$normalized_version"
echo "Preparing $release_tag..."

# update the version
msg="# managed by release.sh"

# update the pyproject version
uv version "$normalized_version"

# build the latest version
uv build

# update the changelog
git cliff --unreleased --tag $(uv version --short) --prepend CHANGELOG.md
git add -A -ip && git commit -m "chore(release): prepare for $release_tag"

export GIT_CLIFF_TEMPLATE="\
\t{% for group, commits in commits | group_by(attribute=\"group\") %}\n\t{{ group | upper_first }}\
\t{% for commit in commits %}\n\t\t- {% if commit.breaking %}(breaking) {% endif %}{{ commit.message | upper_first }} ({{ commit.id | truncate(length=7, end=\"\") }})\
\t{% endfor %}\n\t{% endfor %}"

# create a signed tag
git tag "$release_tag"
echo "Done!"
echo "Now push the commit (git push) and the tag (git push --tags)."
