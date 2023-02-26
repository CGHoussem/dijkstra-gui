from random import randint
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker
from kivy.core.text import Label as CoreLabel
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, BoundedNumericProperty, ObjectProperty, NumericProperty

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'exit_on_escape', '0')

import kivy
kivy.require("2.1.0")

# custom imports
from models import Graph
from controllers import dijkstra, find_path


# global variables
NODE_SIZE = 60
nodes = []
connections = []

class NodeUI(Widget):
    NODE_COUNT = 0

    node_id = BoundedNumericProperty(0, min=0, max=100)
    label = StringProperty('New')
    size = ListProperty([NODE_SIZE, NODE_SIZE])
    color = ListProperty([1, 0, 0, 1])
    inv_color = ListProperty([0, 1, 1, 1])
    offset = ListProperty([0, 0])
    state = StringProperty('normal')
    neighbors = ListProperty([])

    label_texture = ObjectProperty()

    def __init__(self, **kwargs):
        super(NodeUI, self).__init__(**kwargs)

        if 'pos' in kwargs:
            self.pos = kwargs['pos']

        self.node_id = NodeUI.NODE_COUNT
        NodeUI.NODE_COUNT += 1

        self.label = f'#{self.node_id}'

    def preview(self, temp_pos):
        self.draw(temp_pos)

    def move(self, new_pos):
        self.pos = (new_pos[0] + self.offset[0], new_pos[1] + self.offset[1])

    def hold(self, pos):
        self.offset = (self.pos[0] - pos[0], self.pos[1] - pos[1])
        self.state = 'held'

    def release(self):
        self.state = 'normal'

    def draw(self, *args):
        Color(*self.color)
        Ellipse(size=self.size, pos=self.pos)
        Color(0, 0, 0, 1)
        Line(width=1.1, ellipse=(self.pos[0], self.pos[1], self.size[0], self.size[1]))
        text = CoreLabel(text=self.label, font_size=16)
        text.refresh()
        self.label_texture = text.texture
        label_pos = (
            self.pos[i] + (self.size[i] - self.label_texture.size[i]) / 2 for i in range(2)
        )
        Rectangle(size=self.label_texture.size, pos=label_pos, texture=self.label_texture)

    def add_neighbor(self, neighbor_node):
        self.neighbors.append(neighbor_node)


class ConnectionUI(Widget):
    default_color = ListProperty([0, 0, 0, 1])
    highlight_color = ListProperty([1, 0, 0, 1])
    line_color = ListProperty([0, 0, 0, 1])
    nodes = ListProperty([])
    weight = NumericProperty()

    def __init__(self, p_nodes, p_weight, **kwargs):
        super(ConnectionUI, self).__init__(**kwargs)

        if len(p_nodes) != 2:
            raise SyntaxError()

        self.nodes = p_nodes
        self.nodes[0].add_neighbor((self.nodes[1], self.nodes[0]))
        self.nodes[1].add_neighbor((self.nodes[0], self.nodes[1]))
        self.weight = p_weight

    def highlight(self):
        self.line_color = self.highlight_color

    def reset_color(self):
        self.line_color = self.default_color

    def draw(self):
        Color(*self.line_color)
        # draw line
        pt_1 = [self.nodes[0].pos[i] + NODE_SIZE / 2 for i in range(2)]
        pt_2 = [self.nodes[1].pos[i] + NODE_SIZE / 2 for i in range(2)]
        Line(points=[pt_1, pt_2], width=1.2, dash_offset=3, dash_length=1)
        # draw text
        text = CoreLabel(text=f"{self.weight}", font_size=18)
        text.refresh()
        label_texture = text.texture
        label_pos = ((pt_1[0] + pt_2[0])/2, (pt_1[1] + pt_2[1])/2)
        Rectangle(size=label_texture.size, pos=label_pos, texture=label_texture)


class ColorPickerWidget(ColorPicker):
    pass


class ColPopup(Popup):
    selected_color = ListProperty([0, 0, 0, 1])


