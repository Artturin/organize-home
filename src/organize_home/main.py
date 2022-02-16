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


def move_files_magic(home_path: Path, mime: list[str], dest: Path) -> None:
    """move files using magic"""
    for child in home_path.iterdir():
        if not child.name.startswith(".") and child.is_file() and child.read_text:
            file_mime = magic.from_file(child, mime=True)
            if file_mime in mime:
                move_with_shutil(child, dest)


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

    ext_dict: dict[Path, list[str]] = {
        doc_path.joinpath("bookmarkpics"): [".jpg", ".jpeg", ".png", ".gif"],
        home_path.joinpath("Videos", "mp44"): [".mp4", ".webm", ".mov", ".mkv"],
        doc_path.joinpath("compressedarchives"): [".zst", ".xz", ".zip", ".tar", ".bz2", ".7z", ".gz"],
        doc_path.joinpath("ergodoxlayout"): [".hex"],
        doc_path.joinpath("3dprint"): [".stl"],
        doc_path.joinpath("text"): [".txt", ".log", ".patch"],
        doc_path: [".pdf", ".docx", ".odt", ".key", ".asc"],
    }

    mime_dict: dict[Path, list[str]] = {
        doc_path.joinpath("text"): ["text/plain"],
        doc_path.joinpath("epub"): ["application/epub+zip"],
        doc_path: ["application/json", "application/vnd.oasis.opendocument.graphics"],
    }

    for dest, ext in ext_dict.items():
        move_files_extension(home_path, ext, dest)

    for dest, mime in mime_dict.items():
        move_files_magic(home_path, mime, dest)


if __name__ == "__main__":
    main()
