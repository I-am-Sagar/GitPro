#!/usr/bin/env python3
import subprocess
import sys

def is_detached_head():
    try:
        # Check if HEAD points to a branch or a commit hash
        branch_name = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD']).strip().decode('utf-8')
        return False, branch_name
    except subprocess.CalledProcessError:
        return True, None

def gitpro(n):
    try:
        # Check if currently in a detached HEAD state
        detached, branch_name = is_detached_head()

        if detached:
            print("Currently in detached HEAD state.")
            print("Checking out to master branch first...")
            subprocess.run(['git', 'checkout', 'master'])
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
        # Checkout to the master branch
        subprocess.run(['git', 'checkout', 'master'])
    except subprocess.CalledProcessError:
        print("Failed to checkout to master branch.")
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

        # Show differences between the mth and nth commits
        subprocess.run(['git', 'diff', m_commit_hash, n_commit_hash])
    except IndexError:
        print("Commit not found.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Failed to show differences between commits.")
        sys.exit(1)


def main():
    # Check if argument is provided
    if len(sys.argv) < 2:
        print("Usage: gitpro <n:int> | reset | list | diff [<m:int> [<n:int>]]")
        sys.exit(1)
    
    option = sys.argv[1]

    if option == 'reset':
        gitpro_reset()
    elif option == 'list':
        list_commits()
    elif option == 'diff':
        if len(sys.argv) == 2:
            git_diff(1, 2)  # Default to differences between the current commit and the next commit
        elif len(sys.argv) == 4:
            try:
                m = int(sys.argv[2])
                n = int(sys.argv[3])
                git_diff(m, n)
            except ValueError:
                print("Invalid arguments. Please provide integers for m and n.")
                sys.exit(1)
        else:
            print("Invalid number of arguments. Usage: gitpro diff [<m:int> [<n:int>]]")
            sys.exit(1)
    else:
        try:
            n = int(option)
            gitpro(n)
        except ValueError:
            print("Invalid argument. Please provide an integer, 'reset', 'list', or 'diff'.")
            sys.exit(1)

if __name__ == "__main__":
    main()
