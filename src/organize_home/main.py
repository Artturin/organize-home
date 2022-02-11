"""
organize my home
"""
import subprocess
from pathlib import Path


def main() -> None:
    """main"""
    home_path = Path.home()
    dest_dir = home_path.joinpath("gits/NotMyGits1").resolve()
    dest_dir.mkdir(exist_ok=True)
    for child in home_path.iterdir():
        g_dir = child.joinpath(".git").resolve()
        if g_dir.is_dir():
            if g_conf := g_dir.joinpath("config"):
                if "Artturin/".lower() not in g_conf.read_text().lower() and child.name.lower() not in [
                    "organize-home",
                    "nixos-gen-config",
                ]:
                    try:
                        # shutil.copytree was much slower and did not copy symlinks properly
                        subprocess.run(["cp", "-R", str(child), str(dest_dir.joinpath(child.name))], check=True)
                    except subprocess.CalledProcessError as err:
                        print(f"{child} {err}\n")


if __name__ == "__main__":
    main()
