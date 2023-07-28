import argparse
import os
import sys


def _line_sort_key(line: str):
    """
    Key to sort non-empty strings in ascending order:
    - words which start with different-case letter are nearby (as opposed to default sorting)
    - capitalized strings are before lowercase
    - shorter strings are before longer ones

    E.g.: ["bb", "a", "A", "B", "b", "Bb"] will be sorted to: ['A', 'a', 'B', 'Bb', 'b', 'bb']
    :param line:
    :return:
    """
    return line[0].lower(), not line[0].isupper(), len(line)


def _append_newline(line: str):
    if not line.endswith("\n"):
        line += "\n"

    return line


def _is_not_empty_line(line: str):
    return line and not line.isspace()


def _sort_requirements():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    [_sort_file(one) for one in args.files]


def _sort_file(file):
    path = os.path.abspath(file)
    with open(path, "r") as f:
        lines = f.readlines()

    sys.stdout.write(f"Sorting {file}...\n")

    processed_lines = filter(_is_not_empty_line, lines)
    formatted_lines = map(_append_newline, processed_lines)
    ordered_lines = list(sorted(formatted_lines, key=_line_sort_key))

    if ordered_lines == lines:
        sys.stdout.write(f"Skipped\n")
        return

    with open(path, "w") as f:
        f.writelines(ordered_lines)

    sys.stdout.write(f"Sorted {len(ordered_lines)} lines\n")


if __name__ == "__main__":
    _sort_requirements()
