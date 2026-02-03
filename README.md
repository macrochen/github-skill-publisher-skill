# github-skill-publisher-skill

Publishes a local skill directory to a GitHub repository using the GitHub CLI. automatically handles git init, .gitignore generation, and repo creation.

## Installation

This is a skill for [Gemini CLI](https://github.com/google/gemini-cli).

To install this skill:

1. Clone this repository.
2. Run the install command:

```bash
gemini skills install ./github-skill-publisher-skill
```

## Documentation

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
Use the Python script to publish one or more skill folders.

**Command:**
```bash
python .gemini/skills/github-skill-publisher/scripts/publish.py <skill_path1> [skill_path2] ... [options]
```

**Arguments:**
*   `paths`: One or more paths to skill folders (e.g., `my-skill1 my-skill2`).
*   `--name <name>`: (Optional) Name of the GitHub repo. **Only works when publishing a single skill.**
*   `--private`: (Optional) Flag to make the repository private.
*   `--desc`: (Optional) Description for the repository.
*   `--force`: (Optional) Force push to remote, overwriting history. **Use with caution.**

### 2. Workflow Example
1.  **Single Skill**:
    "Publish my 'weather-reporter' skill."
    ```bash
    python .gemini/skills/github-skill-publisher/scripts/publish.py workspace/my-skills/weather-reporter --private
    ```

2.  **Batch Publish**:
    "Publish all my skills: skill-a, skill-b, and skill-c."
    ```bash
    python .gemini/skills/github-skill-publisher/scripts/publish.py \
      workspace/my-skills/skill-a \
      workspace/my-skills/skill-b \
      workspace/my-skills/skill-c
    ```
3.  **Confirm**: Report the success URL to the user.

## Safety Checks
*   The script automatically adds `.env`, `__pycache__`, and `node_modules` to `.gitignore` before committing.
*   If `gh` is not authenticated, the script will fail gracefully with an instruction.
