import re

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def update_readme(directory_tree, readme_contents):
    # Define the start and end markers
    start_marker = "<!-- DIRECTORY_TREE_START -->"
    end_marker = "<!-- DIRECTORY_TREE_END -->"
    
    # Define the pattern to find the existing directory tree section
    pattern = re.compile(re.escape(start_marker) + ".*?" + re.escape(end_marker), re.DOTALL)
    
    # Define the replacement content, including the markers
    replacement = f"{start_marker}\n```\n{directory_tree}\n```\n{end_marker}"
    
    # Perform the replacement
    updated_contents = re.sub(pattern, replacement, readme_contents)
    
    return updated_contents

directory_tree = read_file('DIRECTORY_TREE.txt')
readme_contents = read_file('README.md')
updated_readme = update_readme(directory_tree, readme_contents)
write_file('README.md', updated_readme)
