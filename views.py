import copy
from math import floor
from tkinter import (HORIZONTAL, Canvas, PhotoImage, IntVar, StringVar, Tk,
                     Toplevel, colorchooser, messagebox)
from tkinter.ttk import (Button, Entry, Frame, Label, Separator, Radiobutton)

from models import Node, Tool, Graph, Connection, draw

from controllers import dijkstra


def mouse_on_a_node(pos, nodes) -> Node:
    for node in nodes:
        if pos[0] >= node.pos[0]-node.radius and pos[0] <= node.pos[0]+node.radius and \
                pos[1] >= node.pos[1]-node.radius and pos[1] <= node.pos[1]+node.radius:
            return node
    return None


class ToolBar(Tk):
    def __init__(self, graph=None):
        super().__init__()
        self.title('Toolbar')
        self.tool = Tool()
        self.graph = graph

        self.tools = []

        self._initTools()
        self._initUI()
        self.update()

    def _initTools(self):
        self.tools.append(MoveTool(self, self.graph))
        self.tools.append(AddNodeTool(self, self.graph))
        self.tools.append(ConnectionTool(self, self.graph))
        self.tools.append(DeleteTool(self, self.graph))

    def _initUI(self):
        for i, tool in enumerate(self.tools):
            tool.button.grid(row=0, column=i)
        Button(self, text='Find Shortest Path', command=self._open_shorest_path_win).grid(
            row=0, column=len(self.tools), sticky='nsew')

    def _open_shorest_path_win(self):
        DijkstraFrame(self.master, self.graph)


class DijkstraFrame(Toplevel):
    def __init__(self, master=None, graph=None):
        super().__init__(master=master)
        self.graph = graph
        self.title('Dijkstra - Find the shortest path')

        self._f_node_var = IntVar()
        self._l_node_var = IntVar()
        self._initUI()

    def _initUI(self):
        length = len(self.graph.nodes)
        Label(self, text='Find the shortest path').grid(
            row=0, column=0, columnspan=2, sticky='w')

        Separator(self, orient=HORIZONTAL).grid(
            row=1, column=0, columnspan=2, sticky='nsew')

        Label(self, text='Start node').grid(row=2, column=0, sticky='w')
        for i, node in enumerate(self.graph.nodes):
            Radiobutton(self, text=str(node), variable=self._f_node_var,
                        value=node.id).grid(row=3+i, column=1, sticky='w')

        Label(self, text='End node').grid(row=3+length, column=0, sticky='w')
        for i, node in enumerate(self.graph.nodes):
            Radiobutton(self, text=str(node), variable=self._l_node_var,
                        value=node.id).grid(row=4+length+i, column=1, sticky='w')

        Separator(self, orient=HORIZONTAL).grid(
            row=length*2+4, column=0, columnspan=2, sticky='nsew')

        Button(self, text='Cancel', command=self.destroy).grid(
            row=length*2+5, column=0)
        Button(self, text='Calculate', command=self._calculate).grid(
            row=length*2+5, column=1)

    def destroy(self):
        return super().destroy()

    def _calculate(self):
        f_node_id = int(self._f_node_var.get())
        l_node_id = int(self._l_node_var.get())

        if f_node_id == l_node_id:
            messagebox.showerror(
                'Error calculating path', 'You should select different nodes for calculations')
        else:
            f_node = l_node = None
            for node in self.graph.nodes:
                if node.id == f_node_id:
                    f_node = node
                elif node.id == l_node_id:
                    l_node = node
                if f_node and l_node:
                    break
            dijkstra(self.graph, f_node)
            print(f'Minimum distance to the other nodes from {f_node}:\n {self.graph.distances}')
            print(f'preds:\n {self.graph.preds}')


