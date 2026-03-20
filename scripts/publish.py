#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None, exit_on_error=True):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if exit_on_error:
            print(f"Error executing command: {command}")
            print(f"Stderr: {e.stderr}")
            sys.exit(1)
        return None

def check_dependencies():
    """Check if git and gh are installed."""
    if run_command("which git", exit_on_error=False) is None:
        print("Error: 'git' is not installed.")
        sys.exit(1)
    
    if run_command("which gh", exit_on_error=False) is None:
        print("Error: GitHub CLI ('gh') is not installed. Please install it: brew install gh")
        sys.exit(1)
        
    # Check gh auth status
    auth_status = run_command("gh auth status", exit_on_error=False)
    if auth_status is None:
        print("Error: You are not logged into GitHub CLI. Please run 'gh auth login' first.")
        sys.exit(1)

def ensure_gitignore(target_path):
    """Create or update .gitignore with essential patterns."""
    gitignore_path = target_path / ".gitignore"
    essential_ignores = {
        ".env",
        ".DS_Store",
        "__pycache__/",
        "*.pyc",
        "node_modules/",
        "dist/",
        "build/",
        "*.egg-info/",
        ".venv/",
        "venv/"
    }
    
    existing_ignores = set()
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            existing_ignores = set(line.strip() for line in f if line.strip())
            
    missing_ignores = essential_ignores - existing_ignores
    
    if missing_ignores:
        print(f"Adding {len(missing_ignores)} patterns to .gitignore...")
        with open(gitignore_path, "a") as f:
            f.write("\n# Added by github-skill-publisher\n")
            for ignore in missing_ignores:
                f.write(f"{ignore}\n")

def ensure_readme(skill_path):
    """Ensure README.md exists, generate from SKILL.md if missing."""
    readme_path = skill_path / "README.md"
    if readme_path.exists():
        print("README.md already exists.")
        return

    skill_md_path = skill_path / "SKILL.md"
    if not skill_md_path.exists():
        print("Warning: SKILL.md not found, skipping README generation.")
        return

    print("Generating README.md from SKILL.md...")
    
    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Simple frontmatter parsing
    lines = content.splitlines()
    name = "Unknown Skill"
    description = "No description provided."
    body_start = 0
    
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                body_start = i + 1
                break
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip()
            elif line.startswith("description:"):
                description = line.split(":", 1)[1].strip()

    body = "\n".join(lines[body_start:]).strip()

    readme_content = f"""# {name}

{description}

## Installation

This is a skill for [Gemini CLI](https://github.com/google/gemini-cli).

To install this skill:

1. Clone this repository.
2. Run the install command:

```bash
gemini skills install ./{name}
```

## Documentation

{body}
"""
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ Generated README.md")

def publish_skill(skill_path_str, repo_name, is_private, description, force=False):
    skill_path = Path(skill_path_str).resolve()
    
    if not skill_path.exists():
        print(f"Error: Skill directory not found: {skill_path}")
        sys.exit(1)

    print(f"🚀 Preparing to publish skill from: {skill_path}")
    print(f"🌐 Target visibility: {'private' if is_private else 'public (default)'}")
    
    # 1. Initialize Git if needed
    if not (skill_path / ".git").exists():
        print("Initializing git repository...")
        run_command("git init", cwd=skill_path)
    
    # 2. Setup .gitignore and README.md
    ensure_gitignore(skill_path)
    ensure_readme(skill_path)
    
    # 3. Stage and Commit
    print("Staging files...")
    run_command("git add .", cwd=skill_path)
    
    status = run_command("git status --porcelain", cwd=skill_path)
    if status:
        print("Committing changes...")
        run_command('git commit -m "Initial commit by github-skill-publisher"', cwd=skill_path)
    else:
        print("No changes to commit.")

    # 4. Create/Link Remote Repo
    remotes = run_command("git remote", cwd=skill_path)
    
    if "origin" not in remotes:
        print(f"Creating GitHub repository '{repo_name}'...")
        visibility_flag = "--private" if is_private else "--public"
        
        # Try to create repo. We REMOVE --push here to handle it safely later.
        cmd = f"gh repo create {repo_name} {visibility_flag} --source=. --remote=origin"
        if description:
            cmd += f' --description "{description}"'
        
        if run_command(cmd, cwd=skill_path, exit_on_error=False) is None:
            print(f"⚠️ Repo creation failed (likely exists). Linking manually...")
            # Fallback: link to expected URL
            user = run_command("gh api user -q .login")
            remote_url = f"https://github.com/{user}/{repo_name}.git"
            run_command(f"git remote add origin {remote_url}", cwd=skill_path, exit_on_error=False)

    # 5. Safe Push Logic
    print("Pushing to remote...")
    # Try normal push first
    if run_command("git push -u origin HEAD", cwd=skill_path, exit_on_error=False) is None:
        # Push failed
        if force:
            print("⚠️ Push rejected. Force pushing (--force)...")
            run_command("git push -u origin HEAD --force", cwd=skill_path)
        else:
            print("❌ Push rejected. Remote contains work that you do not have locally.")
            print("   💡 Tip: Run with '--force' to overwrite remote history.")
            raise Exception("Push rejected without --force")

    print(f"✅ Successfully published/updated {repo_name}")

def main():
    parser = argparse.ArgumentParser(description='Publish local skills to GitHub')
    parser.add_argument('paths', nargs='+', help='Paths to the skill directories')
    parser.add_argument('--name', help='Name of the GitHub repo (only works when publishing a single skill)')
    parser.add_argument('--private', action='store_true', help='Make the repository private. If omitted, new repositories are public by default.')
    parser.add_argument('--desc', help='Repository description')
    parser.add_argument('--force', action='store_true', help='Force push to remote (DANGEROUS: overwrites remote history)')

    args = parser.parse_args()
    
    check_dependencies()
    
    for path in args.paths:
        repo_name = os.path.basename(os.path.normpath(path))
        
        # Use --name only if a single skill is being published
        if len(args.paths) == 1 and args.name:
            repo_name = args.name
            
        print(f"\n📦 Processing Skill: {repo_name}")
        try:
            publish_skill(path, repo_name, args.private, args.desc, args.force)
        except Exception as e:
            print(f"❌ Failed to publish {repo_name}: {e}")

if __name__ == '__main__':
    main()
