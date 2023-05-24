# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonFlaskFrontend                 
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import os


def convert_static_references(template_folder: str) -> None:
    """
    Function for converting static references in .html files.
    Scripts, images and stylesheets get converted to "{{ url_for('static', filename='my_file_path') }}" syntax.
    :param template_folder: Template folder path containing .html files.
    """
    # collect file paths
    files = []
    if os.path.exists(template_folder):
        for root, _, curr_files in os.walk(template_folder, topdown=True):
            files.extend([os.path.join(root, f) for f in curr_files if f.lower().endswith(".html")])

    for file_path in files:
        content = open(file_path, "r", encoding="utf8").read()
        content = content.split("\n")
        for index, line in enumerate(content):
            if "<script" in line and "src=\"" in line and "src=\"http" not in line and "url_for('static'" not in line:
                reference_path = line.split("src=\"")[1].split("\"")[0]
                content[index] = line.replace(reference_path, "{{ url_for('static', filename='"+reference_path+"') }}")
            elif "<link rel=" in line and "href=\"" in line and "href=\"http" not in line and "url_for('static'" not in line:
                reference_path = line.split("href=\"")[1].split("\"")[0]
                content[index] = line.replace(reference_path, "{{ url_for('static', filename='"+reference_path+"') }}")
            elif "<img" in line and "src=\"" in line and "src=\"http" not in line and "url_for('static'" not in line:
                reference_path = line.split("src=\"")[1].split("\"")[0]
                content[index] = line.replace(reference_path, "{{ url_for('static', filename='"+reference_path+"') }}")
        open(file_path, "w", encoding="utf8").write("\n".join(content))


def get_common_lines(template_folder: str) -> dict:
    """
    Function for extracting common lines in .html files.
    :param template_folder: Template folder path containing .html files.
    :return: Common lines/code blocks as dictionary
    """
    file_paths = []
    files = {}
    common_lines = {}
    if os.path.exists(template_folder):
        for root, _, curr_files in os.walk(template_folder, topdown=True):
            file_paths.extend([os.path.join(root, f) for f in curr_files if f.lower().endswith(".html")])

    for file_path in file_paths:
        files[file_path] = set(open(file_path, "r", encoding="utf8").read().split("\n"))

    for source_index, file_path in enumerate(file_paths):
        for target_index, other_file_path in enumerate(file_paths):
            if source_index != target_index:
                comparison_key = "-".join([str(elem) for elem in sorted([source_index, target_index])])
                intersection = files[file_path].intersection(files[other_file_path])
                # TODO: Finish up aggregation
