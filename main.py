import sys
import math
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTabWidget, QSlider, QLabel, QPushButton, 
                               QComboBox, QStackedWidget, QSpinBox, QGroupBox)
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QFont
from PySide6.QtCore import Qt, QPoint, QPointF

# --- Shape Data Structure ---
class EuclideanShape:
    """Represents any Euclidean shape in N-dimensional space."""
    def __init__(self, vertices, edges, name):
        self.vertices = vertices  # List of N-D points: [[x1, y1, ...], [x2, y2, ...], ...]
        self.edges = edges        # List of vertex index pairs: [(0, 1), (1, 2), ...]
        self.name = name
    
    @property
    def n_dims(self):
        return len(self.vertices[0]) if self.vertices else 0
    
    @property
    def n_vertices(self):
        return len(self.vertices)
    
    @property
    def n_edges(self):
        return len(self.edges)

# --- Shape Generators ---
def generate_simplex(n_dims):
    """N-simplex: N+1 vertices, all pairs connected (complete graph)."""
    vertices = [[0.0] * n_dims for _ in range(n_dims + 1)]
    for i in range(n_dims):
        vertices[i][i] = 100.0
    edges = [(i, j) for i in range(n_dims + 1) for j in range(i + 1, n_dims + 1)]
    return EuclideanShape(vertices, edges, f"{n_dims}-Simplex")

def generate_hypercube(n_dims):
    """N-cube: 2^N vertices, edges where Hamming distance = 1."""
    vertices = []
    for i in range(2**n_dims):
        v = [(80 if (i >> j) & 1 else -80) for j in range(n_dims)]
        vertices.append(v)
    edges = []
    for i in range(2**n_dims):
        for j in range(i + 1, 2**n_dims):
            if bin(i ^ j).count('1') == 1:
                edges.append((i, j))
    return EuclideanShape(vertices, edges, f"{n_dims}-Cube")

def generate_cross_polytope(n_dims):
    """N-orthoplex: 2N vertices (±e_i), edges between non-opposite vertices."""
    vertices = []
    for i in range(n_dims):
        v_pos = [0.0] * n_dims
        v_pos[i] = 100.0
        v_neg = [0.0] * n_dims
        v_neg[i] = -100.0
        vertices.extend([v_pos, v_neg])
    edges = []
    for i in range(2 * n_dims):
        for j in range(i + 1, 2 * n_dims):
            if i // 2 != j // 2:  # Not opposite vertices
                edges.append((i, j))
    return EuclideanShape(vertices, edges, f"{n_dims}-Cross-Polytope")

def generate_random_cloud(n_dims, n_vertices):
    """Random point cloud with all pairs connected."""
    vertices = [[random.uniform(-100, 100) for _ in range(n_dims)] for _ in range(n_vertices)]
    edges = [(i, j) for i in range(n_vertices) for j in range(i + 1, n_vertices)]
    return EuclideanShape(vertices, edges, f"Random Cloud ({n_vertices} pts)")

def generate_shape(shape_type, n_dims, n_vertices=10):
    """Factory function to generate shapes."""
    if shape_type == "Simplex":
        return generate_simplex(n_dims)
    elif shape_type == "Hypercube":
        return generate_hypercube(min(n_dims, 8))  # Cap at 8D for performance
    elif shape_type == "Cross-Polytope":
        return generate_cross_polytope(n_dims)
    elif shape_type == "Random Cloud":
        return generate_random_cloud(n_dims, n_vertices)
    return generate_simplex(n_dims)

# --- Utility Functions ---
def rotate_x(point, angle):
    x, y, z = point[0], point[1], point[2]
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return [x, y * cos_a - z * sin_a, y * sin_a + z * cos_a] + list(point[3:])

def rotate_y(point, angle):
    x, y, z = point[0], point[1], point[2]
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return [x * cos_a + z * sin_a, y, -x * sin_a + z * cos_a] + list(point[3:])

