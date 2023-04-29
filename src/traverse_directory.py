import os
import sys
from pathlib import Path

def is_ancestor_directory(potential_ancestor, dir):
    """
    Check if the ancestor directory is an ancestor of the descendant directory.

    :param potential_ancestor: The ancestor directory path.
    :param dir: The directory to check path.
    :return: True if the ancestor directory is an ancestor of the descendant directory, False otherwise.
    """

    # should return true if ancestor is located anywhere in the path of descendant
    # e.g. /home/user/ancestor is an ancestor of /home/user/ancestor/descendant

    potential_ancestor = os.path.abspath(os.path.realpath(potential_ancestor))
    dir = os.path.abspath(os.path.realpath(dir))

    return os.path.commonpath([potential_ancestor]) == os.path.commonpath([potential_ancestor, dir])

def traverse_directory(path, max_symlink_visits, visited_symlinks=None, indent="", output=None, starting_path=None):
    """
    Recursively traverse the given directory, including symbolic links.

    :param path: The directory path to traverse.
    :param max_symlink_visits: Maximum number of times a symbolic link can be visited.
    :param visited_symlinks: A dictionary to store the visited symbolic links and their counts.
    :param indent: Indentation for the output.
    :param output: A list of strings representing the file hierarchy.
    :param starting_path: The original starting path to calculate relative paths.
    :return: A list of strings representing the file hierarchy.
    """
    if visited_symlinks is None:
        visited_symlinks = {}

    if output is None:
        output = []

    if starting_path is None:
        starting_path = Path(path).resolve()
    else:
        starting_path = Path(starting_path).resolve()

    try:
        with os.scandir(path) as entries:
            for entry in entries:
                
                if not entry.is_symlink():

                    if entry.is_dir(follow_symlinks=False):
                        output.append(indent + os.path.relpath(entry.path, starting_path) + "/")
                        new_indent = indent + "  "
                        traverse_directory(entry.path, max_symlink_visits, visited_symlinks, new_indent, output, starting_path)
                    elif entry.is_file():
                        output.append(indent + os.path.relpath(entry.path, starting_path))
                else:

                    target = os.readlink(entry.path)
                    target_path = Path(entry.path).parent / target
                    target_path = target_path.resolve()

                    output.append(indent + os.path.relpath(entry.path, starting_path) + " -> " + os.path.relpath(target_path, starting_path))
                                    
                    new_indent = indent + "  "
                    if target_path not in visited_symlinks:
                        visited_symlinks[target_path] = 0

                    if visited_symlinks[target_path] < max_symlink_visits:
                        visited_symlinks[target_path] += 1
                        if target_path.is_dir() and not is_ancestor_directory(target_path, starting_path):
                            traverse_directory(target_path, max_symlink_visits, visited_symlinks, new_indent, output, starting_path)
                    else:
                        output.append(f"Maximum visits for symlink ({max_symlink_visits}) reached. Skipping further traversal.")

    except PermissionError as e:
        output.append(f"Permission denied: {e.filename}")
    except FileNotFoundError as e:
        output.append(f"Path not found: {e.filename}")

    return output

def main():
    """
    Process command-line arguments, call traverse_directory with the provided path and max_symlink_visits,
    and print the output.
    """
    
    if len(sys.argv) < 2:
        print("Usage: python traverse_directory.py <path> [<max_symlink_visits>]")
        sys.exit(1)

    path = sys.argv[1]
    max_symlink_visits = 3

    if len(sys.argv) > 2:
        try:
            max_symlink_visits = int(sys.argv[2])
        except ValueError:
            print("Invalid value for max_symlink_visits. Using the default value of 3.")

    output = traverse_directory(path, max_symlink_visits)
    for line in output:
        print(line)


if __name__ == "__main__":
    main()
