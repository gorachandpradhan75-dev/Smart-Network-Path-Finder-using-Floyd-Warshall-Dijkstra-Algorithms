
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import math
import heapq
import random
class Node:
    def __init__(self, name, x=0, y=0):
        self.name = name
        self.x = x
        self.y = y
        self.radius = 22
        self.item_circle = None
        self.item_label = None
class Edge:
    def __init__(self, a: Node, b: Node, w: float):
        self.a = a
        self.b = b
        self.w = w
        self.item_line = None
        self.item_label = None
def dijkstra(graph, start_name):
    dist = {n: math.inf for n in graph}
    prev = {n: None for n in graph}
    dist[start_name] = 0
    pq = [(0, start_name)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return dist, prev
def reconstruct_path(prev, start, goal):
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        if cur == start:
            break
        cur = prev[cur]
    path.reverse()
    if path and path[0] == start:
        return path
    return []
def floyd_warshall(nodes, edges):
    n = len(nodes)
    idx = {name: i for i, name in enumerate(nodes)}
    dist = [[math.inf] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for e in edges:
        i, j = idx[e.a.name], idx[e.b.name]
        dist[i][j] = min(dist[i][j], e.w)
        dist[j][i] = min(dist[j][i], e.w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist, idx
class SmartNetworkApp(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        root.title("Smart Network Path Finder — Animated")
        root.geometry('1100x720')
        self.pack(fill='both', expand=True)
        self.nodes = []  # list of Node
        self.edges = []  # list of Edge
        self.mode = 'idle'  # 'idle', 'add_node', 'add_edge', 'select_src', 'select_dst'
        self.src = None
        self.dst = None
        self.anim_marker = None
        self.anim_after_id = None
        self._build_ui()
        self._bind_canvas()
        self._auto_layout_mode = 'circle'
    def _build_ui(self):
        style = ttk.Style(self.root)
        style.theme_use('default')
        top = ttk.Frame(self)
        top.pack(side='top', fill='x', padx=10, pady=8)
        ttk.Label(top, text='Smart Network Path Finder', font=('Helvetica', 16, 'bold')).pack(side='left')
        control = ttk.Frame(top)
        control.pack(side='right')
        self.algo_var = tk.StringVar(value='Dijkstra')
        algo = ttk.Combobox(control, textvariable=self.algo_var, values=['Dijkstra', 'Floyd–Warshall'], width=18)
        algo.pack(side='left', padx=6)
        ttk.Button(control, text='Add Node', command=self._cmd_add_node).pack(side='left', padx=4)
        ttk.Button(control, text='Add Edge', command=self._cmd_add_edge).pack(side='left', padx=4)
        ttk.Button(control, text='Select Source', command=self._cmd_select_src).pack(side='left', padx=4)
        ttk.Button(control, text='Select Target', command=self._cmd_select_dst).pack(side='left', padx=4)
        ttk.Button(control, text='Run', command=self._cmd_run).pack(side='left', padx=4)
        ttk.Button(control, text='Clear', command=self._cmd_clear).pack(side='left', padx=4)
        ttk.Button(control, text='Layout', command=self._cmd_layout_options).pack(side='left', padx=4)
        self.canvas = tk.Canvas(self, bg='#0f1720', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, padx=12, pady=(0,12))
        self.status = ttk.Label(self, text='Mode: idle — Add nodes/edges and run algorithms', anchor='w')
        self.status.pack(fill='x', padx=10, pady=(0,8))
    def _cmd_add_node(self):
        name = simpledialog.askstring('Add Node', 'Enter node name (unique):', parent=self.root)
        if not name:
            return
        if any(n.name == name for n in self.nodes):
            messagebox.showerror('Error', 'Node with this name already exists.')
            return
        x = random.randint(100, 900)
        y = random.randint(100, 500)
        node = Node(name, x, y)
        self.nodes.append(node)
        self._draw_graph()
        self.status.config(text=f'Added node {name}')
    def _cmd_add_edge(self):
        if len(self.nodes) < 2:
            messagebox.showwarning('Need nodes', 'Add at least two nodes first.')
            return
        add_win = tk.Toplevel(self.root)
        add_win.title('Add Edge')
        add_win.transient(self.root)
        add_win.grab_set()
        ttk.Label(add_win, text='From:').grid(row=0, column=0, padx=6, pady=6)
        from_var = tk.StringVar()
        from_cb = ttk.Combobox(add_win, textvariable=from_var, values=[n.name for n in self.nodes])
        from_cb.grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(add_win, text='To:').grid(row=1, column=0, padx=6, pady=6)
        to_var = tk.StringVar()
        to_cb = ttk.Combobox(add_win, textvariable=to_var, values=[n.name for n in self.nodes])
        to_cb.grid(row=1, column=1, padx=6, pady=6)
        ttk.Label(add_win, text='Weight:').grid(row=2, column=0, padx=6, pady=6)
        w_var = tk.StringVar(value='1')
        w_entry = ttk.Entry(add_win, textvariable=w_var)
        w_entry.grid(row=2, column=1, padx=6, pady=6)
        def do_add():
            a = from_var.get(); b = to_var.get(); w = w_var.get()
            if not a or not b or a == b:
                messagebox.showerror('Invalid', 'Select two different nodes.')
                return
            try:
                wval = float(w)
            except ValueError:
                messagebox.showerror('Invalid', 'Enter numeric weight.')
                return
            na = next(n for n in self.nodes if n.name == a)
            nb = next(n for n in self.nodes if n.name == b)
            for e in list(self.edges):
                if (e.a == na and e.b == nb) or (e.a == nb and e.b == na):
                    self.edges.remove(e)
            e = Edge(na, nb, wval)
            self.edges.append(e)
            add_win.destroy()
            self._draw_graph()
            self.status.config(text=f'Added edge {a} ↔ {b} (w={wval})')
        ttk.Button(add_win, text='Add', command=do_add).grid(row=3, column=0, columnspan=2, pady=8)
    def _cmd_select_src(self):
        self.mode = 'select_src'
        self.status.config(text='Click a node on canvas to set SOURCE')
    def _cmd_select_dst(self):
        self.mode = 'select_dst'
        self.status.config(text='Click a node on canvas to set TARGET')
    def _cmd_run(self):
        algo = self.algo_var.get()
        if algo == 'Dijkstra':
            if not self.src:
                messagebox.showwarning('Source missing', 'Select a source node first.')
                return
            self._run_dijkstra()
        else:
            self._run_floyd()
    def _cmd_clear(self):
        self.nodes.clear()
        self.edges.clear()
        self.src = None
        self.dst = None
        self._cancel_anim()
        self._draw_graph()
        self.status.config(text='Cleared graph')
    def _cmd_layout_options(self):
        choice = simpledialog.askstring('Layout', 'Enter layout: circle / grid', parent=self.root)
        if choice in ('circle', 'grid'):
            self._auto_layout_mode = choice
            self._apply_layout()
            self._draw_graph()
    def _bind_canvas(self):
        self.canvas.bind('<Configure>', lambda e: self._draw_graph())
        self.canvas.bind('<Button-1>', self._on_canvas_click)
    def _on_canvas_click(self, event):
        clicked = None
        for n in self.nodes:
            if (event.x - n.x)**2 + (event.y - n.y)**2 <= (n.radius+2)**2:
                clicked = n
                break
        if clicked:
            if self.mode == 'select_src':
                self.src = clicked
                self.mode = 'idle'
                self.status.config(text=f'Source set: {clicked.name}')
                self._draw_graph()
                return
            elif self.mode == 'select_dst':
                self.dst = clicked
                self.mode = 'idle'
                self.status.config(text=f'Target set: {clicked.name}')
                self._draw_graph()
                return
            else:
                self._show_node_info(clicked)
                return
        if self.mode != 'idle':
            self.mode = 'idle'
            self.status.config(text='Mode: idle')
    def _show_node_info(self, node):
        nb = [e for e in self.edges if e.a == node or e.b == node]
        s = f'Node: {node.name}\nDegree: {len(nb)}\nNeighbors:\n'
        for e in nb:
            other = e.b if e.a == node else e.a
            s += f'  {other.name} (w={e.w})\n'
        messagebox.showinfo('Node info', s)
    def _apply_layout(self):
        w = max(600, self.canvas.winfo_width())
        h = max(400, self.canvas.winfo_height())
        n = len(self.nodes)
        if n == 0:
            return
        if self._auto_layout_mode == 'circle':
            cx, cy = w // 2, h // 2
            r = min(w, h) // 2 - 80
            for i, node in enumerate(self.nodes):
                theta = 2 * math.pi * i / n
                node.x = cx + r * math.cos(theta)
                node.y = cy + r * math.sin(theta)
        else:  # grid
            cols = math.ceil(math.sqrt(n))
            rows = math.ceil(n / cols)
            padx = 120; pady = 80
            cell_w = (w - 2*padx) / max(1, cols - 1)
            cell_h = (h - 2*pady) / max(1, rows - 1)
            for idx, node in enumerate(self.nodes):
                r = idx // cols; c = idx % cols
                node.x = padx + c * cell_w
                node.y = pady + r * cell_h
    def _draw_graph(self):
        self.canvas.delete('all')
        self._apply_layout()
        for e in self.edges:
            x1, y1 = e.a.x, e.a.y
            x2, y2 = e.b.x, e.b.y
            ang = math.atan2(y2 - y1, x2 - x1)
            ax = x1 + math.cos(ang) * e.a.radius * 0.9
            ay = y1 + math.sin(ang) * e.a.radius * 0.9
            bx = x2 - math.cos(ang) * e.b.radius * 0.9
            by = y2 - math.sin(ang) * e.b.radius * 0.9
            e.item_line = self.canvas.create_line(ax+2, ay+2, bx+2, by+2, width=6, fill='#071026', capstyle='round')
            e.item_line = self.canvas.create_line(ax, ay, bx, by, width=4, fill='#6ee7b7', capstyle='round')
            mx, my = (ax+bx)/2, (ay+by)/2
            if e.item_label:
                try:
                    self.canvas.delete(e.item_label)
                except: pass
            e.item_label = self.canvas.create_text(mx, my-12, text=str(e.w), font=('Helvetica', 11, 'bold'), fill='#e6f4ea')
        for n in self.nodes:
            if n.item_circle:
                try:
                    self.canvas.delete(n.item_circle)
                    self.canvas.delete(n.item_label)
                except: pass
            fill = '#0ea5a5' if n == self.src else ('#ef4444' if n == self.dst else '#1f2937')
            outline = '#34d399' if n == self.src else ('#fb7185' if n == self.dst else '#9ca3af')
            n.item_circle = self.canvas.create_oval(n.x - n.radius, n.y - n.radius, n.x + n.radius, n.y + n.radius, fill=fill, outline=outline, width=3)
            n.item_label = self.canvas.create_text(n.x, n.y, text=n.name, font=('Helvetica', 11, 'bold'), fill='white')
        if self.anim_marker:
            self.canvas.tag_raise(self.anim_marker)
    def _run_dijkstra(self):
        graph = {n.name: [] for n in self.nodes}
        for e in self.edges:
            graph[e.a.name].append((e.b.name, e.w))
            graph[e.b.name].append((e.a.name, e.w))
        dist, prev = dijkstra(graph, self.src.name)
        if self.dst:
            path = reconstruct_path(prev, self.src.name, self.dst.name)
            if not path:
                messagebox.showinfo('No Path', f'No path found from {self.src.name} to {self.dst.name}')
                return
            self.status.config(text=f'Shortest {self.src.name} → {self.dst.name}: distance = {dist[self.dst.name]:.2f}')
            self._animate_path(path)
        else:
            win = tk.Toplevel(self.root)
            win.title(f'Dijkstra distances from {self.src.name}')
            tree = ttk.Treeview(win, columns=('node','dist'), show='headings')
            tree.heading('node', text='Node'); tree.heading('dist', text='Distance')
            for name, d in sorted(dist.items()):
                tree.insert('', 'end', values=(name, '∞' if d==math.inf else f'{d:.2f}'))
            tree.pack(expand=True, fill='both', padx=8, pady=8)
    def _run_floyd(self):
        names = [n.name for n in self.nodes]
        dist, idx = floyd_warshall(names, self.edges)
        win = tk.Toplevel(self.root)
        win.title('Floyd–Warshall Distance Matrix')
        frame = ttk.Frame(win)
        frame.pack(padx=8, pady=8)
        for j, name in enumerate([''] + names):
            ttk.Label(frame, text=name, borderwidth=1, relief='ridge', width=8).grid(row=0, column=j)
        for i, rname in enumerate(names):
            ttk.Label(frame, text=rname, borderwidth=1, relief='ridge', width=8).grid(row=i+1, column=0)
            for j, val in enumerate(dist[i]):
                txt = '∞' if val==math.inf else f'{val:.2f}'
                ttk.Label(frame, text=txt, borderwidth=1, relief='ridge', width=8).grid(row=i+1, column=j+1)
    def _animate_path(self, path_names):
        path_nodes = [next(n for n in self.nodes if n.name==nm) for nm in path_names]
        highlight_lines = []
        for i in range(len(path_nodes)-1):
            a = path_nodes[i]; b = path_nodes[i+1]
            for e in self.edges:
                if (e.a==a and e.b==b) or (e.a==b and e.b==a):
                    x1, y1 = a.x, a.y; x2, y2 = b.x, b.y
                    hl = self.canvas.create_line(x1, y1, x2, y2, width=6, fill='#fffbeb', capstyle='round')
                    highlight_lines.append(hl)
                    break
        if self.anim_marker:
            self.canvas.delete(self.anim_marker)
            self.anim_marker = None
        marker_radius = 8
        start = path_nodes[0]
        self.anim_marker = self.canvas.create_oval(start.x-marker_radius, start.y-marker_radius, start.x+marker_radius, start.y+marker_radius, fill='#ffd166', outline='')
        seq = []
        for i in range(len(path_nodes)-1):
            a = path_nodes[i]; b = path_nodes[i+1]
            seq.append((a.x, a.y, b.x, b.y))
        def play_sequence(idx_seg=0, t=0):
            if idx_seg >= len(seq):
                self.status.config(text=f'Arrived: {path_names[-1]}')
                self.root.after(900, lambda: [self.canvas.delete(x) for x in highlight_lines])
                return
            x1,y1,x2,y2 = seq[idx_seg]
            steps = max(10, int(math.hypot(x2-x1, y2-y1)//8))
            nx = x1 + (x2-x1) * (t/steps)
            ny = y1 + (y2-y1) * (t/steps)
            self.canvas.coords(self.anim_marker, nx-marker_radius, ny-marker_radius, nx+marker_radius, ny+marker_radius)
            if t < steps:
                self.anim_after_id = self.root.after(30, lambda: play_sequence(idx_seg, t+1))
            else:
                play_sequence(idx_seg+1, 0)
        play_sequence()
    def _cancel_anim(self):
        if self.anim_after_id:
            try:
                self.root.after_cancel(self.anim_after_id)
            except Exception:
                pass
            self.anim_after_id = None
        if self.anim_marker:
            try:
                self.canvas.delete(self.anim_marker)
            except: pass
            self.anim_marker = None
if __name__ == '__main__':
    root = tk.Tk()
    app = SmartNetworkApp(root)
    root.mainloop()
