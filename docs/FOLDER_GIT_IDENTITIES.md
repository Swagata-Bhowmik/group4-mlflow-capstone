# Two commit identities, one push credential, this folder only

Yes: use `./git-swagata commit ...` and `./git-sumit commit ...`. The project now includes those wrappers. They set the identity for that command without changing global Git configuration. They contain no token and do not sign into two accounts.

## What the two identities mean

- `git-swagata`: new commits identify Swagata Bhowmik as author and committer.
- `git-sumit`: new commits identify Sumit Kothari as author and committer.
- A shared authorized token can push either set of commits. GitHub records the authenticated push as coming from the token owner; this does not authenticate both students separately.
- Use the relevant wrapper for work that member actually contributed and authorized. These commands do not by themselves establish individual participation or add a verified signature. Merge/rebase/cherry-pick operations can preserve existing authors; these examples concern new commits.

## One-time folder setup

On Windows, use **Git Bash** (provided by Git for Windows) for the `./git-swagata` syntax. The Python pipeline still runs through Docker as explained in the Windows guide. A Python virtual environment has no effect on Git identity.

From the project root, after this folder has been initialized as a repository or cloned:

```bash
git config --local team.swagata.email 'SWAGATAS_VERIFIED_GITHUB_EMAIL'
git config --local team.sumit.email 'SUMITS_VERIFIED_GITHUB_EMAIL'
```

Replace these placeholders with actual emails associated with the respective GitHub accounts. Each member can instead copy their exact private noreply address from GitHub Settings → Emails. Do not guess the noreply format from the username.

These values are stored only in this repository's `.git/config`. The wrappers use fixed display names and the corresponding configured email. They refuse to run when the local email is missing or the wrapper folder is not itself a repository. They do not initialize a repository or discover an enclosing one.

## Everyday commands

```bash
./git-swagata add docs/EXAMPLE_FILE.md
./git-swagata commit -m "Describe Swagata's actual change"

./git-sumit add tests/EXAMPLE_FILE.py
./git-sumit commit -m "Describe Sumit's actual change"
```

The paths/messages above are examples; replace them with actual changed files. Both wrappers use the **same staging area**. Stage only the intended person's changes before committing. Review with `git diff --cached` when alternating contributors.

Inspect the chosen identity without committing:

```bash
./git-swagata var GIT_AUTHOR_IDENT
./git-sumit var GIT_AUTHOR_IDENT
```

After a genuine commit, inspect it using `git log -1 --format=fuller`. No old commit authors are changed by configuring the wrappers.

## One token for pushing

Use a token belonging to an account that has write access to the destination repository. A token cannot grant permissions its owner does not have. Repository access and commit author emails are separate concerns.

For a temporary token-based HTTPS push without storing a token in this project:

```bash
git config --local credential.useHttpPath true
git config --local credential.username 'TOKEN_OWNER_GITHUB_USERNAME'
git -c credential.helper= push -u origin main
```

At the terminal's password prompt, enter the token. The command disables credential helpers **for this invocation only** and does not save the token in a file or remote URL. Run from an interactive terminal. Depending on your terminal setup an askpass dialog may supply the prompt. Subsequent pushes may prompt again; secure credential-manager storage can be configured separately if desired.

Use the token owner's username for authentication—not whichever author wrapper was used most recently. The remote should be an ordinary URL such as `https://github.com/Swagata-Bhowmik/group4-mlflow-capstone.git`, with no token embedded. Confirm the actual repository exists and is the intended destination before setting it. No remote has been configured by adding these wrappers.

For a fine-grained token, select the repository and grant Contents read/write. Pushing the provided `.github/workflows/` files also requires the appropriate Workflows write permission. Account/repository policy may require approval; follow GitHub's token settings rather than broadening access unnecessarily. Never paste the token into chat, scripts, commit messages, or the repository.

## What was actually done

Created two executable wrappers and their shared implementation/documentation. No global Git settings were changed. No account was authenticated, token stored, project Git repository initialized, commit created, or push performed. Configure verified emails after the repository is initialized. Wrapper setup is now authorized; actual identities and repository/authentication configuration remain to be supplied securely.

References: [Git command-specific options](https://git-scm.com/docs/git), [local configuration](https://git-scm.com/docs/git-config), [GitHub personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).
