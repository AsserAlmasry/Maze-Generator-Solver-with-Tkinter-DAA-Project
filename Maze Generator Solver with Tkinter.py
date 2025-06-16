import random
from collections import deque
import heapq
import customtkinter as ctk
from tkinter import ttk, messagebox

CELL_SIZE = 20
STEP_DELAY = 25
   
ctk.set_appearance_mode("light blue") 
ctk.set_appearance_mode("dark") 


class MazeGenerator:
    def __init__(self, rows, cols, single_solution=True):
        self.rows = rows
        self.cols = cols
        self.single_solution = single_solution
        self.maze = [['#' for _ in range(cols)] for _ in range(rows)]

    def generate_maze(self):
        self._dfs(0, 0)
        if not self.single_solution:
            for _ in range((self.rows * self.cols) // 5):
                r = random.randrange(1, self.rows - 1, 2)
                c = random.randrange(1, self.cols - 1, 2)
                self.maze[r][c] = random.choices(['.', '~', '^'], weights=[0.5, 0.3, 0.2])[0]
        self.maze[0][0] = 'S'  
        self.maze[0][self.cols - 1] = 'E'

    def _dfs(self, row, col):
        self.maze[row][col] = '.'
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        for dy, dx in directions:
            nr, nc = row + dy, col + dx
            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.maze[nr][nc] == '#':
                self.maze[row + dy // 2][col + dx // 2] = '.'
                self._dfs(nr, nc)


class MazeSolver:
    def __init__(self, maze, canvas, delay=STEP_DELAY):
        self.maze = maze
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.weights = {'#': float('inf'), '.': 1, 'S': 1, 'E': 1, '~': 3, '^': 5}
        self.canvas = canvas
        self.delay = delay

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def solve_dfs(self):
        start, end = (0, 0), (self.rows - 1, self.cols - 1)
        stack = [(start, [start])]
        visited = {start}
        while stack:
            (r, c), path = stack.pop()
            self.draw_step(path, "red")
            if (r, c) == end:
                return path
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and self.maze[nr][nc] != '#' and (nr, nc) not in visited:
                    stack.append(((nr, nc), path + [(nr, nc)]))
                    visited.add((nr, nc))
            self.canvas.update()
            self.canvas.after(self.delay)

    def solve_bfs(self):
        start, end = (0, 0), (self.rows - 1, self.cols - 1)
        queue = deque([(start, [start])])
        visited = {start}
        while queue:
            (r, c), path = queue.popleft()
            self.draw_step(path, "blue")
            if (r, c) == end:
                return path
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and self.maze[nr][nc] != '#' and (nr, nc) not in visited:
                    queue.append(((nr, nc), path + [(nr, nc)]))
                    visited.add((nr, nc))
            self.canvas.update()
            self.canvas.after(self.delay)


    def solve_dijkstra(self):
        start, end = (0, 0), (self.rows - 1, self.cols - 1)
        heap = [(0, start, [start])]
        visited = {}
        while heap:
            cost, current, path = heapq.heappop(heap)
            self.draw_step(path, "purple")
            if current in visited and visited[current] <= cost:
                continue
            visited[current] = cost
            if current == end:
                return path
            r, c = current
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    tile = self.maze[nr][nc]
                    if tile != '#':
                        new_cost = cost + self.weights.get(tile, 1)
                        heapq.heappush(heap, (new_cost, (nr, nc), path + [(nr, nc)]))
            self.canvas.update()
            self.canvas.after(self.delay)

    def solve_greedy(self):
        start, end = (0, 0), (self.rows - 1, self.cols - 1)
        open_set = [(self.heuristic(start, end), start, [start])]
        visited = set()
        while open_set:
            h, current, path = heapq.heappop(open_set)
            self.draw_step(path, "orange")
            if current == end:
                return path
            if current in visited:
                continue
            visited.add(current)
            r, c = current
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and self.maze[nr][nc] != '#' and (nr, nc) not in visited:
                    heapq.heappush(open_set, (self.heuristic((nr, nc), end), (nr, nc), path + [(nr, nc)]))
            self.canvas.update()
            self.canvas.after(self.delay)
    
    def solve_astar(self):
        start, end = (0, 0), (self.rows - 1, self.cols - 1)
        open_set = [(self.heuristic(start, end), 0, start, [start])]
        visited = {}
        while open_set:
            f, g, current, path = heapq.heappop(open_set)
            self.draw_step(path, "green")
            if current in visited and visited[current] <= g:
                continue
            visited[current] = g
            if current == end:
                return path
            r, c = current
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    tile = self.maze[nr][nc]
                    if tile != '#':
                        new_cost = g + self.weights.get(tile, 1)
                        heapq.heappush(open_set, (
                            new_cost + self.heuristic((nr, nc), end),
                            new_cost, (nr, nc), path + [(nr, nc)]))
            self.canvas.update()
            self.canvas.after(self.delay)

    def draw_step(self, path, color):
        maze_copy = [row[:] for row in self.maze]
        for r, c in path[1:-1]:
            maze_copy[r][c] = '*'
        self.draw_maze(maze_copy, color)

    def draw_maze(self, maze, color):
        self.canvas.delete("all")
        cell = min(500 // self.rows, CELL_SIZE)
        colors = {'#': 'black', '.': 'white', 'S': 'green', 'E': 'red',
                  '~': 'sandybrown', '^': 'gray', '*': color}
        for i, row in enumerate(maze):
            for j, val in enumerate(row):
                x0, y0 = j * cell, i * cell
                x1, y1 = x0 + cell, y0 + cell
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=colors.get(val, 'white'), outline='gray')


class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Generator & Solver")
        self.generator = None

        self.report_box = ctk.CTkTextbox(root, height=100, width=500, fg_color="white", text_color="black")
        self.report_box.pack(pady=5)
        self.report_box.configure(state='disabled')



        ctk.CTkLabel(root, text="Maze Size:").pack()
        self.size_entry = ctk.CTkEntry(root)
        self.size_entry.insert(0, "15")
        self.size_entry.pack()

        self.solution_type_var = ctk.StringVar(value="Single")
        ctk.CTkLabel(root, text="Solution Type:").pack()
        ctk.CTkRadioButton(root, text="One Solution", variable=self.solution_type_var, value="Single").pack(anchor='w')
        ctk.CTkRadioButton(root, text="Multiple Solutions (weighted)", variable=self.solution_type_var, value="Multiple").pack(anchor='w')

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10)
        self.maze_tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.maze_tab, text="Maze Display")
        self.canvas = ctk.CTkCanvas(self.maze_tab, width=500, height=500, bg="white")
        self.canvas.pack()

        self.btn_frame = ctk.CTkFrame(root)
        self.btn_frame.pack(pady=5)
        ctk.CTkButton(self.btn_frame, text="Generate Maze", command=self.generate_maze).grid(row=0, column=0, padx=5)
        ctk.CTkButton(self.btn_frame, text="Compare Algorithms", command=self.choose_comparison).grid(row=0, column=1, padx=5)

    def generate_maze(self):
        try:
            size = int(self.size_entry.get())
            if size % 2 == 0:
                size += 1
            self.generator = MazeGenerator(size, size, single_solution=self.solution_type_var.get() == "Single")
            self.generator.generate_maze()
            for tab in self.notebook.tabs():
                if self.notebook.tab(tab, "text") != "Maze Display":
                    self.notebook.forget(tab)
            self.draw_maze(self.generator.maze)
        except ValueError:
            messagebox.showerror("Error", "Invalid maze size!")

    def draw_maze(self, maze):
        self.canvas.delete("all")
        cell = min(500 // len(maze), CELL_SIZE)
        color_map = {'#': 'black', '.': 'white', 'S': 'green', 'E': 'red',
                     '~': 'sandybrown', '^': 'gray', '*': 'blue'}
        for i, row in enumerate(maze):
            for j, val in enumerate(row):
                x0, y0 = j * cell, i * cell
                x1, y1 = x0 + cell, y0 + cell
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color_map.get(val, 'white'), outline='gray')

    def choose_comparison(self):
        if not self.generator:
            messagebox.showinfo("Generate First", "Please generate a maze first.")
            return

        algorithms = ["DFS", "BFS", "A*", "Dijkstra", "Greedy"]
        selected = []

        top = ctk.CTkToplevel(self.root)
        top.title("Choose Algorithms")
        ctk.CTkLabel(top, text="Select 2 to 5 algorithms to compare:").pack()
        vars = {}

        for alg in algorithms:
            var = ctk.IntVar()
            ctk.CTkCheckBox(top, text=alg, variable=var).pack(anchor='w')
            vars[alg] = var

        def submit():
            selected.clear()
            for alg, var in vars.items():
                if var.get():
                    selected.append(alg)
            if len(selected) < 2 or len(selected) > 5:
                messagebox.showerror("Invalid", "Select between 2 and 5 algorithms")
            else:
                top.destroy()
                self.open_comparison_tabs(selected)

        ctk.CTkButton(top, text="Compare", command=submit).pack(pady=5)

    def open_comparison_tabs(self, algorithms):
        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, "text") != "Maze Display":
                self.notebook.forget(tab)

        results = []
        for alg in algorithms:
            frame = ctk.CTkFrame(self.notebook)
            self.notebook.add(frame, text=alg)
            canvas = ctk.CTkCanvas(frame, width=500, height=500, bg="white")
            canvas.pack()
            solver = MazeSolver([row[:] for row in self.generator.maze], canvas)
            path = None
            if alg == "DFS":
                path = solver.solve_dfs()
            elif alg == "BFS":
                path = solver.solve_bfs()
            elif alg == "A*":
                path = solver.solve_astar()
            elif alg == "Dijkstra":
                path = solver.solve_dijkstra()
            elif alg == "Greedy":
                path = solver.solve_greedy()

            if path:
                steps = len(path)
                results.append({'name': alg, 'length': steps, 'efficiency': 1 / steps if steps > 0 else 0})

        self.report_box.configure(state='normal')
        self.report_box.delete("1.0", "end")
        self.report_box.insert("end", "📊 Comparison Report:\n")

        if results:
            best = min(results, key=lambda r: r['length'])
            most_efficient = max(results, key=lambda r: r['efficiency'])
            for r in results:
                self.report_box.insert("end", f"{r['name']} - Path Length: {r['length']} - Efficiency: {r['efficiency']:.4f}\n")
            self.report_box.insert("end", f"🏁 Shortest Path: {best['name']}\n")
            self.report_box.insert("end", f"🎯 Most Efficient: {most_efficient['name']}")
        else:
            self.report_box.insert("end", "No valid paths found.")

        self.report_box.config(state='disabled')


if __name__ == "__main__":
    root = ctk.CTk()
    app = MazeApp(root)
    root.mainloop()
