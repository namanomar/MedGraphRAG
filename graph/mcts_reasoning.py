import random

class GraphNode:
    def __init__(self, uid, name, neighbors):
        self.uid = uid
        self.name = name
        self.neighbors = neighbors

class MCTS:
    def __init__(self, graph):
        self.graph = graph

    def traverse(self, start_uid, target_name, max_iter=100):
        for _ in range(max_iter):
            path = self._random_walk(start_uid, target_name)
            if path: return path
        return None

    def _random_walk(self, uid, target_name, path=None):
        if path is None: path = [uid]
        node = self.graph.get(uid)
        if node.name == target_name:
            return path
        for next_uid in random.sample(node.neighbors, len(node.neighbors)):
            if next_uid not in path:
                res = self._random_walk(next_uid, target_name, path + [next_uid])
                if res: return res
        return None
