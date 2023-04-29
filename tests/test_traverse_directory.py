import pytest

from pathlib import Path
from src.traverse_directory import traverse_directory

def test_no_symlinks(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()
    (d / "file.txt").write_text("content")

    output = traverse_directory(tmp_path, max_symlink_visits=2)
    expected_output = ["dir/", "  dir/file.txt"]
    assert output == expected_output


def test_symlink_limit_one(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()
    (d / "file.txt").write_text("content")

    symlink_dir = tmp_path / "symlink_dir"
    symlink_dir.symlink_to(d)

    output = traverse_directory(tmp_path, max_symlink_visits=1)
    
    expected_output = [
        "symlink_dir -> dir",
        "  dir/file.txt",
        "dir/",
        "  dir/file.txt",
        ]
    
    assert output == expected_output


def test_circular_symlink(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()

    symlink_dir = d / "symlink_dir"
    symlink_dir.symlink_to(d)

    output = traverse_directory(tmp_path, max_symlink_visits=3)
    
    expected_output = [
        "dir/",
        "  dir/symlink_dir -> dir",
        "    dir/symlink_dir -> dir",
        "      dir/symlink_dir -> dir",
        "        dir/symlink_dir -> dir",
        "Maximum visits for symlink (3) reached. Skipping further traversal."
        ]
    
    assert output == expected_output


def test_symlink_to_file(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()

    file = d / "file.txt"
    file.write_text("content")

    symlink_file = tmp_path / "symlink_file.txt"
    symlink_file.symlink_to(file)

    output = traverse_directory(tmp_path, max_symlink_visits=3)
    expected_output = [
        "dir/", 
        "  dir/file.txt", 
        "symlink_file.txt -> dir/file.txt",
        ]
    assert output == expected_output


def test_symlink_to_dir(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()

    file = d / "file.txt"
    file.write_text("content")

    symlink_dir = tmp_path / "symlink_dir"
    symlink_dir.symlink_to(d)

    output = traverse_directory(tmp_path, max_symlink_visits=3)
    
    expected_output = [
        "symlink_dir -> dir",
        "  dir/file.txt",
        "dir/",
        "  dir/file.txt",
        ]
    
    assert output == expected_output


def test_symlink_to_ancestor(tmp_path):

    d = tmp_path / "one/two/three"
    d.mkdir(parents=True)

    symlink_dir = tmp_path / "one/two/three/two"
    symlink_dir.symlink_to(tmp_path / "one/two")


    file = d / "file.txt"
    file.write_text("content")

    output = traverse_directory(tmp_path, max_symlink_visits=3)
    
    expected_output = [
        "one/",
        "  one/two/",
        "    one/two/three/",
        "  dir/file.txt",
        ]
    
    assert output == expected_output

def test_symlink_with_ancestor_complicated(tmp_path):

    # Create directories
    o = tmp_path / "outsidedir/four/five/six"
    o.mkdir(parents=True)

    s = tmp_path / "startdir/one/two/three"
    s.mkdir(parents=True)

    # Create symbolic links
    symlink_dir = tmp_path / "outsidedir/four/five/one"
    symlink_dir.symlink_to(tmp_path / "startdir/one")

    symlink_dir = tmp_path / "startdir/badlink"
    symlink_dir.symlink_to("/")

    symlink_dir = tmp_path / "startdir/outsidedir"
    symlink_dir.symlink_to(tmp_path / "outsidedir")

    # Create text files
    file = tmp_path / "outsidedir/hello.txt"
    file.write_text("hello")

    file = tmp_path / "startdir/hello.txt"
    file.write_text("hello")

    file = tmp_path / "startdir/one/goodbye.txt"
    file.write_text("goodbye")

    output = traverse_directory(tmp_path / "startdir/", max_symlink_visits=3)
    
    expected_output = [
        "outsidedir -> ../outsidedir",
        "  ../outsidedir/four/",
        "    ../outsidedir/four/five/",
        "      ../outsidedir/four/five/six/",
        "      ../outsidedir/four/five/one -> one",
        "        one/two/",
        "          one/two/three/",
        "        one/goodbye.txt",
        "  ../outsidedir/hello.txt",
        "hello.txt",
        "one/",
        "  one/two/",
        "    one/two/three/",
        "  one/goodbye.txt",
        ]

    assert output == expected_output