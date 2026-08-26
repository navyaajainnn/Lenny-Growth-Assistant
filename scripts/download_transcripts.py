import shutil
import subprocess
import tempfile
from pathlib import Path


REPOSITORY = "https://github.com/ChatPRD/lennys-podcast-transcripts.git"


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    destination = project_root / "data" / "transcripts"
    with tempfile.TemporaryDirectory() as temporary_directory:
        checkout = Path(temporary_directory) / "archive"
        subprocess.run(
            ["git", "clone", "--depth", "1", REPOSITORY, str(checkout)],
            check=True,
        )
        destination.mkdir(parents=True, exist_ok=True)
        for source in (checkout / "episodes").rglob("transcript.md"):
            target = destination / source.relative_to(checkout / "episodes")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    count = len(list(destination.rglob("transcript.md")))
    print(f"Downloaded {count} transcripts into {destination}")


if __name__ == "__main__":
    main()