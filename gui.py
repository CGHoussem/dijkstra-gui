from random import randint
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker
from kivy.core.text import Label as CoreLabel
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, BoundedNumericProperty, ObjectProperty, NumericProperty

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'exit_on_escape', '0')

import kivy
kivy.require("2.1.0")


NODE_SIZE = 60


class Node(Widget):
    NODE_COUNT = 0

    node_id = BoundedNumericProperty(0, min=0, max=100)
    label = StringProperty('New')
    size = ListProperty([NODE_SIZE, NODE_SIZE])
    color = ListProperty([1, 0, 0, 1])
    inv_color = ListProperty([0, 1, 1, 1])
    offset = ListProperty([0, 0])
    state = StringProperty('normal')
    connections = ListProperty([]) #[(neighbor_node, weight), ...]

    label_texture = ObjectProperty()

    def __init__(self, **kwargs):
        super(Node, self).__init__(**kwargs)

        if 'pos' in kwargs:
            self.pos = kwargs['pos']

        self.node_id = Node.NODE_COUNT
        Node.NODE_COUNT += 1

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


class Connection(Widget):
    line_color = ListProperty([0, 0, 0, 1])
    nodes = ListProperty([])
    weight = NumericProperty()

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


class NodePreview(Widget):
    node_label = StringProperty('')
    node_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super(NodePreview, self).__init__(**kwargs)
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.bind(node_color=self._update_canvas)
        self.bind(node_label=self._update_canvas)
        self.preview_node = Node()

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


class EditConnection(Popup):
    node = ObjectProperty(Node())
    connections = ListProperty([])

    def __init__(self, **kwargs):
        super(EditConnection, self).__init__(**kwargs)
        self._weight_inputs = []
        self.bind(connections=self._update_gridlayout)

    def _update_gridlayout(self, *args):
        filtered_widgets = filter(
            lambda widget: isinstance(widget, ScrollView),
            self.content.children
        )
        scroll_view = list(filtered_widgets)[0]
        grid_layout = scroll_view.children[0]
        grid_layout.height = len(self.connections)*30
        for conn in self.connections:
            neighbor_node = conn.nodes[0] if conn.nodes[0] != self.node else conn.nodes[1]
            lbl_widget = Label(
                text=f"Node ({neighbor_node.label})",
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

            self._weight_inputs.append(weight_widget)

    def _apply_new_weights(self):
        for conn, weight_input in zip(self.connections, self._weight_inputs):
            conn.weight = int(weight_input.text)
        self.dismiss()


class NodeConfig(Popup):
    node = ObjectProperty(None)
    selected_color = ListProperty([0, 0, 0, 1])
    new_connections = ListProperty([])

    def __init__(self, **kwargs):
        super(Popup, self).__init__(**kwargs)
        filtered_widgets = filter(
            lambda widget: isinstance(widget, NodePreview),
            self.content.children
        )
        self._node_preview_widget = list(filtered_widgets)[0]
        self.bind(node=self._update_new_connections)

        self._edit_conn_popup = EditConnection()

    def _update_new_connections(self, *args):
        # deep copy node's connections to new_connections
        self.new_connections = list()
        for conn in self.node.connections:
            new_conn = Connection()
            new_conn.weight = conn.weight
            new_conn.nodes = conn.nodes
            self.new_connections.append(new_conn)
        self._edit_conn_popup.connections = self.new_connections

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
        self.node.label = self.ids.label_input.text
        self.node.color = self.selected_color
        # copy the weights over to the node's connections
        for node_conn, new_conn in zip(self.node.connections, self.new_connections):
            node_conn.weight = new_conn.weight
        self.dismiss()


class GraphCanvas(Widget):
    nodes = ListProperty([Node(), Node()])
    connections = ListProperty([])

    def __init__(self, **kwargs):
        super(GraphCanvas, self).__init__(**kwargs)
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas
        )
        self.nodes[0].pos = (randint(NODE_SIZE, self.size[0]), randint(NODE_SIZE, self.size[1]))
        self.nodes[1].pos = (randint(NODE_SIZE, self.size[0]), randint(NODE_SIZE, self.size[1]))

        cnn = Connection()
        cnn.nodes.append(self.nodes[0])
        cnn.nodes.append(self.nodes[1])
        cnn.weight = 15
        self.connections.append(cnn)
        self.nodes[0].connections.append(cnn)
        self.nodes[1].connections.append(cnn)

    def _update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            for connection in self.connections:
                connection.draw()
            for node in self.nodes:
                node.draw()
            self.canvas.ask_update()

    def on_touch_move(self, touch):
        for node in self.nodes:
            if node.state == 'held':
                node.move(touch.pos)
                break
        self._update_canvas()

    def on_touch_down(self, touch):
        for node in self.nodes:
            if node.collide_point(*touch.pos):
                if touch.is_double_tap:
                    ## on double tap, open the node config
                    node_config_popup = NodeConfig()
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
        for node in self.nodes:
            node.release()


class ToolBar(BoxLayout):

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
        print("dijkstra_btn_click")


class MainScreen(BoxLayout):
    pass


class DijkstraApp(App):

    def build(self):
        Window.clearcolor = (0.9, 0.9, 0.9, 1)
        return MainScreen()


if __name__ == '__main__':
    DijkstraApp().run()
