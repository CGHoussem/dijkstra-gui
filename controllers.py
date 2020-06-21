
from models import Node, Graph


def init(G: Graph, start_node: Node):
    for node in G.nodes:
        G.distances[node] = 999
    G.distances[start_node] = 0


def search_min(G: Graph, Q: list) -> Node:
    mini = 999
    node_m = None
    for node in Q:
        if G.distances[node] < mini:
            mini = G.distances[node]
            node_m = node
    return node_m


def get_weight(G: Graph, node1: Node, node2: Node) -> int:
    """
    This function returns the weight between two nodes
        :param G: graph
        :param node1: start node
        :param node2: destination node
        :type G: Graph
        :type node1: Node
        :type node2: Node
        :return: the weight between node1 and node2
        :rtype: int
    """
    w = -1
    for connection in G.connections:
        if (connection.nodes[0] == node1 and connection.nodes[1] == node2) or \
                (connection.nodes[0] == node2 and connection.nodes[1] == node1):
            w = connection.weight
    return w


def update_distances(G: Graph, node1: Node, node2: Node):
    """
    This function updates the distances between two nodes
        :param G: graph
        :param node1: start node
        :param node2: destination node
        :type G: Graph
        :type node1: Node
        :type node2: Node
    """
    p = get_weight(G, node1, node2)
    if G.distances[node2] > G.distances[node1] + p:
        G.distances[node2] = G.distances[node1] + p
        G.preds[node2] = node1


def get_neighboors(G, node) -> list():
    """
    This function returns a list of nodes that are neighbors of a certain node
        :param G: graph
        :param node: the node to search its neighbors
        :type G: Graph
        :type node1: Node
        :return: list of neighbor nodes
        :rtype: list()
    """
    nodes = []
    for connection in G.connections:
        if connection.nodes[0] == node:
            nodes.append(connection.nodes[1])
        elif connection.nodes[1] == node:
            nodes.append(connection.nodes[0])
    return nodes


def dijkstra(G: Graph, start_node: Node):
    init(G, start_node)
    Q = G.nodes.copy()
    
    while len(Q) != 0:
        node1 = search_min(G, Q)
        Q.remove(node1)
        for node2 in get_neighboors(G, node1):
            update_distances(G, node1, node2)
