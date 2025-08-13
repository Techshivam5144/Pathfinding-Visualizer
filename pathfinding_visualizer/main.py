import tkinter as tk
from tkinter import messagebox
from collections import deque
import random
import os
SETTINGS_FILE = "settings.txt"

def load_settings():
    """Read settings from file, return dictionary."""
    if not os.path.exists(SETTINGS_FILE):
        return {"show_tutorial": True}
    with open(SETTINGS_FILE, "r") as f:
        lines = f.readlines()
    settings = {}
    for line in lines:
        key, value = line.strip().split("=")
        settings[key] = value.lower() == "true"
    return settings

def save_settings(settings):
    """Save settings to file."""
    with open(SETTINGS_FILE, "w") as f:
        for key, value in settings.items():
            f.write(f"{key}={'True' if value else 'False'}\n")

def show_tutorial():
    tutorial = tk.Tk()
    tutorial.title("Pathfinding Visualizer - Tutorial")
    tutorial.geometry("550x500")
    tutorial.config(bg="white")

    title = tk.Label(
        tutorial, 
        text="Welcome to Pathfinding Visualizer", 
        font=("Arial", 16, "bold"),
        pady=10,
        bg="white"
    )
    title.pack()

    info = """    
This tool helps you visualize popular pathfinding algorithms.

What is a pathfinding algorithm?
At its core, a pathfinding algorithm seeks to find the shortest path between two points. This application visualizes various pathfinding algorithms in action!

If you want to dive right in, feel free to press the "Skip Tutorial" button below.
Controls:
• Press 'S'and click on the grid  to set the START node (green).
• Press 'E' and click on the grid to set the END node (red).
• Press 'W' or double-click drag mouse to place WALLS (black).
• Use the right-side panel to select algorithms.
• Control the speed of the animation with the speed options on the right-side panel
• After running, the shortest path is shown in light blue.

Features:
• Supports BFS, DFS, A*, Dijkstra, and Greedy BFS.
• Weighted & unweighted algorithms.
• Live animation of search process.
• Clear the grid with the "Clear Board" button.
• Click on the grid to place/remove walls.
• Double-click to toggle drag mode for placing/removing walls.
• speed control of animation.
    """
    tk.Label(
        tutorial,
        text=info,
        font=("Arial", 11),
        justify="left",
        padx=20,
        pady=10,
        bg="white"
    ).pack()

    dont_show_var = tk.BooleanVar(value=False)
    tk.Checkbutton(
        tutorial, 
        text="Don't show this tutorial again", 
        variable=dont_show_var,
        bg="white",
        font=("Arial", 10)
    ).pack(pady=5)

    btn_frame = tk.Frame(tutorial, bg="white")
    btn_frame.pack(pady=15)

    tk.Button(
        btn_frame, 
        text="Start Visualizing", 
        font=("Arial", 12, "bold"),
        bg="#27AE60", 
        fg="white", 
        width=15,
        command=lambda: start_main(tutorial, dont_show_var)
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        btn_frame, 
        text="Skip Tutorial", 
        font=("Arial", 12, "bold"),
        bg="#7F8C8D", 
        fg="white", 
        width=15,
        command=lambda: start_main(tutorial, dont_show_var)
    ).grid(row=0, column=1, padx=10)

    tutorial.mainloop()

def start_main(tutorial_window, dont_show_var):
    settings = load_settings()
    if dont_show_var.get():
        settings["show_tutorial"] = False
        save_settings(settings)
    tutorial_window.destroy()
    run_visualizer()
    

# Constants
ROWS, COLS = 20, 40  # Grid size
CELL_SIZE = 25
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

