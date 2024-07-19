import json

data = INSERT_JSON

nodes = []

class Node:
    def __init__(self, name, description, x, y):
        self.name = name
        self.description = description
        self.x = x
        self.y = y
        self.connections = []

def load_flowchart(data):
        for node_data in data:
            node = Node(node_data['name'], node_data['description'], node_data['x'], node_data['y'])
            for target_name, connection_name in node_data["connections"]:
                node.connections.append([target_name, connection_name])
            nodes.append(node)


def run_game(node):
        print(node.description, "\n=======")
        choices = {}
        for connection in node.connections:
            choices[connection[1]] = connection[0]
        keys_list = list(choices.keys())
        if len(keys_list) > 0:
            choice = input(f"Choose one: {', '.join(keys_list)}_ ")
            for node in nodes:
                if node.name == choices[choice]:
                    run_game(node)
        else:
            pass

if __name__ == "__main__":
    load_flowchart(data)
    for node in nodes:
        if node.name == "Entry":
            run_game(node)