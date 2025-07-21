# Contributing to Tabulae

Thanks for your interest in contributing to Tabulae!

This project is maintained as a portfolio and learning tool, but contributions are welcome if they add value, fix bugs, or improve structure.

---

## Development Guidelines

- Fork the repository and create a feature branch (`feature/my-feature`) from `develop`
- Follow the Git Flow model (see below)
- Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for commit messages
- Keep pull requests focused and small where possible
- Run backend tests with `pytest` before submitting
- For frontend code, check formatting with ESLint (`npm run lint`)

---

## Branching and Commit Flow

This project follows a simplified [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) structure:

- `main`: stable releases
- `develop`: ongoing development
- `feature/*`: new features or improvements
- `hotfix/*`: quick fixes to production
- `release/*`: version preparation (optional)

We also use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) to keep commit history clean and semantic.

### Commit format

Examples:

```bash
feat: add product expiration chart
fix(auth): correct token refresh logic
docs(setup): improve installation guide
refactor(stock): simplify stock query logic
```

> Use git commit -m "type(scope): message" format consistently.

### Example Git Flow (Manual)

Here’s a typical workflow using develop and a feature/\* branch:

```bash
# Start from develop
git checkout develop
git pull --rebase origin develop
```

> Using --rebase avoids unnecessary merge commits and keeps the history linear and easier to read during code review.

```bash
# Create a feature branch
git checkout -b feat/some-feature

# Work and stage changes
git add -p

# Commit with Conventional Commit format
git commit -m "feat(scope): implement X"

# (Optional) Rebase to clean history
git rebase -i HEAD~N

# Merge into develop
git checkout develop
git pull --rebase origin develop
git merge feat/some-feature

# Delete local branch
git branch -d feat/some-feature

# Push changes
git push origin develop
```

> If you rebased before pushing, use the following to avoid overwriting someone else’s work:

```bash
git push --force-with-lease
```

> --force-with-lease is safer than --force — it only pushes if no one else has updated the branch since your last pull, protecting shared work.

### Releasing a new version

```bash
# Merge develop into main
git checkout main
git pull origin main
git merge develop

# Tag the release
git tag -a v1.1.0 -m "Release: feature X completed"
git push origin main
git push origin v1.1.0
```

---

## Testing & Linting

Before submitting a pull request, please make sure:

### Backend tests pass

```bash
docker compose -f docker-compose.dev.yml --profile test up -d db_test
cd backend
pytest
```

### Frontend passes lint checks

```bash
cd frontend
npm run lint
```

> This will highlight potential issues or unused variables in your React code.
