"""
This module is contains the different tests to be run by unittest
"""

import math
import random
import unittest
from models import Connection, Node, Graph, random_color, random_position
import controllers

nodes = [
    Node('0'),
    Node('1'),
    Node('2'),
    Node('3'),
    Node('4'),
    Node('5'),
    Node('6'),
    Node('7'),
    Node('8')
]

connections = [
    Connection((nodes[0], nodes[1]), 4),
    Connection((nodes[0], nodes[7]), 8),
    Connection((nodes[1], nodes[7]), 11),
    Connection((nodes[1], nodes[2]), 8),
    Connection((nodes[7], nodes[8]), 7),
    Connection((nodes[7], nodes[6]), 1),
    Connection((nodes[2], nodes[8]), 2),
    Connection((nodes[8], nodes[6]), 6),
    Connection((nodes[2], nodes[3]), 7),
    Connection((nodes[2], nodes[5]), 4),
    Connection((nodes[6], nodes[5]), 2),
    Connection((nodes[3], nodes[5]), 14),
    Connection((nodes[3], nodes[4]), 9),
    Connection((nodes[5], nodes[4]), 10)
]

graph = Graph(nodes, connections)


class TestControllersMethods(unittest.TestCase):
    """
    This class is responsible for testing the different 'controllers.py' methods
    """
    def test_init(self):
        """
        This test function tests the 'init()' method
        """
        controllers.init(graph, graph.nodes[0])
        self.assertEqual(graph.distances[graph.nodes[0]], 0)
        self.assertEqual(graph.distances[graph.nodes[random.randint(1, len(nodes)-1)]], math.inf)

    def test_search_min(self):
        """
        This test function tests the 'search_min(g, q)' method
        """
        queue = graph.nodes.copy()
        min_d_node = controllers.search_min(graph, queue)
        self.assertEqual(min_d_node, graph.nodes[0])

    def test_find_min_distance(self):
        """
        This test function tests the 'find_min_distance(g, n1, n2)' method
        """
        min_d = controllers.find_min_distance(graph, nodes[0], nodes[1])
        self.assertEqual(min_d, 4)
        min_d = controllers.find_min_distance(graph, nodes[0], nodes[4])
        self.assertEqual(min_d, 21)
        min_d = controllers.find_min_distance(graph, nodes[0], nodes[7])
        self.assertEqual(min_d, 8)
        min_d = controllers.find_min_distance(graph, nodes[0], nodes[8])
        self.assertEqual(min_d, 14)

    def test_get_weight(self):
        """
        This test function tests the 'get_weight(g, n1, n2)' method
        """
        weight = controllers.get_weight(graph, graph.nodes[0], graph.nodes[7])
        self.assertEqual(weight, 8)
        weight = controllers.get_weight(graph, graph.nodes[7], graph.nodes[6])
        self.assertEqual(weight, 1)
        weight = controllers.get_weight(graph, graph.nodes[0], graph.nodes[5])
        self.assertEqual(weight, -1)
        weight = controllers.get_weight(graph, graph.nodes[3], graph.nodes[7])
        self.assertEqual(weight, -1)

    def test_find_path(self):
        """
        This test function tests the 'find_path(graph, n1, n2)' method
        """
        controllers.dijkstra(graph, graph.nodes[0])
        cnnx = controllers.find_path(graph, graph.nodes[0], graph.nodes[2])
        self.assertIn(graph.nodes[2], cnnx[0].nodes)
        self.assertIn(graph.nodes[1], cnnx[0].nodes)
        self.assertIn(graph.nodes[0], cnnx[1].nodes)
        self.assertIn(graph.nodes[1], cnnx[1].nodes)

class TestModelsMethods(unittest.TestCase):
    """
    This class is responsible for testing the different 'models.py' methods
    """
    def test_random_position(self):
        """
        This test function tests the 'random_position()' method
        """
        pos_range = list(range(25, 476))
        for _ in range(100):
            pos_x, pos_y = random_position()
            self.assertIn(pos_x, pos_range)
            self.assertIn(pos_y, pos_range)

    def test_random_color(self):
        """
        This test function tests the 'random_color()' method
        """
        color_range = list(range(0, 256))
        for _ in range(100):
            color_r, color_g, color_b = random_color()
            self.assertIn(color_r, color_range)
            self.assertIn(color_g, color_range)
            self.assertIn(color_b, color_range)

if __name__ == '__main__':
    unittest.main()
