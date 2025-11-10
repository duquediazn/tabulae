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

## Pull Requests & Branch Protection Policy

To keep the project history clean and consistent, all changes must go through a **Pull Request (PR)**.

### Pull Request Guidelines

- Open all PRs against the `develop` branch (never directly into `main`).
- Keep PRs focused and concise — one clear purpose per PR.
- Use clear titles following the Conventional Commits format:
  - `feat(frontend): refactor user form`
  - `fix(api): correct token expiration check`
  - `docs(usage): clarify installation steps`
- Before merging, make sure all review comments and discussions are resolved.
- PRs should be merged using **Squash & Merge** to maintain a linear history.
- Avoid committing generated or build files.

> _Even if working solo, PRs are required. This helps to simulate real-world review workflows and maintain a clean commit history._

---

### Branch Protection Rules

This repository uses protected branches to ensure a clean and safe workflow:

| Branch | Purpose | Rules |
|---------|----------|-------|
| **main** | Stable releases | - Pull Request required<br>- Conversations must be resolved<br>- Linear history required<br>- Force pushes and deletions **not allowed** |
| **develop** | Ongoing development | - Pull Request required<br>- Conversations must be resolved<br>- Linear history optional<br>- Force pushes and deletions **not allowed** |

All other branches (`feature/*`, `hotfix/*`, `release/*`) are **not protected** and can be freely rebased, squashed, or force-pushed before opening a PR.

---

### History & Force Push Policy

- Interactive rebases (`git rebase -i`) and `--force-with-lease` are **allowed only on working branches** (`feature/*`, `hotfix/*`).
- Never rewrite history on `main` or `develop`.
- Before force-pushing, make sure no one else has updated the branch (`--force-with-lease` is safer than `--force`).
- Always prefer rebasing over merging to keep the history linear and easy to review.

---

### Example PR Flow

```bash
# Start from develop
git checkout develop
git pull origin develop

# Create a feature branch
git checkout -b feat/improve-docs

# Work and commit changes
git add .
git commit -m "docs(usage): fix outdated examples"
git push origin feat/improve-docs

# Open a Pull Request to 'develop'
# Review your own code, resolve conversations, then squash & merge when ready


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
