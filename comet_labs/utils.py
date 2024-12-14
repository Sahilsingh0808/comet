import subprocess


def get_unstaged_changes():
    try:
        diff_output = subprocess.check_output(["git", "ls-files", "--others", "--modified", "--exclude-standard"], text=True)
        return diff_output.strip().split("\n") if diff_output.strip() else []
    except subprocess.CalledProcessError:
        return []


def get_staged_diff():
    try:
        return subprocess.check_output(["git", "diff", "--staged"], text=True)
    except subprocess.CalledProcessError:
        return None


def add_files_to_stage(files):
    if not files:
        return
    print("\nSelect files to stage (or press Enter to stage all):")
    for i, file in enumerate(files, 1):
        print(f"[{i}] {file}")
    choice = input("Enter file numbers separated by spaces: ").strip()
    if not choice:
        subprocess.run(["git", "add", "."], check=True)
    else:
        indices = [int(i) for i in choice.split() if i.isdigit()]
        for i in indices:
            subprocess.run(["git", "add", files[i - 1]], check=True)
