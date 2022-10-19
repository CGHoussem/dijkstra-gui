import os

import pygame
from pygame.locals import QUIT, MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN

from models import Graph
from views import ToolBar


def quit_callback():
    global RUNNING
    RUNNING = False

def on_node_hover(graph):
    for node in graph.nodes:
        node.hovered = False
        if node.pos[0] <= pygame.mouse.get_pos()[0]+node.radius and node.pos[0] >= pygame.mouse.get_pos()[0]-node.radius \
                and node.pos[1] <= pygame.mouse.get_pos()[1]+node.radius and node.pos[1] >= pygame.mouse.get_pos()[1]-node.radius:
            node.hovered = True

RUNNING = True

def main():
    global RUNNING

    # sets the window position
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 100)

    # initialize pygame
    pygame.init()
    pygame.font.init()

    # initialize tkinter
    graph = Graph()
    toolbar = ToolBar(graph)
    toolbar.geometry(
        '{}x{}+100+600'.format(toolbar.winfo_width(), toolbar.winfo_height()))
    toolbar.protocol("WM_DELETE_WINDOW", quit_callback)

    # start pygame clock
    clock = pygame.time.Clock()

    # initialize variables
    font = pygame.font.SysFont(None, 25)
    framerate = 30
    double_click_duration = 150  # ms
    last_click = 0

    # sets the window title
    screen = pygame.display.set_caption('Dijkstra 2019-2020')

    # sets the window size
    screen = pygame.display.set_mode((500, 500))

    while RUNNING:
        for event in pygame.event.get():
            if event.type == QUIT:
                RUNNING = False
            elif event.type == MOUSEMOTION:
                toolbar.tool.handleMouseMove(event)

                on_node_hover(graph)
            elif event.type == MOUSEBUTTONDOWN:
                now = pygame.time.get_ticks()
                if now - last_click <= double_click_duration:
                    double_click = True
                else:
                    double_click = False
                last_click = pygame.time.get_ticks()

                toolbar.tool.handleMouseDown(event, double_click)

            elif event.type == MOUSEBUTTONUP:
                toolbar.tool.handleMouseUp(event)

        # Rendering
        clock.tick(framerate)
        screen.fill((255, 255, 255))

        toolbar.tool.renderPreview(screen)

        for connection in graph.connections:
            connection.render(screen, font)

        for node in graph.nodes:
            node.render(screen, font)

        pygame.display.update()

        try:
            toolbar.update()
        except:
            print("ToolBar error")

    toolbar.destroy()


if __name__ == "__main__":
    main()
