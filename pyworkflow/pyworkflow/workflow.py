import networkx as nx
import json

from .node import Node
from .node_factory import node_factory


class Workflow:
    """ Workflow object

    Attributes:
        graph: A NetworkX Directed Graph
        file_path: Location of a workflow file
    """

    def __init__(self, graph=nx.DiGraph(), file_path=None):
        self._graph = graph
        self._file_path = file_path

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, graph):
        self._graph = graph

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path: str):
        if file_path is None or file_path[-5:] == '.json':
            self._file_path = file_path
        else:
            raise WorkflowException('set_file_path', 'File ' + file_path + ' is not JSON.')

    def get_node(self, node_id):
        """Retrieves Node from workflow, if exists

        Return:
            Node object, if one exists. Otherwise, None.
        """
        if self._graph.has_node(node_id) is not True:
            return None

        node_info = self.graph.nodes[node_id]
        return node_factory(node_info)

    def update_or_add_node(self, node: Node):
        """ Update or add a Node object to the graph.

        Args:
            node - The Node object to update or add to the graph

        TODO:
            * validate() always returns True; this should perform actual validation
        """
        if node.validate():
            # If Node not in graph yet, add it
            if self._graph.has_node(node.node_id) is False:
                self._graph.add_node(node.node_id)

            # Iterate through all Node attributes to add to graph
            node_dict = node.__dict__
            for key in node_dict.keys():
                self._graph.nodes[node.node_id][key] = node_dict[key]

        return

    def add_edge(self, node_from: Node, node_to: Node):
        """ Add a Node object to the graph.

        Args:
            node_from - The Node the edge originates from
              node_to - The Node the edge ends at

        TODO:
            * validate() always returns True; this should perform actual validation
        """
        if node_from.validate() and node_to.validate():
            self._graph.add_edge(node_from.node_id, node_to.node_id)

        return

    def remove_node(self, node):
        """ Remove a node from the graph.

        Raises:
            WorkflowException: on issue with removing node from graph
        """
        try:
            self._graph.remove_node(node.node_id)
        except nx.NetworkXError:
            raise WorkflowException('remove_node', 'Node does not exist in graph.')

    @staticmethod
    def read_graph_json(file_like):
        """Deserialize JSON NetworkX graph

        Args:
            file_like: file-like object from which to read JSON-serialized graph

        Returns:
             NetworkX DiGraph object

        Raises:
            OSError: on file error
            NetworkXError: on issue with loading JSON graph data
        """
        json_data = json.load(file_like)
        return nx.readwrite.json_graph.node_link_graph(json_data)

    @classmethod
    def from_session(cls, data):
        """Create instance from graph (JSON) data and filename

        Typically takes Django session as argument, which contains
        `graph` and `file_path` keys.

        Args:
            data: dict-like with keys `file_path` and `graph`
        """
        file_path = data.get('file_path')
        graph_data = data.get('graph')
        if graph_data is None:
            graph = None
        else:
            graph = nx.readwrite.json_graph.node_link_graph(graph_data)
        return cls(graph, file_path)

    @classmethod
    def from_file(cls, file_like):
        """

        """
        graph = cls.read_graph_json(file_like)
        return cls(graph)

    def to_graph_json(self):
        return nx.readwrite.json_graph.node_link_data(self.graph)

    def to_session_dict(self):
        """Store Workflow information in the Django session.
        """
        out = dict()
        out['graph'] = self.to_graph_json()
        out['file_path'] = self.file_path
        return out


class WorkflowException(Exception):
    def __init__(self, action: str, reason: str):
        self.action = action
        self.reason = reason

    def __str__(self):
        return self.action + ': ' + self.reason