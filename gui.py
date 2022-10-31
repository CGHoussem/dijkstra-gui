from random import randint
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.core.text import Label as CoreLabel
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, BooleanProperty, BoundedNumericProperty, ObjectProperty

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'exit_on_escape', '0')

import kivy
kivy.require("2.1.0")


NODE_SIZE = 60


class Node(Widget):
    node_id = BoundedNumericProperty(0, min=0, max=100)
    label = StringProperty('New')
    size = ListProperty([NODE_SIZE, NODE_SIZE])
    color = ListProperty([1, 0, 0, 1])
    inv_color = ListProperty([0, 1, 1, 1])
    offset = ListProperty([0, 0])
    on_hold = BooleanProperty(False)
    state = StringProperty('normal')
    connections = ListProperty([])

    label_texture = ObjectProperty()

    def __init__(self, **kwargs):
        super(Node, self).__init__(**kwargs)

        if 'pos' in kwargs:
            self.pos = kwargs['pos']

    def preview(self, temp_pos):
        self.draw(temp_pos)

    def move(self, new_pos):
        if self.on_hold:
            self.pos = (new_pos[0] + self.offset[0], new_pos[1] + self.offset[1])

    def hold(self, pos):
        self.offset = (self.pos[0] - pos[0], self.pos[1] - pos[1])
        self.on_hold = True

    def release(self):
        self.on_hold = False

    def draw(self, *args):
        Color(*self.color)
        Ellipse(size=self.size, pos=self.pos)
        Color(0, 0, 0, 1)
        Line(width=1.1, ellipse=(self.pos[0], self.pos[1], self.size[0], self.size[1]))
        text = CoreLabel(text=self.label, font_size=16)
        text.refresh()
        self.label_texture = text.texture
        label_pos = (self.pos[i] + (self.size[i] - self.label_texture.size[i]) / 2 for i in range(2))
        Rectangle(size=self.label_texture.size, pos=label_pos, texture=self.label_texture)


class GraphCanvas(Widget):
    node = ObjectProperty(Node())

    def __init__(self, **kwargs):
        super(GraphCanvas, self).__init__(**kwargs)
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
        )
        self.node.pos = (randint(NODE_SIZE, self.size[0]), randint(NODE_SIZE, self.size[1]))

    def _update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            self.node.draw()
            self.canvas.ask_update()

    def on_touch_move(self, touch):
        self.node.move(touch.pos)
        self._update_canvas()

    def on_touch_down(self, touch):
        if self.node.collide_point(*touch.pos):
            if touch.is_double_tap:
                # TODO: implement node config
                print('double tap on node')
            else:
                self.node.hold(touch.pos)

    def on_touch_up(self, touch):
        self.node.release()


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
