import os
import random
import threading
import tkinter as tk

import pygame

from models import *
from views import ToolBar


def random_position() -> int:
    return random.randint(25, 500-25)


def random_color() -> (int, int, int):
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def random_node(nodes) -> Node:
    return Node(random_position(), random_position(), 25, random_color(), '{}'.format(len(nodes)+1))


def quit_callback():
    global running
    running = False


def on_node_hover(graph):
    for node in graph.nodes:
        node.hovered = False
        if node.pos[0] <= pygame.mouse.get_pos()[0]+node.radius and node.pos[0] >= pygame.mouse.get_pos()[0]-node.radius \
                and node.pos[1] <= pygame.mouse.get_pos()[1]+node.radius and node.pos[1] >= pygame.mouse.get_pos()[1]-node.radius:
            node.hovered = True


running = True


def main():
    global running

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
    screen = pygame.display.set_caption(u'Dijkstra 2019-2020')

    # sets the window size
    screen = pygame.display.set_mode((500, 500))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                toolbar.tool.handleMouseMove(event)

                on_node_hover(graph)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                now = pygame.time.get_ticks()
                if now - last_click <= double_click_duration:
                    double_click = True
                else:
                    double_click = False
                last_click = pygame.time.get_ticks()

                toolbar.tool.handleMouseDown(event, double_click)

            elif event.type == pygame.MOUSEBUTTONUP:
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