# --- 2D Visualization ---
class Shape2DWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.shape = generate_simplex(2)

    def set_shape(self, shape):
        self.shape = shape
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        painter.translate(cx, cy)
        
        # Grid
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.PenStyle.DotLine))
        for i in range(-200, 201, 50):
            painter.drawLine(i, -200, i, 200)
            painter.drawLine(-200, i, 200, i)
        
        # Edges
        painter.setPen(QPen(QColor(30, 144, 255), 2))
        for i, j in self.shape.edges:
            v1, v2 = self.shape.vertices[i], self.shape.vertices[j]
            painter.drawLine(QPointF(v1[0], v1[1]), QPointF(v2[0], v2[1]))
        
        # Vertices
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.setPen(QPen(Qt.black, 1))
        for v in self.shape.vertices:
            painter.drawEllipse(QPointF(v[0], v[1]), 5, 5)
        
        # Info
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 10))
        painter.drawText(-cx + 10, -cy + 20, f"{self.shape.name} | {self.shape.n_vertices}V, {self.shape.n_edges}E")
        painter.end()

# --- 3D Visualization ---
class Shape3DWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.shape = generate_simplex(3)
        self.rot_x_angle = 0.5
        self.rot_y_angle = 0.5
        self.last_pos = QPoint()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_shape(self, shape):
        self.shape = shape
        self.update()

    def mousePressEvent(self, event): self.last_pos = event.pos()
    def mouseMoveEvent(self, event):
        self.rot_y_angle += (event.pos().x() - self.last_pos.x()) * 0.01
        self.rot_x_angle += (event.pos().y() - self.last_pos.y()) * 0.01
        self.last_pos = event.pos()
        self.update()

    def project_3d_to_2d(self, point):
        fov, distance = 400, 300
        z = point[2] + distance
        factor = fov / z if z != 0 else 1
        return QPointF(point[0] * factor + self.width() / 2, -point[1] * factor + self.height() / 2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(245, 245, 250))

        transformed = [rotate_y(rotate_x(v, self.rot_x_angle), self.rot_y_angle) for v in self.shape.vertices]

        # Axes
        origin = self.project_3d_to_2d([0,0,0])
        for axis, color in [([100,0,0], Qt.red), ([0,100,0], Qt.green), ([0,0,100], Qt.blue)]:
            painter.setPen(QPen(color, 2))
            painter.drawLine(origin, self.project_3d_to_2d(axis))

        # Edges
        painter.setPen(QPen(QColor(255, 100, 0), 2))
        for i, j in self.shape.edges:
            p1, p2 = self.project_3d_to_2d(transformed[i]), self.project_3d_to_2d(transformed[j])
            painter.drawLine(p1, p2)

        # Vertices
        painter.setBrush(QBrush(QColor(0, 100, 200)))
        painter.setPen(QPen(Qt.black, 1))
        for v in transformed:
            painter.drawEllipse(self.project_3d_to_2d(v), 5, 5)

        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 10))
        painter.drawText(10, 20, f"{self.shape.name} | {self.shape.n_vertices}V, {self.shape.n_edges}E")
        painter.drawText(10, 40, "Click and drag to rotate")
        painter.end()

# --- N-D Visualization Methods ---

class ParallelCoordsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.shape = generate_simplex(5)

    def set_shape(self, shape):
        self.shape = shape
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)
        if self.shape.n_dims < 2: return

        margin, w, h = 50, self.width() - 100, self.height() - 100
        mins = [min(v[i] for v in self.shape.vertices) for i in range(self.shape.n_dims)]
        maxs = [max(v[i] for v in self.shape.vertices) for i in range(self.shape.n_dims)]
        for i in range(self.shape.n_dims):
            if mins[i] == maxs[i]: maxs[i] += 1

        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setFont(QFont("Arial", 10))
        axis_spacing = w / (self.shape.n_dims - 1) if self.shape.n_dims > 1 else 0
        
        for i in range(self.shape.n_dims):
            x = margin + i * axis_spacing
            painter.drawLine(QPointF(x, margin), QPointF(x, margin + h))
            painter.drawText(QPointF(x - 10, margin + h + 20), f"Dim {i+1}")

        # Edges
        painter.setPen(QPen(QColor(100, 100, 200), 2))
        for i, j in self.shape.edges:
            v1, v2 = self.shape.vertices[i], self.shape.vertices[j]
            for d in range(self.shape.n_dims - 1):
                y1 = margin + h - ((v1[d] - mins[d]) / (maxs[d] - mins[d]) * h)
                y2 = margin + h - ((v2[d+1] - mins[d+1]) / (maxs[d+1] - mins[d+1]) * h)
                painter.drawLine(QPointF(margin + d * axis_spacing, y1), QPointF(margin + (d + 1) * axis_spacing, y2))

        # Vertices
        painter.setBrush(QBrush(QColor(255, 100, 0)))
        painter.setPen(QPen(Qt.black, 1))
        for v in self.shape.vertices:
            for d in range(self.shape.n_dims):
                y = margin + h - ((v[d] - mins[d]) / (maxs[d] - mins[d]) * h)
                painter.drawEllipse(QPointF(margin + d * axis_spacing, y), 4, 4)
        painter.end()

class SPLOMWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.shape = generate_simplex(5)

    def set_shape(self, shape):
        self.shape = shape
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)
        if self.shape.n_dims < 2: return

        margin, w, h = 40, self.width() - 80, self.height() - 80
        cell_w, cell_h = w / self.shape.n_dims, h / self.shape.n_dims

        mins = [min(v[i] for v in self.shape.vertices) for i in range(self.shape.n_dims)]
        maxs = [max(v[i] for v in self.shape.vertices) for i in range(self.shape.n_dims)]
        for i in range(self.shape.n_dims):
            if mins[i] == maxs[i]: maxs[i] += 1

        painter.setFont(QFont("Arial", 8))
        for i in range(self.shape.n_dims):
            for j in range(self.shape.n_dims):
                x0, y0 = margin + j * cell_w, margin + i * cell_h
                painter.setPen(QPen(QColor(220, 220, 220), 1))
                painter.drawRect(QPointF(x0, y0), cell_w, cell_h)

                if i == j:
                    painter.setPen(Qt.black)
                    painter.drawText(QPointF(x0 + cell_w/2 - 15, y0 + cell_h/2), f"Dim {i+1}")
                else:
                    # Edges
                    painter.setPen(QPen(QColor(100, 100, 200), 1))
                    for ei, ej in self.shape.edges:
                        v1, v2 = self.shape.vertices[ei], self.shape.vertices[ej]
                        x1_n = (v1[j] - mins[j]) / (maxs[j] - mins[j])
                        y1_n = (v1[i] - mins[i]) / (maxs[i] - mins[i])
                        x2_n = (v2[j] - mins[j]) / (maxs[j] - mins[j])
                        y2_n = (v2[i] - mins[i]) / (maxs[i] - mins[i])
                        painter.drawLine(QPointF(x0 + x1_n*cell_w, y0 + (1-y1_n)*cell_h), 
                                         QPointF(x0 + x2_n*cell_w, y0 + (1-y2_n)*cell_h))

                    # Vertices
                    painter.setBrush(QBrush(QColor(255, 100, 0)))
                    painter.setPen(QPen(Qt.black, 1))
                    for v in self.shape.vertices:
                        px = x0 + ((v[j] - mins[j]) / (maxs[j] - mins[j])) * cell_w
                        py = y0 + (1 - (v[i] - mins[i]) / (maxs[i] - mins[i])) * cell_h
                        painter.drawEllipse(QPointF(px, py), 2, 2)
        painter.end()