class NodeUIPreview(Widget):
    node_label = StringProperty('')
    node_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super(NodeUIPreview, self).__init__(**kwargs)
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.bind(node_color=self._update_canvas)
        self.bind(node_label=self._update_canvas)
        self.preview_node = NodeUI()

    def _update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas.before:
            self.preview_node.label = self.node_label
            self.preview_node.color = self.node_color
        with self.canvas:
            Color(.9, .9, .9, 1)
            rect_bg = Rectangle(size=self.size, pos=self.pos)
            self.preview_node.pos = (
                rect_bg.pos[0] + rect_bg.size[0] // 2 - NODE_SIZE // 2,
                rect_bg.pos[1] + rect_bg.size[1] // 2 - NODE_SIZE // 2
            )
            self.preview_node.draw()


class EditConnectionUI(Popup):
    node = ObjectProperty(None)
    parent_connections = ListProperty([])

    def __init__(self, **kwargs):
        super(EditConnectionUI, self).__init__(**kwargs)
        self.weight_inputs = list()
        self.nodes_dropdown = DropDown()
        self._neighbors = list()
        self._selected_node = None
        self._connections_backup = None
        self._connections = list()

        self.bind(node=self._init)

    def _init(self, *args):
        self._init_connections()
        self._init_dropdown()

    def _init_connections(self, *args):
        self._connections.clear()
        for _conn in connections:
            if self.node in _conn.nodes:
                self._connections.append(_conn)

    def _init_dropdown(self, *args):
        self.nodes_dropdown.clear_widgets()
        self._neighbors.clear()
        # add 'Select a node' to the dropdown list
        btn = Button(text='Select a node', size_hint_y=None, height=32)
        btn.bind(on_release=lambda btn: self.nodes_dropdown.select(btn.text))
        self.nodes_dropdown.add_widget(btn)
        # fill the self.node neighbors list
        for _conn in connections:
            if self.node in _conn.nodes:
                _neighbor_node = _conn.nodes[0] if _conn.nodes[0] != self.node else _conn.nodes[1]
                self._neighbors.append(_neighbor_node)
        # fill the dropdown list with nodes
        for node in nodes:
            if node != self.node and node not in self._neighbors:
                btn = Button(text=f'{node.label}', size_hint_y=None, height=32)
                btn.bind(on_release=lambda btn: self.nodes_dropdown.select(btn.text))
                self.nodes_dropdown.add_widget(btn)
        self._update_gridlayout()

    def _update_gridlayout(self, *args):
        filtered_widgets = filter(
            lambda widget: isinstance(widget, ScrollView),
            self.content.children
        )
        scroll_view = list(filtered_widgets)[0]
        grid_layout = scroll_view.children[0]
        grid_layout.clear_widgets()
        self.weight_inputs.clear()
        grid_layout.height = len(self._connections) * 30 + 30
        for conn in self._connections:
            neighbor_node = conn.nodes[0] if conn.nodes[0] != self.node else conn.nodes[1]
            lbl_widget = Label(
                text=f"NodeUI ({neighbor_node.label})",
                size_hint=(.5, None),
                size_hint_max_x=150,
                height=30,
            )
            weight_widget = TextInput(
                text=f"{conn.weight}",
                size_hint=(.2, None),
                size_hint_max_x=150,
                height=30,
                halign='left',
                multiline=False
            )
            grid_layout.add_widget(lbl_widget)
            grid_layout.add_widget(weight_widget)
            self.weight_inputs.append(weight_widget)

        if len(self._neighbors) > 0:
            nodes_dropdown_btn = Button(
                text='Select a node',
                on_release=self.nodes_dropdown.open
            )
            self.nodes_dropdown.bind(
                on_select=lambda _, val: setattr(nodes_dropdown_btn, 'text', val)
            )
            add_conn_btn = Button(
                text='Add ConnectionUI',
                on_release=lambda _:self._add_connection(nodes_dropdown_btn.text)
            )
            grid_layout.add_widget(nodes_dropdown_btn)
            grid_layout.add_widget(add_conn_btn)

    def _add_connection(self, node_label):
        for node in nodes:
            if node.label == node_label:
                self._selected_node = node
                break
        if self._selected_node:
            # add a connection with this node
            new_connection = ConnectionUI(p_nodes=[self.node, self._selected_node], p_weight=0)
            self._connections.append(new_connection)
            # update the gridlayout
            self._update_gridlayout()

    def _cancel_changes(self):
        self._init()
        self.dismiss()

    def _save_changes(self):
        self.parent_connections = self._connections
        self.dismiss()


