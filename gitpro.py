#!/usr/bin/env python3
import subprocess
import sys
import os
import fnmatch

MAIN_BRANCH_NAME = "main"

# ------------------- HELPER FUNCTIONS ----------------------------------------------

def is_detached_head():
    """
    Checks if the repository is in detached HEAD state.

    Returns:
        (bool): True if in detached HEAD state, False otherwise.
        (str or None): Name of the branch if not detached, None if detached.
    """
    try:
        # Check if HEAD points to a branch or a commit hash
        branch_name = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD']).strip().decode('utf-8')
        return False, branch_name
    except subprocess.CalledProcessError:
        return True, None


def get_commits():
    """
    Retrieves the commit log.

    Returns:
        (list): List of commits in short format.
    """
    # Get the commit log using git log command
    git_log = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True)
    commits = git_log.stdout.strip().split('\n')
    return commits


def read_exclude_patterns_from_gitignore():
    """
    Reads exclude patterns from .gitignore file.

    Returns:
        (list): List of patterns to be excluded.
    """
    exclude_patterns = []
    gitignore_path = os.path.join(os.getcwd(), ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Strip '/' from the start and end of the pattern
                    line = line.strip('/')
                    exclude_patterns.append(line)

    # Add .git folder to exclude patterns as well
    exclude_patterns.append(".git")
    
    return exclude_patterns


def print_lines_by_file(lines_by_file):
    """
    Prints lines of code in each file in a hierarchical tree folder structure.

    Args:
        lines_by_file (dict): Dictionary containing file paths and their respective lines of code.
    """
    for file_path, lines in lines_by_file.items():
        # Split the file path into individual directories and filename
        directories, filename = os.path.split(file_path)
        # Construct indentation string with blue color for directories
        indent_string = '\033[94m' + os.path.join(*directories.split(os.sep)) + os.sep + '\033[0m'
        # Calculate indentation based on the number of directories
        indentation = len(directories.split(os.sep))
        # Adjust indentation for the filename
        indent_string += "  " * (indentation - 1)
        # Print the file path and number of lines with appropriate indentation
        print(f"{indent_string}└── {filename} ({lines} lines)")

    # Print total lines of code
    total_lines = sum(lines_by_file.values())
    print(f"\nTotal lines of code: {total_lines}")


# ---------------------- MAIN COMMANDS -----------------------------------------------

def gitpro(n):
    """
    Checks out to the nth commit from the initial commit.

    Args:
        n (int): Number indicating the nth commit.
    """
    try:
        # Check if currently in a detached HEAD state
        detached, branch_name = is_detached_head()

        if detached:
            print("Currently in detached HEAD state.")
            print("Checking out to master branch first...")
            subprocess.run(['git', 'checkout', MAIN_BRANCH_NAME])
        else:
            print(f"Currently on branch: {branch_name}")

        # Get the nth commit hash
        commit_hash = subprocess.check_output(['git', 'log', '--pretty=format:%H']).splitlines()[-n].decode('utf-8')
        
        # Checkout to the nth commit
        subprocess.run(['git', 'checkout', commit_hash])
    except IndexError:
        print("Commit not found.")
        sys.exit(1)


def gitpro_reset():
    """
    Resets the repository to the main branch and discards local changes.
    """
    try:
        # Check if there are any local changes
        status_output = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if status_output.stdout.strip():
            # There are local changes, discard them
            subprocess.run(['git', 'reset', '--hard'])
        
        # Checkout to the main branch
        subprocess.run(['git', 'checkout', MAIN_BRANCH_NAME])
    except subprocess.CalledProcessError:
        print("Failed to checkout to main branch.")
        sys.exit(1)


def list_commits():
    """
    Lists all commits in the repository.
    """
    try:
        # Get commit hashes and messages
        commit_info = subprocess.check_output(['git', 'log', '--pretty=format:%H %s']).decode('utf-8')
        commit_list = commit_info.splitlines()
        for i, commit in enumerate(commit_list, 1):
            print(f"{i}. {commit}")
    except subprocess.CalledProcessError:
        print("Failed to retrieve commit information.")
        sys.exit(1)


def git_diff(m, n):
    """
    Shows differences between two commits.

    Args:
        m (int): Number indicating the mth commit from the initial commit.
        n (int): Number indicating the nth commit from the initial commit.
    """
    try:
        # Get the mth and nth commit hashes from the start
        m_commit_hash = subprocess.check_output(['git', 'log', '--pretty=format:%H']).splitlines()[-m].decode('utf-8')
        n_commit_hash = subprocess.check_output(['git', 'log', '--pretty=format:%H']).splitlines()[-n].decode('utf-8')

        # Highlight the differences between the folder structures
        print("\nChanges in folder structure:")
        subprocess.run(['git', 'diff', '--name-only', m_commit_hash, n_commit_hash], stdout=sys.stdout)

        # Show differences between the mth and nth commits
        print(f"\nDifferences between the #{m} and #{n} commits:")
        subprocess.run(['git', 'diff', m_commit_hash, n_commit_hash], stdout=sys.stdout)

    except IndexError:
        print("Commit not found.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Failed to show differences between commits.")
        sys.exit(1)


def search_commit_message(search_key):
    """
    Searches for a specific string in commit messages.

    Args:
        search_key (str): String to search for in commit messages.
    """
    # If in detached head-state, checkout to master first
    detached, branch_name = is_detached_head()

    if detached:
        print("Currently in detached HEAD state.")
        print("Checking out to master branch first...")
        subprocess.run(['git', 'checkout', MAIN_BRANCH_NAME])
    else:
        print(f"Currently on branch: {branch_name}")    

    commits = get_commits()
    for i, commit in enumerate(commits):
        commit_parts = commit.split(' ', 1)
        commit_hash = commit_parts[0]
        commit_message = commit_parts[1]
        if search_key.lower() in commit_message.lower():
            print(f"{i+1} {commit_hash} \"{commit_message}\"")


def count_lines_of_code(directory, exclude_patterns):
    """
    Counts lines of code in each file within the repository directory.

    Args:
        directory (str): Path to the repository directory.
        exclude_patterns (list): List of patterns to exclude while counting lines of code.

    Returns:
        (dict): Dictionary containing file paths and their respective lines of code.
    """
    lines_by_file = {}
    for root, dirs, files in os.walk(directory):
        # Exclude directories matching the patterns in exclude_patterns
        dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_patterns)]

        for file in files:
            file_path = os.path.join(root, file)
            # Exclude files matching the patterns in exclude_patterns
            if not any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines_by_file[file_path] = sum(1 for line in f if line.strip())
    return lines_by_file

