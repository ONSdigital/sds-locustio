import sys

from tomlkit import dumps, parse


def bump_major(version: str) -> str:
    major, minor, patch = map(int, version.split("."))
    major += 1
    minor = 0
    patch = 0
    return f"{major}.{minor}.{patch}"

def bump_minor(version: str) -> str:
    major, minor, patch = map(int, version.split("."))
    minor += 1
    patch = 0
    return f"{major}.{minor}.{patch}"

def bump_patch(version: str) -> str:
    major, minor, patch = map(int, version.split("."))
    patch += 1
    return f"{major}.{minor}.{patch}"


actions  = {
    "major": bump_major,
    "minor": bump_minor,
    "patch": bump_patch,
}

# --- read TOML ---
with open("pyproject.toml") as f:
    pyproject = parse(f.read())

# --- get action from args ---
action = sys.argv[1] if len(sys.argv) > 1 else "patch"

if action not in actions:
    print(f"Unknown action: {action}")
    sys.exit(1)

# --- bump version ---
current_version = pyproject["project"]["version"]
new_version = actions[action](current_version)
pyproject["project"]["version"] = new_version

# --- write back ---
with open("pyproject.toml", "w") as f:
    f.write(dumps(pyproject))

print(f"Version bumped: {current_version} → {new_version}")
