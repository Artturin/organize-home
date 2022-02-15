"""
organize my home
"""
import shutil
import subprocess
from pathlib import Path

import magic


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


def move_files_extension(home_path: Path, extensions: list[str], destination_dir: Path) -> None:
    """move files using extension"""
    for child in home_path.iterdir():
        if child.is_file() and [s for s in child.suffixes if any(xs in s for xs in extensions)]:
            move_with_shutil(child, destination_dir)


def move_files_magic(home_path: Path, doc_path: Path) -> None:
    """move files using magic"""
    for child in home_path.iterdir():
        if not child.name.startswith(".") and child.is_file() and child.read_text:
            mime = magic.from_file(child, mime=True)
            destination_dir: Path
            match mime:
                case "text/plain":
                    destination_dir = doc_path.joinpath("text")
                case "application/json":
                    destination_dir = doc_path
                case "application/vnd.oasis.opendocument.graphics":
                    destination_dir = doc_path
                case "application/epub+zip":
                    destination_dir = doc_path.joinpath("epub")
                case _:
                    continue
            move_with_shutil(child, destination_dir)


def move_with_shutil(file_to_move: Path, destination_dir: Path) -> None:
    """move a file with shutil"""
    destination_dir.mkdir(exist_ok=True)
    path_after_moving = ""
    try:
        path_after_moving = shutil.move(file_to_move, destination_dir)
    except shutil.Error as err:
        print(err)
        return
    print(f"{file_to_move} -> {path_after_moving}")


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
        move_files_extension(home_path, ext, dest)

    move_files_magic(home_path, doc_path)


if __name__ == "__main__":
    main()