# -------------------- MAIN DRIVER CODE --------------------------------------------

def main():
    # Check if argument is provided
    if len(sys.argv) < 2:
        print("Usage: gitpro <n:int> | reset | list | diff <m:int> <n:int> | search <search-key:str> | count")
        sys.exit(1)
    
    option = sys.argv[1]

    if option == 'reset':
        gitpro_reset()
    elif option == 'list':
        list_commits()
    elif option == 'diff':
        try:
            m = int(sys.argv[2])
            n = int(sys.argv[3])
            git_diff(m, n)
        except ValueError:
            print("Invalid number of arguments. Usage: gitpro diff <m:int> <n:int>")
            sys.exit(1)
    elif option == 'search':
        if len(sys.argv) != 3:
            print("Usage: ./gitpro.py search 'search_key'")
            sys.exit(1)
        search_key = sys.argv[2]
        search_commit_message(search_key)
    elif option == 'count':
        repository_directory = "."
        exclude_patterns = read_exclude_patterns_from_gitignore()
        lines_by_file = count_lines_of_code(repository_directory, exclude_patterns)
        print_lines_by_file(lines_by_file)
    else:
        try:
            n = int(option)
            gitpro(n)
        except ValueError:
            print("Invalid argument. Please provide an integer, 'reset', 'list', or 'diff'.")
            sys.exit(1)

if __name__ == "__main__":
    main()