class NodeConfigurationFrame(Toplevel):
    def __init__(self, master: Frame = None, graph: Graph = None, node: Node = None):
        super().__init__(master=master)

        self.graph = graph
        self.node = node
        self._temp_node = copy.copy(self.node)
        self._text_var = StringVar(value=self.node.text)

        self._color_picker = colorchooser.Chooser(self)
        self._color = (self.node.color, self.node.hex_color)
        self._change_text_preview = self.register(self._preview)
        self._initUI()

    def _preview(self):
        self._temp_node.text = self._text_var.get()
        self._draw_node(self._temp_node)

    def _initUI(self):
        Label(self, text='Node #{}'.format(self.node.id)).grid(
            row=0, column=0, columnspan=2, sticky='w')
        Separator(self, orient=HORIZONTAL).grid(
            row=1, column=0, columnspan=2, sticky='nsew')
        Label(self, text='Text').grid(row=2, column=0, sticky='w')
        Entry(self, width=5, textvariable=self._text_var, validate='focusout', validatecommand=(
            self._change_text_preview)).grid(row=2, column=1, sticky='w')
        Label(self, text='Color').grid(row=3, column=0, sticky='w')
        Button(self, text='Pick a color', command=self._get_color).grid(
            row=3, column=1, sticky='w')

        Label(self, text='Connections:').grid(
            row=4, column=0, columnspan=2, sticky='w')

        for i, (neighbor_node, connection) in enumerate(self.node.neighbors):
            NodeConnectionConfigRow(
                self, neighbor_node, connection).grid(row=5+i, column=0)

        Separator(self, orient=HORIZONTAL).grid(
            row=5+len(self.node.neighbors), column=0, columnspan=2, sticky='nsew')
        self.canvas = Canvas(self, width=250, height=100)
        self._draw_node(self._temp_node)
        self.canvas.grid(row=6+len(self.node.neighbors),
                         column=0, columnspan=2, sticky='nsew')
        Button(self, text='Cancel', command=self.destroy).grid(
            row=7+len(self.node.neighbors), column=0)
        Button(self, text='Save', command=self._save_node).grid(
            row=7+len(self.node.neighbors), column=1)

    def _get_color(self):
        # ((r, g, b), '#hex')
        self._color = self._color_picker.show()
        self._draw_node(self._temp_node)

    def destroy(self):
        self.node.selected = False
        return super().destroy()

    def _save_node(self):
        self.node.text = self._temp_node.text
        self.node.color = (
            floor(self._color[0][0]),
            floor(self._color[0][1]),
            floor(self._color[0][2])
        )
        self.node.selected = False
        self.destroy()

    def _draw_node(self, node):
        self.canvas.delete('all')
        self.canvas.create_oval(105, 20, 145, 60, fill=self._color[1])
        self.canvas.create_text(125, 40, text=node.text)


class NodeConnectionConfigRow(Frame):
    def __init__(self, master=None, node=None, connection=None):
        super().__init__(master=master)
        self.node = node
        self.connection = connection
        self._weight_text = StringVar(value='0')

        self._initUI()

    def _initUI(self):
        Label(self, text='+ Node[{}]'.format(self.node.text)
              ).grid(row=0, column=0)
        Entry(self, width=4, textvariable=self._weight_text).grid(row=0, column=1)
        Button(self, text='Apply', command=self._save_connection_width).grid(
            row=0, column=2)

    def _save_connection_width(self):
        try:
            weight = int(self._weight_text.get())
            self.connection.weight = weight
        except TypeError as e:
            print(e)


class MoveTool(Tool):
    def __init__(self, master=None, graph=None):
        super().__init__(master, graph)
        self.master = master
        self.graph = graph

        self.image = PhotoImage(file=r"images/move.png")
        self.image = self.image.subsample(3, 3)

        self.button = Button(self.master, text="Move Node",
                             image=self.image, command=self.on_click)

        self._selected_node: Node = None

    def on_click(self):
        self.master.tool = self

    def handleMouseDown(self, event, double_click=False):
        self._selected_node = mouse_on_a_node(event.pos, self.graph.nodes)

        if double_click and self._selected_node:
            self._selected_node.selected = True
            config_frame = NodeConfigurationFrame(
                self.master, self.graph, self._selected_node)
            config_frame.geometry('250x250+600+600')

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


# TODO: deny making connection to itself
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
                connection = Connection((self._start_node, self._end_node))
                self.graph.connections.append(connection)

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
