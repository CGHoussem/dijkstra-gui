from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.core.window import Window

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'exit_on_escape', '0')

import kivy
kivy.require("2.1.0")


class GraphCanvas(Widget):
    def __init__(self, **kwargs):
        super(GraphCanvas, self).__init__(**kwargs)
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
        )

    def _update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(1, .5, .5, 1)
            Rectangle(size=self.size, pos=self.pos)


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
