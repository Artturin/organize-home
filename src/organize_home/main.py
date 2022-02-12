"""
organize my home
"""
import shutil
import subprocess
from pathlib import Path


def move_not_my_repos(home_path: Path) -> None:
    """move repos that are not mine to gits/NotMyGits"""
    dest_dir = home_path.joinpath("gits/NotMyGits").resolve()
    dest_dir.mkdir(exist_ok=True)
    for child in home_path.iterdir():
        g_dir = child.joinpath(".git").resolve()
        if g_dir.is_dir():
            if g_conf := g_dir.joinpath("config"):
                if "Artturin/".lower() not in g_conf.read_text().lower() and child.name.lower() not in [
                    "organize-home",
                    "nixos-gen-config",
                ]:
                    print(f"{child}")
                    try:
                        # shutil.copytree was much slower and did not copy symlinks properly
                        subprocess.run(["rsync", "-aP", "--remove-source-files", str(child), str(dest_dir)], check=True)
                    except subprocess.CalledProcessError as err:
                        print(f"{child} {err}\n")
                        continue
                    try:
                        subprocess.run(["trash-put", str(child)], check=True)
                    except subprocess.CalledProcessError as err:
                        print(f"FAILED TO MOVE {child} TO TRASH {err}\n")


def move_files(home_path: Path, extensions: list[str], destination: Path) -> None:
    """move files"""
    for child in home_path.iterdir():
        if child.is_file() and [s for s in child.suffixes if any(xs in s for xs in extensions)]:
            destination.mkdir(exist_ok=True)
            moved = ""
            try:
                moved = shutil.move(child, destination)
            except shutil.Error as err:
                print(err)
                continue
            print(f"{child} -> {moved}")


def main() -> None:
    """main"""
    home_path = Path.home()
    doc_path = home_path.joinpath("Documents")
    move_not_my_repos(home_path)

    image_extensions: list[str] = [".jpg", ".jpeg", ".png", ".gif"]
    image_dest = doc_path.joinpath("bookmarkpics")

    video_extensions: list[str] = [".mp4", ".webm", ".mov", ".mkv"]
    video_dest = home_path.joinpath("Videos", "mp44")

    archive_extensions: list[str] = [".zst", ".xz", ".zip", ".tar", ".bz2", ".7z", ".gz"]
    archive_dest = doc_path.joinpath("compressedarchives")

    for ext, dest in [
        (image_extensions, image_dest),
        (video_extensions, video_dest),
        (archive_extensions, archive_dest),
        ([".pdf", ".docx", ".odt"], doc_path),
        ([".key", ".asc"], doc_path),
        ([".svg", ".xcf"], doc_path.joinpath("svg_xcf")),
        ([".hex"], doc_path.joinpath("ergodoxlayout")),
        ([".stl"], doc_path.joinpath("3dprint")),
        ([".txt", ".log", ".patch"], doc_path.joinpath("text")),
    ]:
        move_files(home_path, ext, dest)


if __name__ == "__main__":
    main()
