import tkinter as tk
from tkinter import simpledialog, filedialog
import json

class Node:
    def __init__(self, canvas, name, description, x, y, app):
        self.app = app
        self.canvas = canvas
        self.name = name
        self.description = description
        self.x = x
        self.y = y
        self.id = self.canvas.create_rectangle(x-20, y-20, x+20, y+20, fill="lightblue", tags="node")
        self.text_id = self.canvas.create_text(x, y, text=name, tags="node_text")
        self.update_size()
        self.connections = []
        self.canvas.tag_bind(self.id, '<ButtonPress-1>', self.on_press)
        self.canvas.tag_bind(self.id, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.id, '<Button-3>', self.show_popup)
        self.canvas.tag_bind(self.text_id, '<ButtonPress-1>', self.on_press)
        self.canvas.tag_bind(self.text_id, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.text_id, '<Button-3>', self.show_popup)

    def update_size(self):
        text_bbox = self.canvas.bbox(self.text_id)
        x1, y1, x2, y2 = text_bbox
        padding = 5
        self.canvas.coords(self.id, x1-padding, y1-padding, x2+padding, y2+padding)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        self.canvas.move(self.id, dx, dy)
        self.canvas.move(self.text_id, dx, dy)
        self.x += dx
        self.y += dy
        self.start_x = event.x
        self.start_y = event.y

    def show_popup(self, event):
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Change Name", command=self.change_name)
        menu.add_command(label="Change Description", command=self.change_description)
        menu.add_command(label="Add Connection", command=self.add_connection)
        menu.add_separator()
        menu.add_command(label="Delete", command=self.delete)
        menu.add_command(label="Cancel", command=self.cancel)
        menu.post(event.x_root, event.y_root)

    def cancel(self):
        pass

    def change_name(self):
        new_name = simpledialog.askstring("Change Name", "Enter the new name:", initialvalue=self.name)
        if new_name is not None:
            if new_name not in self.app.used_names:
                self.app.used_names.remove(self.name)
                self.app.used_names.append(new_name)
                self.name = new_name
                self.canvas.itemconfig(self.text_id, text=new_name)
                self.update_size()
            else:
                self.app.display_error("Names must be unique")

    def change_description(self):
        new_description = simpledialog.askstring("Change Description", "Enter the new description:",
                                                 initialvalue=self.description)
        if new_description is not None:
            self.description = new_description

    def add_connection(self):
        target_name = simpledialog.askstring("Add Connection", "Enter the target node name:")
        if target_name is not None:
            if target_name in self.app.used_names:
                connection_name = simpledialog.askstring("Add Connection", "Enter the connections condition:")
                if connection_name is not None:
                    self.connections.append([target_name, connection_name])
                    self.update_connections()
            else:
                self.app.display_error("Target must be a valid Node")

    def delete(self):
        self.canvas.delete(self.id)
        self.canvas.delete(self.text_id)
        self.app.nodes.remove(self)
        self.app.used_names.remove(self.name)

    def update_connections(self):
        self.canvas.delete("line_" + str(self.id))
        for target_name, connection_name in self.connections:
            for node in self.app.nodes:
                if node.name == target_name:
                    x1, y1 = self.x, self.y
                    x2, y2 = node.x, node.y
                    self.canvas.create_line(x1, y1, x2, y2, tags=("line_" + str(self.id)), arrow=tk.LAST, arrowshape=(8, 10, 3),
                                            fill="black")
                    label_x = (x1 + x2) / 2
                    label_y = (y1 + y2) / 2
                    self.canvas.create_text(label_x, label_y, text=connection_name, fill='black', font='Arial 10 bold', tags="connection_text")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("CYOAFlowchart")
        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.nodes = []
        self.used_names = []
        self.canvas.bind("<Button-3>", self.create_node)
        self.canvas.bind("<Up>", self.arrow_scroll)
        self.canvas.bind("<Down>", self.arrow_scroll)
        self.canvas.bind("<Left>", self.arrow_scroll)
        self.canvas.bind("<Right>", self.arrow_scroll)
        self.canvas.focus_set()
        self.error_text = self.canvas.create_text(400, 20, text="", fill='red', font=('Arial', 12), anchor=tk.CENTER)
        self.update()
        self.create_menu()

    def arrow_scroll(self, event):
        x, y = self.canvas.canvasx(0), self.canvas.canvasy(0)
        if event.keysym == "Up":
            self.canvas.yview_scroll(-1, "units")
        elif event.keysym == "Down":
            self.canvas.yview_scroll(1, "units")
        elif event.keysym == "Left":
            self.canvas.xview_scroll(-1, "units")
        elif event.keysym == "Right":
            self.canvas.xview_scroll(1, "units")

    def create_node(self, event):
        x, y = event.x, event.y
        overlapping_nodes = self.canvas.find_overlapping(x, y, x, y)
        for node_id in overlapping_nodes:
            tags = self.canvas.gettags(node_id)
            if 'node' in tags:
                return
        node_name = simpledialog.askstring("New Node", "Enter Node Name:")
        if node_name is not None:
            if node_name in self.used_names:
                self.display_error("Name must be unique")
            else:
                new_node = Node(self.canvas, node_name, "Enter Node Description Here", x, y, self)
                self.nodes.append(new_node)
                self.used_names.append(node_name)

    def display_error(self, message):
        self.canvas.itemconfig(self.error_text, text=message)

    def update(self):
        text_items = self.canvas.find_withtag("connection_text")
        for item in text_items:
            self.canvas.delete(item)
        for node in self.nodes:
            node.update_connections()
        self.root.after(20, self.update)

    def create_menu(self):
        menubar = tk.Menu(self.root)

        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="Run", command=self.run)
        run_menu.add_command(label="Build", command=self.build)
        menubar.add_cascade(label="Compile", menu=run_menu)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save", command=self.save_flowchart)
        file_menu.add_command(label="Load", command=self.load_flowchart)
        menubar.add_cascade(label="File", menu=file_menu)

        self.root.config(menu=menubar)
    
    def build(self):
        data = []
        for node in self.nodes:
            connections = [(target_name, connection_name) for target_name, connection_name in node.connections]
            node_data = {
                'x': node.x,
                'y': node.y,
                'name': node.name,
                'description': node.description,
                'connections': connections
            }
            data.append(node_data)
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])

        file = ""
        with open("template.py", "r") as f:
            file = f.read()
            f.close()
        file = str(file).replace("INSERT_JSON", str(data))

        with open(file_path, "w") as f:
            f.write(file)

    def run(self):
        for node in self.nodes:
            if node.name == "Entry":
                self.run_game(node)

    def run_game(self, node):
        print(node.description, "\n=======")
        choices = {}
        for connection in node.connections:
            choices[connection[1]] = connection[0]
        keys_list = list(choices.keys())
        if len(keys_list) > 0:
            choice = input(f"Choose one: {', '.join(keys_list)}_ ")
            for node in self.nodes:
                if node.name == choices[choice]:
                    run_game(node)
        else:
            pass

    def save_flowchart(self):
        file_path = tk.filedialog.asksaveasfilename(defaultextension='.json', filetypes=[("JSON Files", "*.json")])
        if file_path:
            data = []
            for node in self.nodes:
                connections = [(target_name, connection_name) for target_name, connection_name in node.connections]
                node_data = {
                    'x': node.x,
                    'y': node.y,
                    'name': node.name,
                    'description': node.description,
                    'connections': connections
                }
                data.append(node_data)
            with open(file_path, "w") as f:
                json.dump(data, f)
    
    def load_flowchart(self):
        self.clear_canvas()
        file_path = tk.filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            nodes = []
            for node_data in data:
                node = Node(self.canvas, node_data['name'], node_data['description'], node_data['x'], node_data['y'], self)
                for target_name, connection_name in node_data["connections"]:
                    node.connections.append([target_name, connection_name])
                self.used_names.append(node.name)
                self.nodes.append(node)

    def clear_canvas(self):
        for node in self.nodes:
            node.delete()
        self.nodes = []

if __name__ == "__main__":
    root=tk.Tk()
    app=App(root)
    root.mainloop()