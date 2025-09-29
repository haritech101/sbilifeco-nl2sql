from math import e
from git import Repo
from pathlib import Path
from subprocess import run
from re import search
from toml import load

repo_path = Path("../..").resolve()
print(f"Repo path is {repo_path}")

with Repo(repo_path) as repo:
    if not repo.is_dirty(untracked_files=True):
        print("Repository has no changes. Nothing to examine.")
        exit(0)

    changed_files = [item.a_path for item in repo.index.diff(None)]
    changed_files.extend(repo.untracked_files)

    libraries = [
        Path(search("(.*)/src/.*", changed_file)[1])
        for changed_file in changed_files
        if "src" in str(changed_file)
    ]

    libraries.extend(
        [
            Path(search("(.*)/pyproject.toml", changed_file)[1])
            for changed_file in changed_files
            if "pyproject.toml" in str(changed_file)
        ]
    )

    libraries = list(set(libraries))

    print("Changed libraries")
    for i, library_path in enumerate(libraries, 1):
        print(f" - {i}. {library_path}")

    for library_path in libraries:
        pyproject_toml = load(repo_path / library_path / "pyproject.toml")

        library_name = pyproject_toml.get("project", {}).get("name")
        version_in_toml = pyproject_toml.get("project", {}).get("version")

        print(f"\nExamining {library_name}")
        print(f" - Version in pyproject.toml is {version_in_toml}")

        version_in_pip = "0.0.0"
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
                timeout=5,
            )

            version_matches = search(r"LATEST:\s*(.*)", shell_output.stdout)
            if not version_matches:
                print(f" - Unable to retrieve installed version of {library_name}")
                continue

            version_in_pip = version_matches[1]
        except Exception as e:
            print(f" - Could not get installed version of {library_name}: {e}")
            continue

        print(f" - Version in pip is {version_in_pip}")

        if version_in_toml != version_in_pip:
            print(
                f" - Version in pyproject.toml is correctly bumped up to {version_in_toml}"
            )
            continue

        print(
            " - There are changes in the library code. Please bump up the version in pyproject.toml"
        )
        # TODO: Optionally, we can auto-bump the version here.
