"""Local release checks. Reports paths/categories, never potential secret values."""

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "api_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
}


def main():
    files = (
        subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT
        )
        .decode()
        .split("\0")
    )
    findings = []
    from dotenv import dotenv_values

    credentials = []
    for candidate in (ROOT / ".env", ROOT.parent / ".env"):
        if candidate.is_file():
            credentials.extend(
                v
                for k, v in dotenv_values(candidate).items()
                if k.endswith("API_KEY") and v and len(v) >= 12
            )
            break
    for name in filter(None, files):
        path = ROOT / name
        if path.name.startswith(".env") and path.name != ".env.example":
            findings.append({"path": name, "kind": "environment-file"})
        try:
            text = path.read_text()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        if any(value in text for value in credentials):
            findings.append({"path": name, "kind": "active-credential-exact-match"})
        for kind, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append({"path": name, "kind": kind})
    # Presence checks do not print or inspect secret contents.
    ignored_env = (ROOT / ".env").exists()
    result = {
        "tracked_files": len([x for x in files if x]),
        "findings": findings,
        "local_env_present": ignored_env,
        "scope": "pattern and active-credential exact-match scan of tracked and unignored candidate text; not a comprehensive secret or privacy audit",
    }
    print(json.dumps(result, indent=2))
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
