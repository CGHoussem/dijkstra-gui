# Dijkstra Algorithm GUI Implementation

Dijkstra's algorithm (or Dijkstra's Shortest Path First algorithm, SPF algorithm) is an algorithm for finding the shortest paths between nodes in a graph, which may represent, for example, road networks. It was conceived by computer scientist Edsger W. Dijkstra in 1956 and published three years later. For better understading of the algorithm, check out [the wikipedia page](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm).

This application is still UNDER DEVELOPMENT!!

# Features

  - A Toolbar with the following tools:
    - Move Tool (Selecting / Moving nodes)
    - Add Tool (Adding nodes)
    - Connect Tool (Connecting nodes)
    - Delete Tool (Deleting nodes therefore it's connections)
  - The ability to customize nodes (text / color / its connections weights)

### Tech

This application uses a number of open source projects to work properly:

* [Pygame](https://www.pygame.org/) - Modules designed for writing video games
* [Tkinter](https://wiki.python.org/moin/TkInter) - Standard python interface GUI library

And of course this application itself is open source with a public repository on GitHub.

### Installation

This application requires [Python](https://www.python.org/) to be installed in your computer.

Install the necessary modules using [pip](https://pypi.org/project/pip/).

```sh
$ cd dijkstra-gui
$ pip install -r requirements.txt
$ python main.py
```

### Todos

 - Implementation of dijkstra algorithm in an existing graph
 - Reorganizing the whole project

License
----

MIT

**Free Software, Hell Yeah!**