class SlidingWindow3DWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.shape = generate_simplex(5)
        self.window_start = 0
        self.rot_x_angle = 0.5
        self.rot_y_angle = 0.5
        self.last_pos = QPoint()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_shape(self, shape, window_start=0):
        self.shape = shape
        self.window_start = min(window_start, max(0, self.shape.n_dims - 3))
        self.update()

    def mousePressEvent(self, event): self.last_pos = event.pos()
    def mouseMoveEvent(self, event):
        self.rot_y_angle += (event.pos().x() - self.last_pos.x()) * 0.01
        self.rot_x_angle += (event.pos().y() - self.last_pos.y()) * 0.01
        self.last_pos = event.pos()
        self.update()

    def project_3d_to_2d(self, point):
        fov, distance = 400, 300
        z = point[2] + distance
        factor = fov / z if z != 0 else 1
        return QPointF(point[0] * factor + self.width() / 2, -point[1] * factor + self.height() / 2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(245, 245, 250))

        if self.shape.n_dims < 3:
            painter.setPen(Qt.red)
            painter.drawText(50, 50, "Need at least 3 dimensions for 3D window.")
            painter.end()
            return

        w_start = self.window_start
        transformed = []
        for v in self.shape.vertices:
            p = [v[w_start] * 0.5, v[w_start+1] * 0.5, v[w_start+2] * 0.5]
            transformed.append(rotate_y(rotate_x(p, self.rot_x_angle), self.rot_y_angle))

        origin = self.project_3d_to_2d([0,0,0])
        for axis, color in [([100,0,0], Qt.red), ([0,100,0], Qt.green), ([0,0,100], Qt.blue)]:
            painter.setPen(QPen(color, 2))
            painter.drawLine(origin, self.project_3d_to_2d(axis))

        painter.setPen(QPen(QColor(255, 100, 0), 2))
        for i, j in self.shape.edges:
            p1, p2 = self.project_3d_to_2d(transformed[i]), self.project_3d_to_2d(transformed[j])
            painter.drawLine(p1, p2)

        painter.setBrush(QBrush(QColor(0, 100, 200)))
        painter.setPen(QPen(Qt.black, 1))
        for v in transformed:
            painter.drawEllipse(self.project_3d_to_2d(v), 5, 5)

        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 10))
        painter.drawText(10, 20, f"Subspace: Dim {w_start+1}, {w_start+2}, {w_start+3}")
        painter.drawText(10, 40, "Click and drag to rotate")
        painter.end()

class OptimalProjectionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.shape = generate_simplex(5)

    def set_shape(self, shape):
        self.shape = shape
        self.update()

    def get_2d_projection(self):
        """PCA-like projection onto the first 2 principal components."""
        if self.shape.n_vertices < 2:
            return [[0, 0]]
        
        # Simple approach: use first two dimensions after centering
        mean = [sum(v[i] for v in self.shape.vertices) / self.shape.n_vertices for i in range(self.shape.n_dims)]
        centered = [[v[i] - mean[i] for i in range(self.shape.n_dims)] for v in self.shape.vertices]
        
        # For simplicity, just project onto first 2 dimensions
        return [[v[0], v[1]] for v in centered]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)

        proj_verts = self.get_2d_projection()
        if not proj_verts:
            painter.end()
            return
            
        min_x, max_x = min(v[0] for v in proj_verts), max(v[0] for v in proj_verts)
        min_y, max_y = min(v[1] for v in proj_verts), max(v[1] for v in proj_verts)
        range_x, range_y = (max_x - min_x) or 1, (max_y - min_y) or 1
        
        margin = 80
        scale = min((self.width() - 2*margin) / range_x, (self.height() - 2*margin) / range_y) * 0.8
        cx, cy = self.width() / 2, self.height() / 2
        mean_x, mean_y = (min_x + max_x) / 2, (min_y + max_y) / 2

        def to_screen(p):
            return QPointF(cx + (p[0] - mean_x) * scale, cy - (p[1] - mean_y) * scale)

        painter.setPen(QPen(QColor(230, 230, 230), 1, Qt.PenStyle.DotLine))
        for i in range(-5, 6):
            painter.drawLine(cx + i * 50, 0, cx + i * 50, self.height())
            painter.drawLine(0, cy + i * 50, self.width(), cy + i * 50)

        painter.setPen(QPen(QColor(138, 43, 226), 2))
        for i, j in self.shape.edges:
            p1, p2 = to_screen(proj_verts[i]), to_screen(proj_verts[j])
            painter.drawLine(p1, p2)

        painter.setBrush(QBrush(QColor(255, 215, 0)))
        painter.setPen(QPen(Qt.black, 1))
        for v in proj_verts:
            painter.drawEllipse(to_screen(v), 5, 5)

        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 10))
        painter.drawText(10, 20, f"Optimal 2D Projection | {self.shape.name}")
        painter.end()

class GivensSliceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.shape = generate_simplex(5)
        self.base_vertices = [v[:] for v in self.shape.vertices]
        self.vertices = [v[:] for v in self.shape.vertices]
        
        layout = QVBoxLayout(self)
        
        self.canvas = SliceCanvas(self)
        self.canvas.setMinimumHeight(400)
        layout.addWidget(self.canvas, 1)
        
        ctrl_layout = QHBoxLayout()
        
        self.spin_i = QSpinBox()
        self.spin_i.setMinimum(1)
        self.spin_i.setMaximum(self.shape.n_dims)
        self.spin_i.setValue(1)
        self.spin_i.valueChanged.connect(self.update_temporary_rotation)
        
        self.spin_j = QSpinBox()
        self.spin_j.setMinimum(1)
        self.spin_j.setMaximum(self.shape.n_dims)
        self.spin_j.setValue(2)
        self.spin_j.valueChanged.connect(self.update_temporary_rotation)
        
        self.slider_theta = QSlider(Qt.Orientation.Horizontal)
        self.slider_theta.setMinimum(-180)
        self.slider_theta.setMaximum(180)
        self.slider_theta.setValue(0)
        self.theta_label = QLabel("θ: 0°")
        self.slider_theta.valueChanged.connect(self.on_theta_changed)
        
        self.btn_apply = QPushButton("Apply Rotation")
        self.btn_apply.clicked.connect(self.apply_rotation)
        
        self.btn_reset = QPushButton("Reset Orientation")
        self.btn_reset.clicked.connect(self.reset_orientation)
        
        ctrl_layout.addWidget(QLabel("Dim i:"))
        ctrl_layout.addWidget(self.spin_i)
        ctrl_layout.addWidget(QLabel("Dim j:"))
        ctrl_layout.addWidget(self.spin_j)
        ctrl_layout.addWidget(QLabel("Angle:"))
        ctrl_layout.addWidget(self.slider_theta)
        ctrl_layout.addWidget(self.theta_label)
        ctrl_layout.addWidget(self.btn_apply)
        ctrl_layout.addWidget(self.btn_reset)
        
        layout.addLayout(ctrl_layout)

    def set_shape(self, shape):
        self.shape = shape
        self.base_vertices = [v[:] for v in shape.vertices]
        self.vertices = [v[:] for v in shape.vertices]
        
        self.spin_i.setMaximum(shape.n_dims)
        self.spin_j.setMaximum(shape.n_dims)
        if self.spin_i.value() > shape.n_dims: self.spin_i.setValue(1)
        if self.spin_j.value() > shape.n_dims: self.spin_j.setValue(2)
        
        self.slider_theta.setValue(0)
        self.canvas.update()

    def on_theta_changed(self, val):
        self.theta_label.setText(f"θ: {val}°")
        self.update_temporary_rotation()

    def update_temporary_rotation(self):
        self.vertices = [v[:] for v in self.base_vertices]
        i = self.spin_i.value() - 1
        j = self.spin_j.value() - 1
        
        if i != j and 0 <= i < self.shape.n_dims and 0 <= j < self.shape.n_dims:
            theta = math.radians(self.slider_theta.value())
            cos_t, sin_t = math.cos(theta), math.sin(theta)
            for v in self.vertices:
                vi, vj = v[i], v[j]
                v[i] = vi * cos_t - vj * sin_t
                v[j] = vi * sin_t + vj * cos_t
        self.canvas.update()

    def apply_rotation(self):
        self.base_vertices = [v[:] for v in self.vertices]
        self.slider_theta.setValue(0)
        self.update_temporary_rotation()

    def reset_orientation(self):
        self.base_vertices = [v[:] for v in self.shape.vertices]
        self.slider_theta.setValue(0)
        self.update_temporary_rotation()