class NodeUIConfig(Popup):
    node = ObjectProperty(None)
    selected_color = ListProperty([0, 0, 0, 1])

    def __init__(self, **kwargs):
        super(Popup, self).__init__(**kwargs)
        filtered_widgets = filter(
            lambda widget: isinstance(widget, NodeUIPreview),
            self.content.children
        )
        self._node_preview_widget = list(filtered_widgets)[0]
        self._edit_conn_popup = EditConnectionUI()
        self._edit_conn_popup.parent_connections = connections
        self._edit_conn_popup.bind(on_dismiss=self._update_connections_count)

        self._connections_count_label = None
        gridlayout_widgets = filter(
            lambda widget: isinstance(widget, GridLayout),
            self.content.children
        )
        boxlayout_widgets = filter(
            lambda widget: isinstance(widget, BoxLayout),
            list(gridlayout_widgets)[0].children
        )
        label_widgets = filter(
            lambda widget: isinstance(widget, Label),
            list(boxlayout_widgets)[0].children
        )
        self._connections_count_label = list(label_widgets)[1]

    def _count_connections(self):
        _count = 0
        if self.node:
            for conn in self._edit_conn_popup.parent_connections:
                if self.node in conn.nodes:
                    _count += 1
        return _count

    def _update_connections_count(self, *args):
        # update connections count label (gui)
        self._connections_count_label.text = str(self._count_connections())

    def _open_color_picker(self):
        col_popup = ColPopup()
        col_popup.selected_color = self.node.color
        col_popup.bind(on_dismiss=self._update_color)
        col_popup.open()

    def _update_color(self, instance):
        if self._node_preview_widget:
            self._node_preview_widget.node_color = instance.selected_color
        self.selected_color = instance.selected_color
        return False

    def _on_label_input(self, value):
        if self._node_preview_widget:
            self._node_preview_widget.node_label = value

    def _open_connections_popup(self):
        # open popup and edit connections
        self._edit_conn_popup.node = self.node
        self._edit_conn_popup.open()

    def _apply_changes(self):
        global connections
        self.node.label = self.ids.label_input.text
        self.node.color = self.selected_color
        # apply weights & new connections
        for conn, weight_input in \
            zip(self._edit_conn_popup.parent_connections, self._edit_conn_popup.weight_inputs):
            conn.weight = int(weight_input.text)
        connections = self._edit_conn_popup.parent_connections
        self.dismiss()


class FindPath(Popup):

    def __init__(self, **kwargs):
        super(Popup, self).__init__(**kwargs)

        gridlayout_widgets = filter(
            lambda widget: isinstance(widget, GridLayout),
            self.content.children
        )
        self.gridlayout = list(gridlayout_widgets)[0]

        self._start_node_btn = None
        self._dest_node_btn = None
        self._start_dropdown = DropDown()
        self._dest_dropdown = DropDown()
        self._init_start_dropdown()
        self._init_dest_dropdown()

    def _init_start_dropdown(self):
        btn = Button(text='Select a node', size_hint_y=None, height=32)
        btn.bind(on_release=lambda btn: self._start_dropdown.select(btn.text))
        self._start_dropdown.add_widget(btn)
        for node in nodes:
            btn = Button(text=f'{node.label}', size_hint_y=None, height=32)
            btn.bind(on_release=lambda btn: self._start_dropdown.select(btn.text))
            self._start_dropdown.add_widget(btn)

        self._start_node_btn = Button(
            text='Select a node', on_release=self._start_dropdown.open,
            size_hint_y=None, height=32
        )

        self._start_dropdown.bind(on_select=lambda _, val: setattr(self._start_node_btn, 'text', val))

        self.gridlayout.add_widget(Label(text='Start NodeUI', size_hint_y=None, height=32))
        self.gridlayout.add_widget(self._start_node_btn)

    def _init_dest_dropdown(self):
        btn = Button(text='Select a node', size_hint_y=None, height=32)
        btn.bind(on_release=lambda btn: self._dest_dropdown.select(btn.text))
        self._dest_dropdown.add_widget(btn)
        for node in nodes:
            btn = Button(text=f'{node.label}', size_hint_y=None, height=32)
            btn.bind(on_release=lambda btn: self._dest_dropdown.select(btn.text))
            self._dest_dropdown.add_widget(btn)

        self._dest_node_btn = Button(
            text='Select a node', on_release=self._dest_dropdown.open,
            size_hint_y=None, height=32
        )

        self._dest_dropdown.bind(on_select=lambda _, val: setattr(self._dest_node_btn, 'text', val))

        self.gridlayout.add_widget(Label(text='End NodeUI', size_hint_y=None, height=32))
        self.gridlayout.add_widget(self._dest_node_btn)

    def _calculate(self, *args):
        # find the appropriate nodes
        start_node = None
        dest_node = None
        for node in nodes:
            if start_node is None and node.label == self._start_node_btn.text:
                start_node = node
            if dest_node is None and node.label == self._dest_node_btn.text:
                dest_node = node
        if start_node and dest_node and start_node != dest_node:
            dijkstra(graph, start_node)
            try:
                path_connections = find_path(graph, start_node, dest_node)
                for conn in path_connections:
                    conn.highlight()
                self.dismiss()
            except KeyError as _err:
                _msg = _err.args[0]
                # TODO: create a error dialog with the msg
                print(_msg)


