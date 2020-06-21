from tkinter import Tk, X, StringVar, HORIZONTAL, N, S, PhotoImage
from tkinter.ttk import Frame, Label, Entry, Button, Separator

from models import *


def mouse_on_a_node(pos, nodes) -> Node:
    for node in nodes:
        if pos[0] >= node.pos[0]-node.radius and pos[0] <= node.pos[0]+node.radius and \
                pos[1] >= node.pos[1]-node.radius and pos[1] <= node.pos[1]+node.radius:
            return node
    return None


class ToolBar(Frame):
    def __init__(self, master=None, graph=None):
        super().__init__(master=master)
        self.tool = Tool()
        self.graph = graph

        self.tools = []

        self._initTools()
        self.initUI()

    def _initTools(self):
        self.tools.append(MoveTool(self, self.graph))
        self.tools.append(AddNodeTool(self, self.graph))
        self.tools.append(ConnectionTool(self, self.graph))
        self.tools.append(DeleteTool(self, self.graph))

    def initUI(self):
        for i, tool in enumerate(self.tools):
            tool.button.grid(row=0, column=i)


class MoveTool(Tool):
    def __init__(self, master=None, graph=None):
        super().__init__(master, graph)
        self.master = master
        self.graph = graph

        self.image = PhotoImage(file=r"images/move.png")
        self.image = self.image.subsample(3, 3)

        self.button = Button(self.master, text="Move Node",
                             image=self.image, command=self.on_click)

        self._selected_node = None

    def on_click(self):
        self.master.tool = self

    def handleMouseDown(self, event, double_click=False):
        self._selected_node = mouse_on_a_node(event.pos, self.graph.nodes)

        if double_click and self._selected_node:
            pass

    def handleMouseUp(self, event):
        self._selected_node = None

    def handleMouseMove(self, event):
        if self._selected_node != None:
            self._selected_node.pos = event.pos


class AddNodeTool(Tool):
    def __init__(self, master=None, graph=None):
        super().__init__(master, graph)
        self.master = master
        self.graph = graph

        self.image = PhotoImage(file=r"images/add_node.png")
        self.image = self.image.subsample(3, 3)

        self.button = Button(self.master, text="Add Node",
                             image=self.image, command=self.on_click)

    def on_click(self):
        self.master.tool = self

    def handleMouseDown(self, event, double_click=False):
        if event.button == 1:
            if mouse_on_a_node(event.pos, self.graph.nodes) == None:
                node = Node(text='?', pos=event.pos)
                self.graph.nodes.append(node)


class ConnectionTool(Tool):
    def __init__(self, master=None, graph=Graph):
        super().__init__(master, graph)
        self.master = master
        self.graph = graph

        self.image = PhotoImage(file=r"images/connection.png")
        self.image = self.image.subsample(3, 3)

        self.button = Button(self.master, text="Connection",
                             image=self.image, command=self.on_click)

        self._start_node = None
        self._end_node = None

    def on_click(self):
        self.master.tool = self

    def handleMouseDown(self, event, double_click=False):
        if event.button == 1:
            self._start_node = mouse_on_a_node(event.pos, self.graph.nodes)

    def handleMouseUp(self, event):
        if event.button == 1 and self._start_node:
            node = mouse_on_a_node(event.pos, self.graph.nodes)
            if node != None:
                self._end_node = node

                # connecting the two nodes
                self.graph.connections.append(
                    Connection((self._start_node, self._end_node)))

        self._start_node = None

    def handleMouseMove(self, event):
        self._end_pos = event.pos

    def renderPreview(self, screen):
        if self._start_node != None:
            color = (150, 150, 150)
            draw.line(screen, color, self._start_node.pos, self._end_pos)


class DeleteTool(Tool):
    def __init__(self, master=None, graph=None):
        super().__init__(master, graph)
        self.master = master
        self.graph = graph

        self.image = PhotoImage(file=r"images/delete.png")
        self.image = self.image.subsample(3, 3)

        self.button = Button(master, text="Delete",
                             image=self.image, command=self.on_click)

    def on_click(self):
        self.master.tool = self

    def handleMouseDown(self, event, double_click=False):
        node = mouse_on_a_node(event.pos, self.graph.nodes)
        if node:
            # Delete the connections of that node
            connections_to_delete = []
            for connection in self.graph.connections:
                if node in connection.nodes:
                    connections_to_delete.append(connection)
            for connection in connections_to_delete:
                self.graph.connections.remove(connection)

            # Delete the node
            self.graph.nodes.remove(node)