# Colors
EMPTY_COLOR = "white"
WALL_COLOR = "black"
class PathfindingVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pathfinding Visualizer")

        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]  # 0=empty, 1=wall
        self.start = None
        self.end = None

        self.mode = "wall"
        self.drag_mode = True
        self.is_running = False

        self.algo_descriptions = {
            "BFS": "Breath-first Search is unweighted and guarantees the shortest path!",
            "DFS": "Depth-first Search is unweighted and does not guarantee the shortest path!",
            "A*": "A* Search is weighted and guarantees the shortest path!",
            "Dijkstra": "Dijkstra's Algorithm is weighted and guarantees the shortest path!",
            "Greedy BFS": "Greedy Best-first Search is weighted and does not guarantee the shortest path!"
}

        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # 📌 Legend Frame (above the grid)
        legend_frame = tk.Frame(main_frame)
        legend_frame.pack(side="top", pady=10)

        def add_legend_item(parent, color, text):
            box = tk.Label(parent, bg=color, width=2, height=1, relief="solid", borderwidth=1)
            box.pack(side="left", padx=(0, 5))
            label = tk.Label(parent, text=text)
            label.pack(side="left", padx=(0, 15))

        # Add legend items
        add_legend_item(legend_frame, "green", "Start Node")
        add_legend_item(legend_frame, "red", "End Node")
        add_legend_item(legend_frame, "white", "Unvisited Node")
        add_legend_item(legend_frame, "black", "Wall Node")
        add_legend_item(legend_frame, "lightblue", "Shortest Path Found")
        label = tk.Label(legend_frame,   font=("Arial", 13, "bold"), text="Visited nodes: shown in random colors", fg="#34495E") # Dark grayish blue
        label.pack(side="left", padx=(0, 15))

        #Left panel (Description+Grid)
        left_panel = tk.Frame(main_frame, bg="midnight blue")
        left_panel.pack(side="left", fill="both", expand=True)

        # Description label above the grid
        self.algo_description = tk.Label(
            left_panel,
            text="Select an algorithm to see details",
            font=("Arial", 14, "italic"),
            fg="white",
            bg="medium aquamarine",
            anchor="w",
            wraplength=500,
            justify="left"
        )
        self.algo_description.pack(pady=10)
        # Canvas for grid
        self.canvas = tk.Canvas(left_panel, width=600, height=600, bg="white")
        self.canvas.pack(padx=10, pady=10, fill="both", expand=True)

        # Right panel for controls
        side_frame = tk.Frame(main_frame, width=240, bg="midnight blue")  # set width
        side_frame.pack(side="right", fill="y")  # fill vertically
        side_frame.pack_propagate(False)  # prevent auto-shrink to content

        # Heading
        self.algo_heading = tk.Label(side_frame,fg="white", bg="midnight blue", text="Select Algorithm", font=("Arial", 16, "bold"))
        self.algo_heading.pack(pady=10)

        algorithms = [
            ("BFS", self.bfs),
            ("DFS", self.dfs),
            ("A*", self.astar),
            ("Dijkstra", self.dijkstra),
            ("Greedy BFS", self.greedy_best_first)
        ]
        for name, func in algorithms:
            tk.Button(side_frame, font=("Arial", 13, "bold"), text=name, height=2, width=30, fg="white", bg="medium aquamarine",
                    command=lambda f=func, n=name: self.run_algorithm_with_heading(f, n)
            ).pack(pady=5)

        # Speed controls
        self.speed_var = tk.StringVar(value="Average")
        tk.Label(side_frame,fg="white", bg="midnight blue", font=("Arial", 16, "bold"), text="Speed:").pack(pady=(15, 0))
        tk.Radiobutton(side_frame, fg="white",bg="midnight blue", font=("Arial", 16, "bold"), text="Average", variable=self.speed_var, value="Average").pack(anchor="w")
        tk.Radiobutton(side_frame, fg="white", bg="midnight blue", font=("Arial", 16, "bold"), text="Fast", variable=self.speed_var, value="Fast").pack(anchor="w")
        tk.Radiobutton(side_frame, fg="white", bg="midnight blue", font=("Arial", 16, "bold"), text="Slow", variable=self.speed_var, value="Slow").pack(anchor="w")

        # Clear board button
        tk.Button(side_frame, font=("Arial", 10, "bold"),height=2, fg="white", text="Clear Board",bg="lightblue", width=30, command=self.clear_grid).pack(pady=10)

        # Event bindings
        self.canvas.bind("<Button-1>", self.handle_left_click)
        self.canvas.bind("<Double-Button-1>", self.start_drag_mode)
        self.canvas.bind("<B1-Motion>", self.handle_drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag_mode)

        self.root.bind("s", self.set_mode_start)
        self.root.bind("e", self.set_mode_end)
        self.root.bind("w", self.set_mode_wall)

        self.draw_grid()

    def run_algorithm_with_heading(self, algo_func, algo_name):
        # Update heading on the right
        self.algo_heading.config(text=algo_name)

        # Update description above the grid
        desc = self.algo_descriptions.get(algo_name, "")
        self.algo_description.config(text=desc)

        # Run the algorithm
        self.run_algorithm(algo_func)

    def clear_grid(self):
        if self.is_running:
            return 
        for (row, col), rect in self.rects.items():
            self.canvas.itemconfig(rect, fill=EMPTY_COLOR)
            self.grid[row][col] = 0  # reset logical state

        self.start = None
        self.end = None

    def handle_drag(self, event):
        if not self.drag_mode:
            return

        row = event.y // CELL_SIZE
        col = event.x // CELL_SIZE
        if 0 <= row < ROWS and 0 <= col < COLS:
            if (row, col) != self.start and (row, col) != self.end:
                if self.grid[row][col] != 1:
                    self.grid[row][col] = 1
                    self.draw_grid()
    
    def start_drag_mode(self, event):
        self.drag_mode = True
        self.handle_drag(event)  # draw immediately on double-click hold
        print("Drag mode ON")

    def stop_drag_mode(self, event):
        if self.drag_mode:
            self.drag_mode = False
            print("Drag mode OFF")
   
    def draw_grid(self):
        self.rects = {}  # Add this at the start of draw_grid()
        self.canvas.delete("all")
        for row in range(ROWS):
            for col in range(COLS):
                color = EMPTY_COLOR
                if self.grid[row][col] == 1:
                    color = WALL_COLOR
                if self.start == (row, col):
                    color = "green"
                elif self.end == (row, col):
                    color = "red"

                x1, y1 = col * CELL_SIZE, row * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                self.rects[(row, col)] = rect

    def handle_left_click(self, event):
        row = event.y // CELL_SIZE
        col = event.x // CELL_SIZE
        if 0 <= row < ROWS and 0 <= col < COLS:
            if self.mode == "wall":
                if (row, col) != self.start and (row, col) != self.end:
                    self.grid[row][col] = 1 - self.grid[row][col]
            elif self.mode == "start":
                if self.start:
                    old_r, old_c = self.start
                    self.grid[old_r][old_c] = 0
                self.start = (row, col)
            elif self.mode == "end":
                if self.end:
                    old_r, old_c = self.end
                    self.grid[old_r][old_c] = 0
                self.end = (row, col)
            self.draw_grid()

    def set_mode_start(self, event=None):
        self.mode = "start"
        print("Mode: Place Start Node (green)")

    def set_mode_end(self, event=None):
        self.mode = "end"
        print("Mode: Place End Node (red)")

    def set_mode_wall(self, event=None):
        self.mode = "wall"
        print("Mode: Place/Remove Walls")

    def random_color(self):
        return f"#{random.randint(50,255):02x}{random.randint(50,255):02x}{random.randint(50,255):02x}"

    def dfs(self):
        traversal_color = self.random_color()
        if not self.start or not self.end:
            print("Start or End not set!")
            self.is_running = False
            return

        start, end = self.start, self.end
        stack = [start]
        visited = set([start])
        parent = {}

        def visit_next():
            if not stack:
                print("No path found.")
                self.is_running = False
                return

            current = stack.pop()
            row, col = current

            if current == end:
                print("Path found!")
                self.draw_path(parent)
                self.is_running = False
                return

            for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
                nr, nc = row + dr, col + dc
                neighbor = (nr, nc)
                if (
                    0 <= nr < ROWS and 0 <= nc < COLS and
                    self.grid[nr][nc] != 1 and  # not wall
                    neighbor not in visited
                ):
                    stack.append(neighbor)
                    visited.add(neighbor)
                    parent[neighbor] = current
                    self.canvas.itemconfig(
                        self.get_canvas_id(nr, nc), fill=traversal_color
                    )

            if stack:
                self.root.after(self.get_speed_delay(), visit_next)  # Delay for animation
            else:
                # No more nodes to visit, mark done
                self.is_running = False
        visit_next()
        
    def bfs(self):
        traversal_color = self.random_color()
        if not self.start or not self.end:
            print("Start or End not set!")
            self.is_running = False
            return

        start, end = self.start, self.end
        queue = deque([start])
        visited = set([start])
        parent = {}

        def visit_next():
            if not queue:
                print("No path found.")
                self.is_running = False
                return

            current = queue.popleft()
            row, col = current

            if current == end:
                print("Path found!")
                self.draw_path(parent)
                self.is_running = False
                return

            for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
                nr, nc = row + dr, col + dc
                neighbor = (nr, nc)
                if (
                    0 <= nr < ROWS and 0 <= nc < COLS and
                    self.grid[nr][nc] != 1 and  # not wall
                    neighbor not in visited
                ):
                    queue.append(neighbor)
                    visited.add(neighbor)
                    parent[neighbor] = current
                    self.canvas.itemconfig(
                        self.get_canvas_id(nr, nc), fill=traversal_color
                    )

            if queue:
                self.root.after(self.get_speed_delay(), visit_next)
            else:
                # No more nodes to visit, mark done
                self.is_running = False
        visit_next()
    
    def get_canvas_id(self, row, col):
   
        return self.rects.get((row, col))

    def draw_path(self, parent):
        current = self.end
        while current != self.start:
            if current in parent:
                row, col = current
                self.canvas.itemconfig(
                    self.get_canvas_id(row, col), fill="aquamarine"
                )
                current = parent[current]
            else:
                break

    def dijkstra(self):
        traversal_color = self.random_color()  # Random color for this run

        if not self.start or not self.end:
            print("Start or End not set!")
            self.is_running = False
            return

        start, end = self.start, self.end

        # Priority queue for picking the closest node first
        from heapq import heappush, heappop
        pq = []
        heappush(pq, (0, start))  # (distance, node)

        visited = set()
        parent = {}
        distance = {start: 0}

        def visit_next():
            if not pq:
                print("No path found.")
                self.is_running = False
                return

            dist, current = heappop(pq)
            if current in visited:
                self.root.after(1, visit_next)
                return

            visited.add(current)
            row, col = current

            if current == end:
                print("Path found!")
                self.draw_path(parent)
                self.is_running = False
                return

            # Explore neighbors
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = row + dr, col + dc
                neighbor = (nr, nc)

                if (
                    0 <= nr < ROWS and 0 <= nc < COLS and
                    self.grid[nr][nc] != 1 and  # Not a wall
                    neighbor not in visited
                ):
                    new_dist = dist + 1  # All edges weight = 1
                    if new_dist < distance.get(neighbor, float('inf')):
                        distance[neighbor] = new_dist
                        parent[neighbor] = current
                        heappush(pq, (new_dist, neighbor))
                        self.canvas.itemconfig(
                            self.get_canvas_id(nr, nc), fill=traversal_color
                        )

            if pq:
                self.root.after(self.get_speed_delay(), visit_next)  # Delay for animation
            else:
                # No more nodes to visit, mark done
                self.is_running = False
        visit_next()
       
    def astar(self):
        traversal_color = self.random_color()  # Random color for this run

        if not self.start or not self.end:
            print("Start or End not set!")
            self.is_running = False
            return

        start, end = self.start, self.end

        from heapq import heappush, heappop
        pq = []
        heappush(pq, (0, start))  # (f_score, node)

        visited = set()
        parent = {}
        g_score = {start: 0}  # Distance from start
        f_score = {start: self.heuristic(start, end)}  # Estimated total cost

        def visit_next():
            if not pq:
                print("No path found.")
                self.is_running = False
                return

            _, current = heappop(pq)
            if current in visited:
                self.root.after(1, visit_next)
                return

            visited.add(current)
            row, col = current

            if current == end:
                print("Path found!")
                self.draw_path(parent)
                self.is_running = False
                return

            # Explore neighbors
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = row + dr, col + dc
                neighbor = (nr, nc)

                if (
                    0 <= nr < ROWS and 0 <= nc < COLS and
                    self.grid[nr][nc] != 1 and  # Not a wall
                    neighbor not in visited
                ):
                    tentative_g = g_score[current] + 1  # Cost from start to neighbor
                    if tentative_g < g_score.get(neighbor, float('inf')):
                        parent[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + self.heuristic(neighbor, end)
                        heappush(pq, (f_score[neighbor], neighbor))
                        self.canvas.itemconfig(
                            self.get_canvas_id(nr, nc), fill=traversal_color
                        )

            if pq:
                self.root.after(self.get_speed_delay(), visit_next)  # Delay for animation
            else:
                # No more nodes to visit, mark done
                self.is_running = False
        visit_next()
    
    def heuristic(self, a, b):
        (x1, y1), (x2, y2) = a, b
        return abs(x1 - x2) + abs(y1 - y2)

    def greedy_best_first(self):
        traversal_color = self.random_color()  # Random color for this run

        if not self.start or not self.end:
            print("Start or End not set!")
            self.is_running = False
            return

        start, end = self.start, self.end

        from heapq import heappush, heappop
        pq = []
        heappush(pq, (self.heuristic(start, end), start))  # (priority, node)

        visited = set()
        parent = {}

        def visit_next():
            if not pq:
                print("No path found.")
                self.is_running = False
                return

            _, current = heappop(pq)
            if current in visited:
                self.root.after(1, visit_next)
                return

            visited.add(current)
            row, col = current

            if current == end:
                print("Path found!")
                self.draw_path(parent)
                self.is_running = False
                return

            # Explore neighbors
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = row + dr, col + dc
                neighbor = (nr, nc)

                if (
                    0 <= nr < ROWS and 0 <= nc < COLS and
                    self.grid[nr][nc] != 1 and  # Not a wall
                    neighbor not in visited
                ):
                    parent[neighbor] = current
                    heappush(pq, (self.heuristic(neighbor, end), neighbor))
                    self.canvas.itemconfig(
                        self.get_canvas_id(nr, nc), fill=traversal_color
                    )

            if pq:
                self.root.after(self.get_speed_delay(), visit_next)  # Delay for animation
            else:
                # No more nodes to visit, mark done
                self.is_running = False
        visit_next()
       
    def run_algorithm(self, algo_func):
        if self.is_running:
            return
        if not getattr(self, "start", None) or not getattr(self, "end", None):
            messagebox.showinfo(
                "Set START and END before running an algorithm."
            )
            return
        
        for (row,col),rect in self.rects.items():
            if self.grid[row][col] != 1 and (row,col) not in [self.start,self.end]:  # Not a wall and not start/end 
                self.canvas.itemconfig(rect, fill=EMPTY_COLOR)
        
        if self.start:
            self.canvas.itemconfig(self.rects[self.start], fill="green")
        if self.end:
            self.canvas.itemconfig(self.rects[self.end], fill="red")
        self.is_running = True
        # Run the algorithm
        algo_func()

    def get_speed_delay(self):
        if self.speed_var.get() == "Fast":
            return 10      # ms
        elif self.speed_var.get() == "Average":
            return 50
        else:  # Slow
            return 150


def run_visualizer():
    root = tk.Tk()
    app = PathfindingVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    settings = load_settings()
    if settings.get("show_tutorial", True):
        show_tutorial()
    else:
        run_visualizer()