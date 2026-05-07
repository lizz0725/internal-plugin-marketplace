#!/usr/bin/env python3
"""
Claude Code Plugin Marketplace - Sync Script
=============================================
Syncs plugins from upstream sources defined in sources.json.

Usage:
    python sync_plugins.py              # Sync all pending plugins
    python sync_plugins.py --all        # Force sync all (even if unchanged)
    python sync_plugins.py --name foo   # Sync only specified plugin
    python sync_plugins.py --status     # Show sync status only, no action
    python sync_plugins.py --init       # First-time: clone all with pending status
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_REPO = REPO_ROOT / "plugins-repo"
SOURCES_FILE = PLUGINS_REPO / "sources.json"
MARKETPLACE_FILE = PLUGINS_REPO / ".claude-plugin" / "marketplace.json"
TEMP_DIR = Path("/tmp") / "plugin-marketplace-sync"
GIT_TIMEOUT = 120  # seconds
MAX_RETRIES = 2


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def run_git(args, cwd=None, timeout=GIT_TIMEOUT):
    """Run a git command and return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(
            ["git"] + args,
            cwd=cwd or str(PLUGINS_REPO),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except FileNotFoundError:
        return -1, "", "git not found"


def load_sources():
    with open(SOURCES_FILE) as f:
        return json.load(f)


def save_sources(data):
    with open(SOURCES_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_remote_head(repo_url, ref="main"):
    """Get the latest commit SHA from a remote ref."""
    for attempt in range(MAX_RETRIES):
        rc, out, err = run_git(["ls-remote", repo_url, ref])
        if rc == 0 and out:
            sha = out.split()[0]
            return sha
        log(f"  ls-remote attempt {attempt + 1} failed: {err[:100]}")
        time.sleep(2)
    return None


def shallow_clone_ref(repo_url, ref, dest_dir):
    """Shallow clone a repo branch/ref into dest_dir using 'git clone --depth 1'."""
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    try:
        r = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", ref,
             "--single-branch", "--", repo_url, str(dest_dir)],
            capture_output=True, text=True, timeout=300,
        )
        if r.returncode != 0:
            log(f"  git clone failed: {r.stderr[:100]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        log("  git clone timed out (300s)")
        return False
    except FileNotFoundError:
        log("  git not found")
        return False


def shallow_clone_ref_sparse(repo_url, ref, dest_dir, sparse_paths=None):
    """Clone with partial fetch + sparse checkout for large repos.

    Uses git init + remote add + fetch --depth 1 --filter=blob:none + sparse-checkout
    to minimize data transfer. Only the files under sparse_paths are checked out.
    """
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Init empty repo
        r = subprocess.run(
            ["git", "init"], cwd=dest_dir, capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0:
            log(f"  git init failed: {r.stderr[:80]}")
            return False

        # Add remote
        r = subprocess.run(
            ["git", "remote", "add", "origin", repo_url],
            cwd=dest_dir, capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0:
            log(f"  git remote add failed: {r.stderr[:80]}")
            return False

        # Fetch with blob:none filter and HTTP/1.1 to avoid HTTP2 framing errors
        r = subprocess.run(
            ["git", "-c", "http.version=HTTP/1.1", "fetch", "--depth", "1",
             "--filter=blob:none", "origin", ref],
            cwd=dest_dir, capture_output=True, text=True, timeout=300,
        )
        if r.returncode != 0:
            log(f"  git fetch failed: {r.stderr[:120]}")
            return False

        # Sparse checkout to limit disk usage
        if sparse_paths:
            r = subprocess.run(
                ["git", "sparse-checkout", "init", "--cone"],
                cwd=dest_dir, capture_output=True, text=True, timeout=30
            )
            if r.returncode == 0:
                r = subprocess.run(
                    ["git", "sparse-checkout", "set"] + sparse_paths,
                    cwd=dest_dir, capture_output=True, text=True, timeout=30
                )

        # Checkout
        r = subprocess.run(
            ["git", "checkout", "FETCH_HEAD"],
            cwd=dest_dir, capture_output=True, text=True, timeout=120,
        )
        if r.returncode != 0:
            log(f"  git checkout failed: {r.stderr[:80]}")
            return False

        return True
    except subprocess.TimeoutExpired:
        log("  sparse clone timed out")
        return False
    except FileNotFoundError:
        log("  git not found")
        return False


def find_claude_plugin_dir(source_dir):
    """Find the .claude-plugin directory. Could be at root or one level deep."""
    candidates = [
        source_dir / ".claude-plugin",
        source_dir / "skills" / ".claude-plugin",
    ]
    for p in candidates:
        if p.exists() and (p / "plugin.json").exists():
            return p
    # Walk one level deep looking for .claude-plugin dirs
    for item in source_dir.iterdir():
        if item.is_dir():
            cp = item / ".claude-plugin"
            if cp.exists() and (cp / "plugin.json").exists():
                return cp
    return None


def copy_plugin(source_plugin_dir, target_plugin_dir):
    """Copy .claude-plugin/ to target, preserving structure."""
    if target_plugin_dir.exists():
        shutil.rmtree(target_plugin_dir)
    target_plugin_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_plugin_dir, target_plugin_dir)
    return True


def write_source_file(target_plugin_dir, source_info):
    """Write per-plugin source.json."""
    source_file = target_plugin_dir.parent / "source.json"
    with open(source_file, "w") as f:
        json.dump(source_info, f, indent=2, ensure_ascii=False)
        f.write("\n")


def generate_marketplace_json(sources_data) -> list:
    """Generate the .claude-plugin/marketplace.json from sources data."""
    plugins_list = []
    for entry in sources_data.get("plugins", []):
        name = entry["name"]
        plugin_json_path = PLUGINS_REPO / "plugins" / name / ".claude-plugin" / "plugin.json"
        if not plugin_json_path.exists():
            log(f"  WARNING: plugin.json not found for '{name}', skipping marketplace entry")
            continue
        try:
            with open(plugin_json_path) as f:
                meta = json.load(f)
        except (json.JSONDecodeError, IOError):
            log(f"  WARNING: invalid plugin.json for '{name}', skipping marketplace entry")
            continue

        plugins_list.append({
            "name": meta.get("name", name),
            "description": meta.get("description", entry.get("description", "")),
            "category": entry.get("category", "community"),
            "source": f"./plugins/{name}/.claude-plugin",
        })
    return plugins_list


def sync_plugin(entry, force=False) -> bool:
    """Sync a single plugin from upstream. Returns True if updated."""
    source = entry.get("source", {})
    source_type = source.get("type", "manual")

    if source_type == "manual":
        log(f"  SKIP (manual source)")
        return False

    repo_url = source.get("repo_url", "")
    repo_ref = source.get("repo_ref", "main")
    current_sha = source.get("commit_sha", "")
    subdir = source.get("subdir")
    name = entry["name"]

    # Check remote head
    new_sha = get_remote_head(repo_url, repo_ref)
    if not new_sha:
        log(f"  FAILED to get remote head")
        return False

    target_plugin_dir = PLUGINS_REPO / "plugins" / name / ".claude-plugin"
    has_files = target_plugin_dir.exists() and (target_plugin_dir / "plugin.json").exists()

    if new_sha == current_sha and has_files and not force:
        source["last_sync_status"] = "unchanged"
        log(f"  UNCHANGED ({new_sha[:12]})")
        return False

    log(f"  Updating: {current_sha[:12] if current_sha else 'none'} -> {new_sha[:12]}")

    # Clone the repo (try regular shallow clone first, fall back to sparse)
    clone_dir = TEMP_DIR / f"{name}_{int(time.time())}"
    cloned = shallow_clone_ref(repo_url, repo_ref, clone_dir)
    if not cloned:
        log(f"  Retrying with sparse checkout...")
        cloned = shallow_clone_ref_sparse(repo_url, repo_ref, clone_dir, [".claude-plugin"])
    if not cloned:
        source["last_sync_status"] = "failed"
        log(f"  FAILED: clone error")
        if clone_dir.exists():
            shutil.rmtree(clone_dir)
        return False

    # Find the plugin subdirectory within the clone
    if subdir:
        source_dir = clone_dir / subdir
        if not source_dir.exists():
            log(f"  FAILED: subdir '{subdir}' not found in clone")
            source["last_sync_status"] = "failed"
            shutil.rmtree(clone_dir)
            return False
    else:
        source_dir = clone_dir

    # Find .claude-plugin/ directory
    plugin_dir = find_claude_plugin_dir(source_dir)
    if not plugin_dir:
        log(f"  FAILED: no .claude-plugin/plugin.json found")
        source["last_sync_status"] = "failed"
        shutil.rmtree(clone_dir)
        return False

    # Copy to target
    target_plugin_dir = PLUGINS_REPO / "plugins" / name / ".claude-plugin"
    copy_plugin(plugin_dir, target_plugin_dir)

    # Write per-plugin source.json
    write_source_file(target_plugin_dir, {
        "name": name,
        "source": {
            "type": source_type,
            "repo_url": repo_url,
            "commit_sha": new_sha,
            "subdir": subdir,
            "last_sync_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "installed_path": f"./plugins/{name}/.claude-plugin",
    })

    # Update sources.json entry
    source["commit_sha"] = new_sha
    source["last_sync_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    source["last_sync_status"] = "success"

    log(f"  UPDATED ({new_sha[:12]})")
    shutil.rmtree(clone_dir)
    return True


def do_sync(sources_data, force=False, plugin_name=None):
    """Run the sync for all (or specified) plugins."""
    updated_count = 0
    unchanged_count = 0
    failed_count = 0
    skipped_count = 0

    plugins = sources_data.get("plugins", [])
    if plugin_name:
        plugins = [p for p in plugins if p["name"] == plugin_name]
        if not plugins:
            log(f"Plugin '{plugin_name}' not found in sources.json")
            return 0, 0, 1

    for entry in plugins:
        name = entry["name"]
        source = entry.get("source", {})
        stype = source.get("type", "manual")

        if not force and source.get("last_sync_status") == "success" and source.get("commit_sha"):
            # Check if it's a manual entry
            if stype == "manual":
                skipped_count += 1
                continue

        log(f"  [{name}] ({stype})...")
        try:
            if stype in ("github_single", "github_monorepo"):
                if sync_plugin(entry, force=force):
                    updated_count += 1
                else:
                    status = source.get("last_sync_status", "")
                    if status == "failed":
                        failed_count += 1
                    else:
                        unchanged_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            log(f"  ERROR: {e}")
            source["last_sync_status"] = "failed"
            failed_count += 1

    save_sources(sources_data)
    return updated_count, unchanged_count, failed_count


def regenerate_marketplace(sources_data):
    """Regenerate .claude-plugin/marketplace.json from current state."""
    plugins_list = generate_marketplace_json(sources_data)

    marketplace = {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": "cc-plugin-marketplace",
        "description": "Claude Code Plugin Marketplace - Curated collection of popular plugins and skills",
        "owner": {
            "name": "Marketplace Admin",
        },
        "plugins": plugins_list,
    }

    MARKETPLACE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MARKETPLACE_FILE, "w") as f:
        json.dump(marketplace, f, indent=2, ensure_ascii=False)
        f.write("\n")

    log(f"  Regenerated marketplace.json with {len(plugins_list)} plugins")


def commit_and_push(message):
    """Commit changes and push to all configured remotes."""
    # Check if anything changed
    rc, out, err = run_git(["status", "--porcelain"])
    if not out.strip():
        log("  Nothing to commit")
        return True

    # Stage all
    rc, _, err = run_git(["add", "-A"])
    if rc != 0:
        log(f"  git add failed: {err[:100]}")
        return False

    # Commit
    rc, _, err = run_git(["commit", "-m", message])
    if rc != 0:
        if "nothing to commit" in err.lower():
            log("  Nothing to commit")
            return True
        log(f"  git commit failed: {err[:200]}")
        return False

    log(f"  Committed: {message}")

    # Push to all remotes
    sources_data = load_sources()
    remotes = sources_data.get("remotes", [])
    for remote in remotes:
        name = remote["name"]
        url = remote["url"]
        branch = remote.get("push_branch", "master")

        # Ensure remote exists
        run_git(["remote", "add", name, url])
        run_git(["remote", "set-url", name, url])

        log(f"  Pushing to {name} ({branch})...")
        rc, _, err = run_git(["push", name, branch], timeout=60)
        if rc != 0:
            log(f"  WARNING: push to {name} failed: {err[:200]}")
        else:
            log(f"  Pushed to {name} successfully")

        # Push tags
        run_git(["push", name, "--tags"], timeout=30)

    return True


def show_status():
    """Display sync status for all plugins."""
    sources_data = load_sources()
    plugins = sources_data.get("plugins", [])

    print(f"\n{'Name':25s} {'Status':12s} {'Type':16s} {'Last Sync':25s} {'Commit'}")
    print("-" * 100)
    for entry in plugins:
        source = entry.get("source", {})
        name = entry["name"]
        status = source.get("last_sync_status", "unknown")
        stype = source.get("type", "manual")
        last_sync = source.get("last_sync_at", "")[:19] if source.get("last_sync_at") else ""
        sha = (source.get("commit_sha", "") or "")[:12]
        print(f"{name:25s} {status:12s} {stype:16s} {last_sync:25s} {sha}")

    print(f"\nTotal: {len(plugins)} plugins")


def ensure_plugins_dir():
    """Ensure plugins/ directory exists."""
    (PLUGINS_REPO / "plugins").mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Sync plugins from upstream sources")
    parser.add_argument("--all", action="store_true", help="Force sync all plugins")
    parser.add_argument("--name", type=str, help="Sync only a specific plugin")
    parser.add_argument("--status", action="store_true", help="Show sync status only")
    parser.add_argument("--init", action="store_true", help="Initial sync of all pending plugins")
    parser.add_argument("--no-push", action="store_true", help="Skip git push")
    args = parser.parse_args()

    if not SOURCES_FILE.exists():
        log(f"ERROR: {SOURCES_FILE} not found")
        sys.exit(1)

    if args.status:
        show_status()
        return

    ensure_plugins_dir()
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    sources_data = load_sources()
    force = args.all or args.init

    log(f"Starting sync...")
    start = time.time()

    updated, unchanged, failed = do_sync(sources_data, force=force, plugin_name=args.name)

    elapsed = time.time() - start
    log(f"Sync complete: {updated} updated, {unchanged} unchanged, {failed} failed ({elapsed:.1f}s)")

    # Regenerate marketplace.json
    sources_data = load_sources()  # Reload in case it was updated
    regenerate_marketplace(sources_data)

    # Update last_updated
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sources_data["last_updated"] = now
    save_sources(sources_data)

    # Commit and push (unless --no-push)
    if updated > 0 or args.init:
        if args.init:
            msg = f"sync: initial import of plugins ({now[:10]})"
        else:
            msg = f"sync: updated {updated} plugins, {unchanged} unchanged, {failed} failed ({now[:10]})"
        if args.no_push:
            log("  --no-push: skipping commit and push")
            # Still stage changes so user can inspect
            run_git(["add", "-A"])
        else:
            commit_and_push(msg)
    else:
        log("No changes to commit")

    # Cleanup temp dir
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
