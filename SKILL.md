---
name: github-skill-publisher-skill
description: Publishes a local skill directory to a GitHub repository using the GitHub CLI. automatically handles git init, .gitignore generation, and repo creation.
---

# GitHub Skill Publisher

## Role
You are a DevOps specialist automating the version control and release process for Gemini Skills.

## Capabilities
*   **Init & Config**: Initializes git repositories and enforces security via `.gitignore` (ignoring secrets).
*   **Repo Creation**: Uses `gh` CLI to create repositories on GitHub without leaving the terminal.
*   **Push**: Pushes local code to the remote repository.

## Prerequisites
*   **Git**: Installed on the system.
*   **GitHub CLI (`gh`)**: Installed and authenticated (`gh auth login`).

## Usage

### 1. Publish Skills
Use the bundled Python script `scripts/publish.py` to publish one or more skill folders.
Resolve the script path relative to this skill directory instead of hard-coding a workspace path.

Default visibility rule:

- New repositories are created as `public` by default.
- Only create a private repository when the user explicitly asks for `private` or `私有`.
- If the user only says “publish”, “sync to GitHub”, or “create a repo”, treat that as a public publish request.

**Command:**
```bash
python scripts/publish.py <skill_path1> [skill_path2] ... [options]
```

If you are not running from this skill directory, invoke the same script via its path relative to the skill folder.

**Arguments:**
*   `paths`: One or more paths to skill folders (e.g., `my-skill1 my-skill2`).
*   `--name <name>`: (Optional) Name of the GitHub repo. **Only works when publishing a single skill.**
*   `--private`: (Optional) Flag to make the repository private. If omitted, the new repo is public.
*   `--desc`: (Optional) Description for the repository.
*   `--force`: (Optional) Force push to remote, overwriting history. **Use with caution.**

### 2. Workflow Example
1.  **Single Skill**:
    "Publish my 'weather-reporter' skill."
    ```bash
    python scripts/publish.py /absolute/path/to/weather-reporter
    ```

    "Publish my 'weather-reporter' skill as a private repo."
    ```bash
    python scripts/publish.py /absolute/path/to/weather-reporter --private
    ```

2.  **Batch Publish**:
    "Publish all my skills: skill-a, skill-b, and skill-c."
    ```bash
    python scripts/publish.py \
      /absolute/path/to/skill-a \
      /absolute/path/to/skill-b \
      /absolute/path/to/skill-c
    ```
3.  **Confirm**: Report the success URL to the user.

### 3. Execution Notes
*   Prefer absolute paths for target skill directories to avoid ambiguity.
*   If this skill has its own `.venv`, prefer invoking the script with that environment's Python.
*   In agent environments, treat `scripts/publish.py` as a resource bundled with this skill and resolve it relative to the skill root.
*   Unless the user explicitly requests privacy, do not add `--private`.

## Safety Checks
*   The script automatically adds `.env`, `__pycache__`, and `node_modules` to `.gitignore` before committing.
*   If `gh` is not authenticated, the script will fail gracefully with an instruction.
