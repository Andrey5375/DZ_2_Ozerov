# test_dependency_visualizer.py

import unittest
from dependency_visualizer import download_packages_file, parse_packages_data, build_dependency_graph, generate_graphviz_code

class TestDependencyVisualizer(unittest.TestCase):

    def test_download_packages_file(self):
        repo_url = 'http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/'
        packages_data = download_packages_file(repo_url)
        self.assertIsNotNone(packages_data)
        self.assertIn('Package:', packages_data)

    def test_parse_packages_data(self):
        packages_data = """
        Package: bash
        Depends: libc6 (>= 2.15), libtinfo6 (>= 6)

        Package: libc6
        Depends: libgcc1

        Package: libtinfo6
        Depends:
        """
        packages_info = parse_packages_data(packages_data)
        self.assertIn('bash', packages_info)
        self.assertIn('libc6', packages_info['bash'])
        self.assertIn('libtinfo6', packages_info['bash'])

    def test_build_dependency_graph(self):
        packages_info = {
            'bash': ['libc6', 'libtinfo6'],
            'libc6': ['libgcc1'],
            'libtinfo6': []
        }
        graph = build_dependency_graph('bash', packages_info)
        self.assertIn('bash', graph)
        self.assertIn('libc6', graph['bash'])
        self.assertIn('libtinfo6', graph['bash'])
        self.assertIn('libgcc1', graph['libc6'])

    def test_generate_graphviz_code(self):
        graph = {
            'bash': {'libc6', 'libtinfo6'},
            'libc6': {'libgcc1'}
        }
        graphviz_code = generate_graphviz_code(graph)
        self.assertIn('"bash" -> "libc6"', graphviz_code)
        self.assertIn('"bash" -> "libtinfo6"', graphviz_code)
        self.assertIn('"libc6" -> "libgcc1"', graphviz_code)

if __name__ == '__main__':
    unittest.main()
