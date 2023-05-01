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
  - Console Log of the shortest path from a chosen node to all other nodes

### Tech

This application uses a number of open source projects to work properly:
* [Pygame](https://www.pygame.org/) - Modules designed for writing video games
* [Tkinter](https://wiki.python.org/moin/TkInter) - Standard python interface GUI library

### Requirements

This application requires [python](https://www.python.org/) to be installed. 
I have used [conda](https://docs.conda.io/en/latest/) to create the virtual environment.

In order to create the virtual environment with all of the required packages:
```bash
cd dijkstra-gui
conda create --name venv-dijkstra --file conda_requirements.txt
```

### Execution

In order to activate the virtual environment and open the application, run the following commands:
```bash
conda activate venv-dijkstra
python gui.py
```

### Todos

 - [ ] Implementation dijkstra algorithm steps graphically
 - [ ] Serialization / Deserialization of created graphs
 - [ ] Implementation of directed graphs
 - [ ] Improve GUI

License
----

MIT

**Free Software, Hell Yeah!**
