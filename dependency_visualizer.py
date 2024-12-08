# dependency_visualizer.py



import argparse
import urllib.request
import gzip
import io
from collections import defaultdict
import sys
import configparser

def read_config(config_file):
    """
    Read the configuration file.

    Args:
        config_file (str): Path to the configuration file.

    Returns:
        dict: A dictionary containing the configuration parameters.
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    return {
        'path': config.get('Settings', 'path'),
        'name': config.get('Settings', 'name'),
        'output': config.get('Settings', 'output'),
        'url': config.get('Settings', 'url')
    }

def download_packages_file(repo_url):
    """
    Download and decompress the Packages.gz file from the repository URL.

    Args:
        repo_url (str): The base URL of the repository.

    Returns:
        str: The decompressed content of the Packages file.

    Raises:
        Exception: If there is an error downloading or decompressing the file.
    """
    packages_url = repo_url.rstrip('/') + '/Packages.gz'
    try:
        with urllib.request.urlopen(packages_url) as response:
            compressed_data = response.read()
            with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as f:
                packages_data = f.read().decode('utf-8')
        return packages_data
    except Exception as e:
        raise Exception(f"Error downloading or decompressing Packages.gz: {e}")

def parse_packages_data(packages_data):
    """
    Parse the Packages data and extract package information.

    Args:
        packages_data (str): The content of the Packages file.

    Returns:
        dict: A dictionary mapping package names to their dependencies.
    """
    packages_info = {}
    current_package = {}
    for line in packages_data.split('\n'):
        if line.strip() == '':
            if 'Package' in current_package:
                package_name = current_package['Package']
                depends = current_package.get('Depends', '')
                depends = [dep.strip().split(' ')[0] for dep in depends.split(',')] if depends else []
                packages_info[package_name] = depends
            current_package = {}
        else:
            if ':' in line:
                key, value = line.split(':', 1)
                current_package[key.strip()] = value.strip()
    return packages_info

def build_dependency_graph(package_name, packages_info):
    """
    Build the dependency graph for the given package.

    Args:
        package_name (str): The name of the package to analyze.
        packages_info (dict): A dictionary mapping package names to their dependencies.

    Returns:
        dict: A dictionary representing the dependency graph.

    Raises:
        Exception: If the package is not found in the packages_info.
    """
    if package_name not in packages_info:
        raise Exception(f"Package {package_name} not found in repository.")

    graph = defaultdict(set)
    visited = set()

    def dfs(pkg):
        if pkg in visited:
            return
        visited.add(pkg)
        graph[pkg]  # Ensure the package is added to the graph even if it has no dependencies
        dependencies = packages_info.get(pkg, [])
        for dep in dependencies:
            graph[pkg].add(dep)
            dfs(dep)

    dfs(package_name)
    return graph

def generate_graphviz_code(graph):
    """
    Generate Graphviz code from the dependency graph.

    Args:
        graph (dict): The dependency graph.

    Returns:
        str: The Graphviz code representing the dependency graph.
    """
    lines = ['digraph G {']
    for pkg, deps in graph.items():
        for dep in deps:
            lines.append(f'    "{pkg}" -> "{dep}";')
    lines.append('}')
    return '\n'.join(lines)

def main():
    config = read_config('config.ini')

    try:
        packages_data = download_packages_file(config['url'])
        packages_info = parse_packages_data(packages_data)
        graph = build_dependency_graph(config['name'], packages_info)
        graphviz_code = generate_graphviz_code(graph)
        # Output the code to the screen
        print(graphviz_code)
        # Write the code to the output file
        with open(config['output'], 'w') as f:
            f.write(graphviz_code)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
