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

### Example Git Flow (with Protected Branches)

Because `develop` and `main` are protected, **you never push directly to them.**
**All changes must go through a PR.**

#### Typical workflow

```bash
# Start from the latest develop
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

# Keep your branch aligned with develop while working
git fetch origin
git rebase origin/develop

# (Optional) Rebase to clean history
git rebase -i HEAD~N

# Push the branch
git push origin feat/some-feature
```
> If you rebased before pushing, use the following to avoid overwriting someone else’s work:

```bash
git push --force-with-lease
```
> --force-with-lease is safer than --force — it only pushes if no one else has updated the branch since your last pull, protecting shared work.

Open a **Pull Request → develop.**
Once the PR is approved and merged (Squash & Merge):
```bash
# Update your local develop after merge
git checkout develop
git pull origin develop

# Delete the feature branch
git branch -d feat/some-feature
git push origin --delete feat/some-feature
```

### Releasing a new version
Releases also use PRs.
You never merge to `main` locally.

```bash
# Update local develop
git checkout develop
git pull origin develop

# Create a release branch
git checkout -b release/v1.2.0
git push origin release/v1.2.0
```

Open PR → main
Title example: chore(release): version 1.2.0
Once merged:
```bash
# Locally sync main
git checkout main
git pull origin main

# Tag the released version
git tag -a v1.2.0 -m "Release: version 1.2.0"
git push origin v1.2.0
```

---

## Pull Requests & Branch Protection Policy

To keep the project history clean and consistent, all changes must go through a **Pull Request (PR)**.

### Pull Request Guidelines

- Open PRs into `develop`, except for release branches (`release/*`) which target `main`.
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

| Branch      | Purpose            | Rules                                                                                                |
| ----------- | ------------------ | ---------------------------------------------------------------------------------------------------- |
| **main**    | Stable releases    | - PR required<br>- Conversations resolved<br>- Squash merge<br>- No direct pushes<br>- No force push |
| **develop** | Active development | - PR required<br>- Conversations resolved<br>- Squash merge<br>- No direct pushes<br>- No force push |


All other branches (`feature/*`, `hotfix/*`, `release/*`) are **not protected** and can be freely rebased, squashed, or force-pushed before opening a PR.

---

### History & Force Push Policy

- Interactive rebases (`git rebase -i`) and `--force-with-lease` are **allowed only on working branches** (`feature/*`, `hotfix/*`).
- Never rewrite history on `main` or `develop`.
- Before force-pushing, make sure no one else has updated the branch (`--force-with-lease` is safer than `--force`).
- Always prefer rebasing over merging to keep the history linear and easy to review.

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
