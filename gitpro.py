#!/usr/bin/env python3
import subprocess
import sys

MAIN_BRANCH_NAME = "master"

# ------------------- HELPER FUNCTION ----------------------------------------------

def is_detached_head():
    try:
        # Check if HEAD points to a branch or a commit hash
        branch_name = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD']).strip().decode('utf-8')
        return False, branch_name
    except subprocess.CalledProcessError:
        return True, None


def get_commits():
    # Get the commit log using git log command
    git_log = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True)
    commits = git_log.stdout.strip().split('\n')
    return commits


# ---------------------- MAIN COMMANDS -----------------------------------------------

def gitpro(n):
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


# -------------------- MAIN DRIVER CODE --------------------------------------------

def main():
    # Check if argument is provided
    if len(sys.argv) < 2:
        print("Usage: gitpro <n:int> | reset | list | diff <m:int> <n:int> | search <search-key:str>")
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
    else:
        try:
            n = int(option)
            gitpro(n)
        except ValueError:
            print("Invalid argument. Please provide an integer, 'reset', 'list', or 'diff'.")
            sys.exit(1)

if __name__ == "__main__":
    main()
