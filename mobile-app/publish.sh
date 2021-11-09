set -euo pipefail

# export tExpo app
expo export --public-url http://IP_TEMPLATE:8123 --dev

# rename index files to be a template
# so they cannot be recognized directly by Expo Go
echo "Preparing template files!"
cd ./dist
mv -f ios-index.json ios-index.template.json
mv -f android-index.json android-index.template.json
cd ..

# on CI push that changes to git
if [[ -n "$CI" ]]; then
  echo "CI env... Committing updated template to git."
  git config --global user.name "GitHub Action"
  git config --global user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git add ./dist
  git commit -m "[autocommit] Updated mobile-app template" --author="github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>"
  git push
fi 

echo "Publishing template done!"
