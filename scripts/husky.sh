npx husky add .husky/pre-commit "yarn format:lint && yarn lint:check"
npx husky add .husky/commit-msg "yarn commitlint --edit $1"