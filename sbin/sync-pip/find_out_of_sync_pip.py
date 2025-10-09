from pathlib import Path
from toml import load
from subprocess import run
from sys import executable
from re import search

LIBS_DIR = Path("../..").resolve()
print(f"Libraries are in the path: {LIBS_DIR}\n\n")

print("Searching for pyproject.toml files...\n\n")
pyprojects = [
    pyproject
    for pyproject in Path(LIBS_DIR).rglob("pyproject.toml")
    if ".venv" not in str(pyproject)
]

library_path_stubs = [
    f"{str(pyproject).replace(str(LIBS_DIR) + "/", '').replace('/pyproject.toml', '')}"
    for pyproject in pyprojects
]

library_names: list[str] = []
for library_path in library_path_stubs:
    toml_path = LIBS_DIR / library_path / "pyproject.toml"
    with open(toml_path, "r") as toml_file:
        toml_tree = load(toml_file)

        library_name = toml_tree.get("project", {}).get("name", "unknown")
        library_names.append(library_name)

dirty_libs = []
for library_name in library_names:
    print(f"\n\nChecking {library_name}")

    try:
        pip_output = run(
            [executable, "-m", "pip", "show", library_name],
            text=True,
            capture_output=True,
            timeout=2,
            check=True,
        )

        pip_output_lines = pip_output.stdout.splitlines()
        version_in_env = "unknown"
        for line in pip_output_lines:
            if line.startswith("Version:"):
                version_in_env = line.replace("Version:", "").strip()
                break
        print(f"Version in environment: {version_in_env}")
    except Exception as e:
        print(f"Could not get version from pip: {e}")
        version_in_env = "0.0.0"

    try:
        shell_output = run(
            [
                "pip",
                "index",
                "versions",
                "--extra-index-url",
                "https://api.repoforge.io/yWf4uV/",
                library_name,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        version_matches = search(r"LATEST:\s*(.*)", shell_output.stdout)
        if not version_matches:
            print(f" - Unable to retrieve hosted version of {library_name}")
            continue

        version_in_pip = version_matches[1]
        print(f"Version in pip: {version_in_pip}")
    except Exception as e:
        print(f" - Could not get hosted version of {library_name}: {e}")
        version_in_pip = "0.0.0"

    if version_in_env == version_in_pip:
        print(f"{library_name} is up to date @ {version_in_env}")
    else:
        print(f"{library_name} is out of date! Need to twupload")
        dirty_libs.append(f"{library_name}=={version_in_env}")

if dirty_libs:
    print("\n\nThe following libraries are out of date and need to be uploaded:")
    for dirty_lib in dirty_libs:
        print(f" - {dirty_lib}")
