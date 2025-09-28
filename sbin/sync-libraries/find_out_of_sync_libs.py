from pathlib import Path
from toml import load
from sys import executable
from subprocess import run
from os import chdir

LIBS_DIR = Path("../..").resolve()
print(f"Libraries are in the path: {LIBS_DIR}\n\n")

print("Searching for pyproject.toml files...\n\n")
pyprojects = [pyproject for pyproject in Path(LIBS_DIR).rglob("pyproject.toml")]

print("The following libraries were found:\n\n")

library_path_stubs = [
    f"- {str(pyproject).replace(str(LIBS_DIR), '').replace('/pyproject.toml', '')}"
    for pyproject in pyprojects
]
for path_stub in library_path_stubs:
    print(path_stub)
print("\n\n")

dirty_libs = []
for i, pyproject in enumerate(pyprojects):
    print(f"Checking library {library_path_stubs[i]}\n")

    with open(pyproject, "r") as toml_file:
        toml_tree = load(toml_file)

        library_name = toml_tree.get("project", {}).get("name", "unknown")
        print(f"Library name: {library_name}")

        version_in_codebase = toml_tree.get("project", {}).get("version", "0.0.0")
        print(f"Version in project: {version_in_codebase}")

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

            if version_in_codebase != version_in_env:
                dirty_libs.append(pyproject.parent.resolve())
        except Exception as e:
            print(f"Could not get version from pip: {e}")
            version_in_env = "0.0.0"
            dirty_libs.append(pyproject.parent.resolve())

        print("\n\n")

if not dirty_libs:
    print("All libraries are in sync!")
    exit(0)

for dirty_lib in dirty_libs:
    print(f"Library {dirty_lib} is out of sync\n")

    print(f"Changing working directory to {dirty_lib}")
    chdir(dirty_lib)

    run([executable, "-m", "build"], check=True)
    run([executable, "-m", "pip", "install", "."], check=True)

    print("\n\n")
