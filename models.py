from pygame import draw, time
from math import sin, ceil

import random


def random_position() -> (int, int):
    return (random.randint(25, 500-25), random.randint(25, 500-25))


def random_color() -> (int, int, int):
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


class Node:
    node_ids = 0

    def __init__(self, text='', pos=(0, 0)):
        self.id = Node.node_ids
        self.pos = pos
        self.radius = 15
        self.color = (255, 0, 0)
        self.text = text
        self.hovered = False
        self.selected = False

        self._neighbors = []

        Node.node_ids += 1

    def render(self, screen, font):
        (r, g, b) = self.color

        if self.hovered:
            r = self.color[0]+50
            if r > 255:
                r = 255
            g = self.color[1]+50
            if g > 255:
                g = 255
            b = self.color[2]+50
            if b > 255:
                b = 255
        if self.selected:
            r = self.color[0]-50
            if r < 0:
                r = 0
            g = self.color[1]-50
            if g < 0:
                g = 0
            b = self.color[2]-50
            if b < 0:
                b = 0

        # drawing the circle
        draw.circle(screen, (r, g, b), self.pos, self.radius)

        # drawing the text
        label = font.render(self.text, 1, (0, 0, 0))
        screen.blit(label, (self.pos[0]-6, self.pos[1]-5))

    def add_neighbor(self, node):
        self._neighbors.append(node)

    @property
    def neighbors(self):
        return self._neighbors

    @property
    def hex_color(self):
        return '#%02x%02x%02x' % self.color

    def __str__(self):
        return '({})'.format(self.id)

    def __repr__(self):
        return str(self)


class Connection:
    def __init__(self, nodes=(None, None), weight=0, color=(0, 0, 0)):
        self.nodes = nodes
        self.nodes[0].add_neighbor((self.nodes[1], self))
        self.nodes[1].add_neighbor((self.nodes[0], self))

        self.weight = weight
        self.color = color

    def render(self, screen, font):
        node_1_pos = self.nodes[0].pos
        node_2_pos = self.nodes[1].pos

        # drawing the line
        draw.line(screen, self.color, node_1_pos, node_2_pos, 2)

        # drawing the weight
        label = font.render(str(self.weight), 1, (0, 0, 0))

        # calculating the median position of the two nodes
        x = (node_1_pos[0] + node_2_pos[0]) / 2
        y = (node_1_pos[1] + node_2_pos[1]) / 2

        screen.blit(label, (x, y))

    def __str__(self):
        return '({},{})[{}]'.format(self.nodes[0], self.nodes[1], self.weight)

    def __repr__(self):
        return str(self)


class Graph:
    def __init__(self, nodes=[], connections=[]):
        self.nodes = nodes
        self.connections = connections
        self.distances = {}
        self.preds = {}


class Tool:
    def __init__(self, master=None, graph=None):
        super().__init__()

    def on_click(self): pass

    def handleMouseDown(self, event, double_click=False): pass
    def handleMouseUp(self, event): pass
    def handleMouseMove(self, event): pass

    def renderPreview(self, screen): pass
