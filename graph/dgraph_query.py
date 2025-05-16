import requests
from graph.mcts_reasoning import GraphNode

def build_graph():
    q = """
    {
      all(func: has(name)) {
        uid
        name
        type
        treats { uid }
        side_effect { uid }
      }
    }
    """
    resp = requests.post("http://localhost:8080/query", json={"query": q}).json()
    graph = {}
    for node in resp["data"]["all"]:
        neighbors = []
        neighbors += [n["uid"] for n in node.get("treats", [])]
        neighbors += [n["uid"] for n in node.get("side_effect", [])]
        graph[node["uid"]] = GraphNode(node["uid"], node["name"], neighbors)
    return graph
