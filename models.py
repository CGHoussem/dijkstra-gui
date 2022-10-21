"""
This is the Models module
"""

from typing import Tuple
import random

from pygame import draw


def random_position() -> Tuple[int, int]:
    """
    This methods returns a random position (x, y)
    """
    return (random.randint(25, 500-25), random.randint(25, 500-25))


def random_color() -> Tuple[int, int, int]:
    """
    This methods returns a random color (r, g, b).
        rgb values are from 0 to 255
    """
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


class Node:
    """
    Node class
    """
    node_ids = 0

    def __init__(self, text='', pos=(0, 0)):
        self._id = Node.node_ids
        self.pos = pos
        self.radius = 20
        self.color = (255, 0, 0)
        self.text = text
        self.hovered = False
        self.selected = False

        self._neighbors = []

        Node.node_ids += 1

    def render(self, screen, font):
        """
        This is the render method. It renders the Node object in the window.
        """
        (color_r, color_g, color_b) = self.color

        if self.hovered:
            color_r = min(self.color[0]+50, 255)
            color_g = min(self.color[1]+50, 255)
            color_b = min(self.color[2]+50, 255)
        if self.selected:
            color_r = max(self.color[0]-50, 0)
            color_g = max(self.color[1]-50, 0)
            color_b = max(self.color[2]-50, 0)

        # drawing the circle
        draw.circle(screen, (color_r, color_g, color_b), self.pos, self.radius)
        # drawing the outline
        width = 1
        if self.hovered or self.selected:
            width = 2
        draw.circle(screen, (0, 0, 0), self.pos, self.radius, width)

        # drawing the text
        label = font.render(self.text, 1, (0, 0, 0))
        screen.blit(label, (self.pos[0]-6, self.pos[1]-5))

    def add_neighbor(self, node):
        """
        This method adds the node object to a given node's neighbors.
        """
        self._neighbors.append(node)

    @property
    def node_id(self):
        """
        This returns the node id propery.
        """
        return self._id

    @property
    def neighbors(self):
        """
        This property returns the neighbors of the current node.
        """
        return self._neighbors

    @property
    def hex_color(self):
        """
        This property returns the color of the current node in hex format.
        """
        return f'#{self.color[0]:02x}{self.color[1]:02x}{self.color[2]:02x}'

    def __str__(self):
        return f'Node ({self.text})'

    def __repr__(self):
        return str(self)


class Connection:
    """
    Connection class
    """
    HIGHLIGHT_COLOR = (255, 0, 0)
    def __init__(self, nodes=(None, None), weight=0, color=(0, 0, 0)):
        self.nodes = nodes
        self.nodes[0].add_neighbor((self.nodes[1], self))
        self.nodes[1].add_neighbor((self.nodes[0], self))

        self.weight = weight
        self.color = color
        self._highlighted = False

    @property
    def is_highlighted(self):
        """
        This property returns whether the highlighted property is enabled or disabled
        """
        return self._highlighted

    def disable_highlight(self):
        """
        This methods disables the highlight of the connection (line).
        """
        self._highlighted = False

    def enable_highlight(self):
        """
        This method enables the highlight of the connection (line).
        """
        self._highlighted = True

    def render(self, screen, font):
        """
        This method renders the connect object (line) in the window.
        """
        node_1_pos = self.nodes[0].pos
        node_2_pos = self.nodes[1].pos

        # drawing the highlight
        if self._highlighted:
            draw.line(screen, Connection.HIGHLIGHT_COLOR, node_1_pos, node_2_pos, 6)

        # drawing the line
        draw.line(screen, self.color, node_1_pos, node_2_pos, 2)

        # drawing the weight
        label = font.render(str(self.weight), 1, (0, 0, 0))

        # calculating the median position of the two nodes
        pos_x = (node_1_pos[0] + node_2_pos[0]) / 2
        pos_y = (node_1_pos[1] + node_2_pos[1]) / 2

        screen.blit(label, (pos_x, pos_y))

    def __str__(self):
        return f'{self.nodes[0]} -> {self.nodes[1]} = {self.weight}'

    def __repr__(self):
        return str(self)


class Graph:
    """Graph class"""
    def __init__(self, nodes=None, connections=None):
        self.nodes = nodes
        if self.nodes is None:
            self.nodes = []
        self.connections = connections
        if self.connections is None:
            self.connections = []
        self.distances = {}
        self.preds = {}


class Tool:
    """Tool class"""
    def __init__(self, _master=None, _graph=None):
        super().__init__()

    def on_click(self):
        """
        This is the 'on click' callback
        """

    def handle_mouse_down(self, event, double_click=False):
        """
        This is the 'handle mouse down' callback
        """

    def handle_mouse_up(self, event):
        """
        This is the 'handle mouse up' callback
        """

    def handle_mouse_move(self, event):
        """
        This is the 'handle mouse move' callback
        """

    def render_preview(self, screen):
        """
        This method is responsible for rendering a preview of the object \
            before it's placement.
        """