class GraphCanvas(Widget):
    def __init__(self, **kwargs):
        super(GraphCanvas, self).__init__(**kwargs)
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas
        )

        # TODO: find a way to position the nodes after the canvas "last" update
        Clock.schedule_once(self._position_nodes, 1.0)

    def _position_nodes(self, *args):
        print(self.size)
        nodes[0].pos = (randint(NODE_SIZE, int(self.size[0])), randint(NODE_SIZE, int(self.size[1])))
        nodes[1].pos = (randint(NODE_SIZE, int(self.size[0])), randint(NODE_SIZE, int(self.size[1])))
        nodes[2].pos = (randint(NODE_SIZE, int(self.size[0])), randint(NODE_SIZE, int(self.size[1])))
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.clear()

        with self.canvas:
            for conn in connections:
                conn.draw()
            for node in nodes:
                node.draw()
            self.canvas.ask_update()

    def on_touch_move(self, touch):
        for node in nodes:
            if node.state == 'held':
                node.move(touch.pos)
                break
        self._update_canvas()

    def on_touch_down(self, touch):
        for node in nodes:
            if node.collide_point(*touch.pos):
                if touch.is_double_tap:
                    ## on double tap, open the node config
                    node_config_popup = NodeUIConfig()
                    # pass along the node + some attributes
                    node_config_popup.node = node
                    node_config_popup.selected_color = node.color
                    # update canvas on popup dismiss
                    node_config_popup.bind(on_dismiss=self._update_canvas)
                    node_config_popup.open()
                else:
                    node.hold(touch.pos)
                break

    def on_touch_up(self, touch):
        for node in nodes:
            node.release()


class ToolBar(BoxLayout):

    def __init__(self, **kwargs):
        super(ToolBar, self).__init__(**kwargs)


    def _on_load_btn_click(self):
        print("load_btn_click")

    def _on_save_btn_click(self):
        print("save_btn_click")

    def _on_move_btn_click(self):
        print("move_btn_click")

    def _on_add_btn_click(self):
        print("add_btn_click")

    def _on_delete_btn_click(self):
        print("delete_btn_click")

    def _on_connect_btn_click(self):
        print("connect_btn_click")

    def _on_dijkstra_btn_click(self):
        self.popup = FindPath()
        self.popup.open()
        self.popup.bind(on_dismiss=lambda _: self._update_canvas())

    def _update_canvas(self, *args):
        # TODO: update GraphCanvas UI
        # TODO: open a small popup with transparent bg that shows the weight & a reset button
        pass


class MainScreen(BoxLayout):
    pass


class DijkstraApp(App):
    def __init__(self, **kwargs):
        super(DijkstraApp, self).__init__(**kwargs)
        self._initialize_global_vars()

    def _initialize_global_vars(self):
        global nodes, graph, connections

        nodes = [NodeUI(), NodeUI(), NodeUI()]
        cnn = ConnectionUI(p_nodes=[nodes[0], nodes[1]], p_weight=15)
        connections.append(cnn)
        graph = Graph(nodes, connections)

    def build(self):
        Window.clearcolor = (0.9, 0.9, 0.9, 1)
        return MainScreen()


if __name__ == '__main__':
    DijkstraApp().run()