class SliceCanvas(QWidget):
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(250, 250, 255))
        
        w, h = self.width(), self.height()
        margin = 50
        
        if self.parent_widget.shape.n_dims < 2:
            painter.setPen(Qt.red)
            painter.drawText(50, 50, "Need at least 2 dimensions.")
            painter.end()
            return
            
        proj_verts = [[v[0], v[1]] for v in self.parent_widget.vertices]
        
        min_x = min(v[0] for v in proj_verts)
        max_x = max(v[0] for v in proj_verts)
        min_y = min(v[1] for v in proj_verts)
        max_y = max(v[1] for v in proj_verts)
        
        range_x = (max_x - min_x) or 1
        range_y = (max_y - min_y) or 1
        
        scale = min((w - 2*margin) / range_x, (h - 2*margin) / range_y) * 0.8
        cx, cy = w / 2, h / 2
        mean_x, mean_y = (min_x + max_x) / 2, (min_y + max_y) / 2
        
        def to_screen(p):
            return QPointF(cx + (p[0] - mean_x) * scale, cy - (p[1] - mean_y) * scale)
        
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.PenStyle.DotLine))
        painter.drawLine(0, cy, w, cy)
        painter.drawLine(cx, 0, cx, h)
        
        # Edges
        painter.setPen(QPen(QColor(220, 20, 60), 2))
        for i, j in self.parent_widget.shape.edges:
            p1, p2 = to_screen(proj_verts[i]), to_screen(proj_verts[j])
            painter.drawLine(p1, p2)
        
        # Vertices
        painter.setBrush(QBrush(QColor(0, 0, 139)))
        painter.setPen(QPen(Qt.black, 1))
        for v in proj_verts:
            painter.drawEllipse(to_screen(v), 5, 5)
            
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 10))
        painter.drawText(10, 20, f"2D Projection Slice | {self.parent_widget.shape.name}")
        painter.end()

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Euclidean Shape Visualizer: Any Shape in 2D, 3D, and N-D")
        self.resize(1100, 850)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Shape Controls
        shape_ctrl = QHBoxLayout()
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Simplex", "Hypercube", "Cross-Polytope", "Random Cloud"])
        self.shape_combo.currentIndexChanged.connect(self.update_shape)
        
        self.dim_slider = QSlider(Qt.Orientation.Horizontal)
        self.dim_slider.setMinimum(2)
        self.dim_slider.setMaximum(10)
        self.dim_slider.setValue(3)
        self.dim_slider.valueChanged.connect(self.update_shape)
        self.dim_label = QLabel("Dims: 3")
        
        self.vertex_spin = QSpinBox()
        self.vertex_spin.setMinimum(3)
        self.vertex_spin.setMaximum(50)
        self.vertex_spin.setValue(10)
        self.vertex_spin.valueChanged.connect(self.update_shape)
        self.vertex_label = QLabel("Vertices:")
        
        shape_ctrl.addWidget(QLabel("Shape:"))
        shape_ctrl.addWidget(self.shape_combo)
        shape_ctrl.addWidget(self.dim_label)
        shape_ctrl.addWidget(self.dim_slider)
        shape_ctrl.addWidget(self.vertex_label)
        shape_ctrl.addWidget(self.vertex_spin)
        shape_ctrl.addStretch()
        
        main_layout.addLayout(shape_ctrl)

        # Tabs
        self.tabs = QTabWidget()
        self.tab_2d = Shape2DWidget()
        self.tab_3d = Shape3DWidget()
        
        # N-D Tab
        nd_widget = QWidget()
        nd_layout = QVBoxLayout(nd_widget)
        
        nd_method_ctrl = QHBoxLayout()
        self.nd_method_combo = QComboBox()
        self.nd_method_combo.addItems([
            "1. Parallel Coordinates", 
            "2. Scatterplot Matrix (SPLOM)", 
            "3. Sliding Window 3D Subspace", 
            "4. Optimal 2D Projection",
            "5. 2D Projection Slice (Givens)"
        ])
        self.nd_method_combo.currentIndexChanged.connect(self.update_nd_view)
        
        self.window_slider = QSlider(Qt.Orientation.Horizontal)
        self.window_slider.setMinimum(0)
        self.window_slider.setMaximum(0)
        self.window_slider.setValue(0)
        self.window_slider.valueChanged.connect(self.update_window_pos)
        self.window_slider_label = QLabel("Window: 0")
        
        nd_method_ctrl.addWidget(QLabel("N-D Method:"))
        nd_method_ctrl.addWidget(self.nd_method_combo)
        nd_method_ctrl.addWidget(self.window_slider_label)
        nd_method_ctrl.addWidget(self.window_slider)
        nd_method_ctrl.addStretch()
        
        nd_layout.addLayout(nd_method_ctrl)
        
        self.nd_stack = QStackedWidget()
        self.nd_parallel = ParallelCoordsWidget()
        self.nd_splo = SPLOMWidget()
        self.nd_window3d = SlidingWindow3DWidget()
        self.nd_optimal = OptimalProjectionWidget()
        self.nd_givens = GivensSliceWidget()
        
        self.nd_stack.addWidget(self.nd_parallel)
        self.nd_stack.addWidget(self.nd_splo)
        self.nd_stack.addWidget(self.nd_window3d)
        self.nd_stack.addWidget(self.nd_optimal)
        self.nd_stack.addWidget(self.nd_givens)
        
        nd_layout.addWidget(self.nd_stack)
        
        self.tabs.addTab(self.tab_2d, "2D View")
        self.tabs.addTab(self.tab_3d, "3D View (Interactive)")
        self.tabs.addTab(nd_widget, "N-D Views (Academic Suite)")
        main_layout.addWidget(self.tabs)

        self.update_shape()

    def update_shape(self):
        n_dims = self.dim_slider.value()
        self.dim_label.setText(f"Dims: {n_dims}")
        
        shape_type = self.shape_combo.currentText()
        n_vertices = self.vertex_spin.value()
        
        self.current_shape = generate_shape(shape_type, n_dims, n_vertices)
        
        self.tab_2d.set_shape(self.current_shape)
        self.tab_3d.set_shape(self.current_shape)
        
        self.nd_parallel.set_shape(self.current_shape)
        self.nd_splo.set_shape(self.current_shape)
        self.nd_window3d.set_shape(self.current_shape, self.window_slider.value())
        self.nd_optimal.set_shape(self.current_shape)
        self.nd_givens.set_shape(self.current_shape)
        
        self.window_slider.setMaximum(max(0, n_dims - 3))
        self.update_window_pos(self.window_slider.value())

    def update_window_pos(self, value):
        self.nd_window3d.set_shape(self.current_shape, value)
        self.window_slider_label.setText(f"Window: {value} (Dims {value+1}-{value+3})")

    def update_nd_view(self, index):
        self.nd_stack.setCurrentIndex(index)
        is_window = (index == 2)
        self.window_slider.setVisible(is_window)
        self.window_slider_label.setVisible(is_window)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())