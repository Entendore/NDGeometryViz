import sys
import math
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTabWidget, QSlider, QLabel, QPushButton, 
                               QSizePolicy, QComboBox, QStackedWidget, QSpinBox)
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QFont
from PySide6.QtCore import Qt, QPoint, QPointF

# --- Utility Functions ---
def rotate_x(point, angle):
    x, y, z = point
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return [x, y * cos_a - z * sin_a, y * sin_a + z * cos_a]

def rotate_y(point, angle):
    x, y, z = point
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return [x * cos_a + z * sin_a, y, -x * sin_a + z * cos_a]

def generate_triangle_2d():
    return [[-50, -50], [50, -50], [0, 50]]

def generate_triangle_3d():
    return [[-50, -50, -50], [50, -50, 0], [0, 50, 50]]

def generate_triangle_nd(n_dims):
    return [[random.uniform(-100, 100) for _ in range(n_dims)] for _ in range(3)]

# --- 2D & 3D Widgets (Unchanged) ---
class Triangle2DWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.vertices = generate_triangle_2d()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        painter.translate(cx, cy)
        
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.PenStyle.DotLine))
        for i in range(-200, 201, 50):
            painter.drawLine(i, -200, i, 200)
            painter.drawLine(-200, i, 200, i)
            
        painter.setPen(QPen(QColor(30, 144, 255), 3))
        painter.setBrush(QBrush(QColor(30, 144, 255, 50)))
        painter.drawPolygon([QPointF(v[0], v[1]) for v in self.vertices])
        
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        for v in self.vertices:
            painter.drawEllipse(QPointF(v[0], v[1]), 5, 5)
        painter.end()

class Triangle3DWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.vertices = generate_triangle_3d()
        self.rot_x_angle = 0.5
        self.rot_y_angle = 0.5
        self.last_pos = QPoint()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def mousePressEvent(self, event): self.last_pos = event.pos()
    def mouseMoveEvent(self, event):
        dx = event.pos().x() - self.last_pos.x()
        dy = event.pos().y() - self.last_pos.y()
        self.rot_y_angle += dx * 0.01
        self.rot_x_angle += dy * 0.01
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

        transformed = [rotate_y(rotate_x(v, self.rot_x_angle), self.rot_y_angle) for v in self.vertices]

        painter.setPen(QPen(QColor(150, 150, 150), 1, Qt.PenStyle.DashLine))
        origin = self.project_3d_to_2d([0,0,0])
        for axis, color in [([100,0,0], Qt.red), ([0,100,0], Qt.green), ([0,0,100], Qt.blue)]:
            painter.setPen(QPen(color, 2))
            painter.drawLine(origin, self.project_3d_to_2d(axis))

        painter.setPen(QPen(QColor(255, 100, 0), 3))
        painter.setBrush(QBrush(QColor(255, 100, 0, 60)))
        projected_points = [self.project_3d_to_2d(v) for v in transformed]
        painter.drawPolygon(projected_points)

        painter.setBrush(QBrush(QColor(0, 100, 200)))
        for p in projected_points: painter.drawEllipse(p, 6, 6)
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 10))
        painter.drawText(10, 20, "Click and drag to rotate")
        painter.end()

# --- Academic N-D Visualization Methods ---

class ParallelCoordsWidget(QWidget):
    def __init__(self, n_dims=5):
        super().__init__()
        self.n_dims = n_dims
        self.vertices = generate_triangle_nd(self.n_dims)
        self.colors = [QColor(255, 99, 71), QColor(46, 139, 87), QColor(70, 130, 180)]

    def set_data(self, vertices, n_dims):
        self.vertices, self.n_dims = vertices, n_dims
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)
        if self.n_dims < 2: return

        margin, w, h = 50, self.width() - 100, self.height() - 100
        mins = [min(v[i] for v in self.vertices) for i in range(self.n_dims)]
        maxs = [max(v[i] for v in self.vertices) for i in range(self.n_dims)]
        for i in range(self.n_dims):
            if mins[i] == maxs[i]: maxs[i] += 1

        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setFont(QFont("Arial", 10))
        axis_spacing = w / (self.n_dims - 1) if self.n_dims > 1 else 0
        
        for i in range(self.n_dims):
            x = margin + i * axis_spacing
            painter.drawLine(QPointF(x, margin), QPointF(x, margin + h))
            painter.drawText(QPointF(x - 10, margin + h + 20), f"Dim {i+1}")

        for i in range(3):
            v, v_next = self.vertices[i], self.vertices[(i + 1) % 3]
            painter.setPen(QPen(self.colors[i], 4))
            for d in range(self.n_dims - 1):
                y1 = margin + h - ((v[d] - mins[d]) / (maxs[d] - mins[d]) * h)
                y2 = margin + h - ((v_next[d+1] - mins[d+1]) / (maxs[d+1] - mins[d+1]) * h)
                painter.drawLine(QPointF(margin + d * axis_spacing, y1), QPointF(margin + (d + 1) * axis_spacing, y2))

        for i in range(3):
            painter.setBrush(QBrush(self.colors[i]))
            painter.setPen(QPen(Qt.black, 1))
            for d in range(self.n_dims):
                y = margin + h - ((self.vertices[i][d] - mins[d]) / (maxs[d] - mins[d]) * h)
                painter.drawEllipse(QPointF(margin + d * axis_spacing, y), 5, 5)
        painter.end()

class SPLOMWidget(QWidget):
    def __init__(self, n_dims=5):
        super().__init__()
        self.n_dims = n_dims
        self.vertices = generate_triangle_nd(self.n_dims)
        self.colors = [QColor(255, 99, 71), QColor(46, 139, 87), QColor(70, 130, 180)]

    def set_data(self, vertices, n_dims):
        self.vertices, self.n_dims = vertices, n_dims
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)
        if self.n_dims < 2: return

        margin, w, h = 40, self.width() - 80, self.height() - 80
        cell_w, cell_h = w / self.n_dims, h / self.n_dims

        mins = [min(v[i] for v in self.vertices) for i in range(self.n_dims)]
        maxs = [max(v[i] for v in self.vertices) for i in range(self.n_dims)]
        for i in range(self.n_dims):
            if mins[i] == maxs[i]: maxs[i] += 1

        painter.setFont(QFont("Arial", 8))
        for i in range(self.n_dims):
            for j in range(self.n_dims):
                x0, y0 = margin + j * cell_w, margin + i * cell_h
                painter.setPen(QPen(QColor(220, 220, 220), 1))
                painter.drawRect(QPointF(x0, y0), cell_w, cell_h)

                if i == j:
                    painter.setPen(Qt.black)
                    painter.drawText(QPointF(x0 + cell_w/2 - 15, y0 + cell_h/2), f"Dim {i+1}")
                else:
                    for k in range(3):
                        v1, v2 = self.vertices[k], self.vertices[(k+1)%3]
                        x1_n = (v1[j] - mins[j]) / (maxs[j] - mins[j])
                        y1_n = (v1[i] - mins[i]) / (maxs[i] - mins[i])
                        x2_n = (v2[j] - mins[j]) / (maxs[j] - mins[j])
                        y2_n = (v2[i] - mins[i]) / (maxs[i] - mins[i])
                        
                        painter.setPen(QPen(self.colors[k], 2))
                        painter.drawLine(QPointF(x0 + x1_n*cell_w, y0 + (1-y1_n)*cell_h), 
                                         QPointF(x0 + x2_n*cell_w, y0 + (1-y2_n)*cell_h))

                    for k in range(3):
                        v = self.vertices[k]
                        px = x0 + ((v[j] - mins[j]) / (maxs[j] - mins[j])) * cell_w
                        py = y0 + (1 - (v[i] - mins[i]) / (maxs[i] - mins[i])) * cell_h
                        painter.setBrush(QBrush(self.colors[k]))
                        painter.setPen(QPen(Qt.black, 1))
                        painter.drawEllipse(QPointF(px, py), 3, 3)
        painter.end()

class SlidingWindow3DWidget(QWidget):
    def __init__(self, n_dims=5):
        super().__init__()
        self.n_dims = n_dims
        self.vertices = generate_triangle_nd(self.n_dims)
        self.window_start = 0
        self.rot_x_angle = 0.5
        self.rot_y_angle = 0.5
        self.last_pos = QPoint()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_data(self, vertices, n_dims, window_start):
        self.vertices, self.n_dims = vertices, n_dims
        self.window_start = min(window_start, max(0, self.n_dims - 3))
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

        if self.n_dims < 3:
            painter.setPen(Qt.red)
            painter.drawText(50, 50, "Need at least 3 dimensions for 3D window.")
            painter.end()
            return

        w_start = self.window_start
        transformed = []
        for v in self.vertices:
            p = [v[w_start] * 0.5, v[w_start+1] * 0.5, v[w_start+2] * 0.5]
            transformed.append(rotate_y(rotate_x(p, self.rot_x_angle), self.rot_y_angle))

        painter.setPen(QPen(QColor(150, 150, 150), 1, Qt.PenStyle.DashLine))
        origin = self.project_3d_to_2d([0,0,0])
        for axis, color in [([100,0,0], Qt.red), ([0,100,0], Qt.green), ([0,0,100], Qt.blue)]:
            painter.setPen(QPen(color, 2))
            painter.drawLine(origin, self.project_3d_to_2d(axis))

        painter.setPen(QPen(QColor(255, 100, 0), 3))
        painter.setBrush(QBrush(QColor(255, 100, 0, 60)))
        projected_points = [self.project_3d_to_2d(v) for v in transformed]
        painter.drawPolygon(projected_points)

        painter.setBrush(QBrush(QColor(0, 100, 200)))
        for p in projected_points: painter.drawEllipse(p, 6, 6)

        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 10))
        painter.drawText(10, 20, f"Subspace: Dim {w_start+1}, {w_start+2}, {w_start+3}")
        painter.drawText(10, 40, "Click and drag to rotate")
        painter.end()

class OptimalProjectionWidget(QWidget):
    def __init__(self, n_dims=5):
        super().__init__()
        self.n_dims = n_dims
        self.vertices = generate_triangle_nd(self.n_dims)

    def set_data(self, vertices, n_dims):
        self.vertices, self.n_dims = vertices, n_dims
        self.update()

    def get_2d_projection(self):
        v0, v1, v2 = self.vertices
        u1 = [v1[i] - v0[i] for i in range(self.n_dims)]
        u2 = [v2[i] - v0[i] for i in range(self.n_dims)]
        
        norm_u1 = math.sqrt(sum(x*x for x in u1)) or 1
        e1 = [x / norm_u1 for x in u1]
        
        dot_u2_e1 = sum(u2[i] * e1[i] for i in range(self.n_dims))
        u2_orth = [u2[i] - dot_u2_e1 * e1[i] for i in range(self.n_dims)]
        
        norm_u2 = math.sqrt(sum(x*x for x in u2_orth)) or 1
        e2 = [x / norm_u2 for x in u2_orth]
        
        return [
            [0.0, 0.0], 
            [norm_u1, 0.0], 
            [dot_u2_e1, sum(u2[i] * e2[i] for i in range(self.n_dims))]
        ]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)

        proj_verts = self.get_2d_projection()
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

        painter.setPen(QPen(QColor(138, 43, 226), 3))
        painter.setBrush(QBrush(QColor(138, 43, 226, 50)))
        painter.drawPolygon([to_screen(v) for v in proj_verts])

        painter.setBrush(QBrush(QColor(255, 215, 0)))
        for v in proj_verts: painter.drawEllipse(to_screen(v), 6, 6)

        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 10))
        painter.drawText(10, 20, "Optimal 2D Projection (PCA/MDS equivalent)")
        painter.drawText(10, 40, "Preserves exact N-D edge lengths and angles.")
        
        painter.setFont(QFont("Arial", 9))
        painter.setPen(QColor(100, 100, 100))
        for i in range(3):
            p1, p2 = to_screen(proj_verts[i]), to_screen(proj_verts[(i+1)%3])
            mid = QPointF((p1.x()+p2.x())/2, (p1.y()+p2.y())/2)
            dist = math.sqrt(sum((self.vertices[i][k]-self.vertices[(i+1)%3][k])**2 for k in range(self.n_dims)))
            painter.drawText(mid + QPointF(5, -5), f"L={dist:.1f}")
        painter.end()

# --- NEW: 2D Projection Slice via Givens Rotations ---
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
        
        if self.parent_widget.n_dims < 2:
            painter.setPen(Qt.red)
            painter.drawText(50, 50, "Need at least 2 dimensions.")
            painter.end()
            return
            
        # Project onto the first two dimensions (Dim 1 & Dim 2)
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
        
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 10))
        painter.drawText(10, 20, "2D Projection Slice (Dims 1 & 2)")
        painter.drawText(10, 40, "Drag slider to preview rotation, click 'Apply' to commit.")
        
        painter.setPen(QPen(QColor(220, 20, 60), 3))
        painter.setBrush(QBrush(QColor(220, 20, 60, 50)))
        screen_verts = [to_screen(v) for v in proj_verts]
        painter.drawPolygon(screen_verts)
        
        painter.setBrush(QBrush(QColor(0, 0, 139)))
        for p in screen_verts:
            painter.drawEllipse(p, 6, 6)
            
        painter.end()

class GivensSliceWidget(QWidget):
    def __init__(self, n_dims=5):
        super().__init__()
        self.n_dims = n_dims
        self.original_vertices = generate_triangle_nd(self.n_dims)
        self.base_vertices = [v[:] for v in self.original_vertices]
        self.vertices = [v[:] for v in self.original_vertices]
        
        layout = QVBoxLayout(self)
        
        self.canvas = SliceCanvas(self)
        self.canvas.setMinimumHeight(400)
        layout.addWidget(self.canvas, 1)
        
        ctrl_layout = QHBoxLayout()
        
        self.spin_i = QSpinBox()
        self.spin_i.setMinimum(1)
        self.spin_i.setMaximum(self.n_dims)
        self.spin_i.setValue(1)
        self.spin_i.valueChanged.connect(self.update_temporary_rotation)
        
        self.spin_j = QSpinBox()
        self.spin_j.setMinimum(1)
        self.spin_j.setMaximum(self.n_dims)
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

    def on_theta_changed(self, val):
        self.theta_label.setText(f"θ: {val}°")
        self.update_temporary_rotation()

    def update_temporary_rotation(self):
        # Reset to the last committed state
        self.vertices = [v[:] for v in self.base_vertices]
        i = self.spin_i.value() - 1
        j = self.spin_j.value() - 1
        
        # Apply the temporary Givens rotation for preview
        if i != j and 0 <= i < self.n_dims and 0 <= j < self.n_dims:
            theta = math.radians(self.slider_theta.value())
            cos_t, sin_t = math.cos(theta), math.sin(theta)
            for v in self.vertices:
                vi, vj = v[i], v[j]
                v[i] = vi * cos_t - vj * sin_t
                v[j] = vi * sin_t + vj * cos_t
        self.canvas.update()

    def apply_rotation(self):
        # Commit the current state as the new base
        self.base_vertices = [v[:] for v in self.vertices]
        self.slider_theta.setValue(0)
        self.update_temporary_rotation()

    def reset_orientation(self):
        self.base_vertices = [v[:] for v in self.original_vertices]
        self.slider_theta.setValue(0)
        self.update_temporary_rotation()

    def set_data(self, vertices, n_dims):
        self.n_dims = n_dims
        self.original_vertices = [v[:] for v in vertices]
        self.base_vertices = [v[:] for v in vertices]
        self.vertices = [v[:] for v in vertices]
        
        self.spin_i.setMaximum(n_dims)
        self.spin_j.setMaximum(n_dims)
        if self.spin_i.value() > n_dims: self.spin_i.setValue(1)
        if self.spin_j.value() > n_dims: self.spin_j.setValue(2)
        
        self.slider_theta.setValue(0)
        self.canvas.update()

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Academic Triangle Visualizer: 2D, 3D, and N-D")
        self.resize(1000, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        self.tab_2d = Triangle2DWidget()
        self.tab_3d = Triangle3DWidget()
        
        nd_widget = QWidget()
        nd_layout = QVBoxLayout(nd_widget)
        
        ctrl_layout = QHBoxLayout()
        self.nd_method_combo = QComboBox()
        self.nd_method_combo.addItems([
            "1. Parallel Coordinates (Standard)", 
            "2. Scatterplot Matrix (SPLOM)", 
            "3. Sliding Window 3D Subspace", 
            "4. Optimal 2D Projection (PCA/MDS)",
            "5. 2D Projection Slice (Givens Rotations)"
        ])
        self.nd_method_combo.currentIndexChanged.connect(self.update_nd_view)
        
        self.nd_slider = QSlider(Qt.Orientation.Horizontal)
        self.nd_slider.setMinimum(3)
        self.nd_slider.setMaximum(15)
        self.nd_slider.setValue(5)
        self.nd_slider.valueChanged.connect(self.generate_new_nd_data)
        
        self.window_slider = QSlider(Qt.Orientation.Horizontal)
        self.window_slider.setMinimum(0)
        self.window_slider.setMaximum(2)
        self.window_slider.setValue(0)
        self.window_slider.valueChanged.connect(self.update_window_pos)
        self.window_slider_label = QLabel("Window Start: 0")
        
        self.btn_randomize = QPushButton("Randomize All")
        self.btn_randomize.clicked.connect(self.randomize_all)
        
        ctrl_layout.addWidget(QLabel("Method:"))
        ctrl_layout.addWidget(self.nd_method_combo)
        ctrl_layout.addWidget(QLabel("N-Dims:"))
        ctrl_layout.addWidget(self.nd_slider)
        ctrl_layout.addWidget(self.window_slider_label)
        ctrl_layout.addWidget(self.window_slider)
        ctrl_layout.addWidget(self.btn_randomize)
        ctrl_layout.addStretch()
        
        nd_layout.addLayout(ctrl_layout)
        
        self.nd_stack = QStackedWidget()
        self.nd_parallel = ParallelCoordsWidget(n_dims=5)
        self.nd_splo = SPLOMWidget(n_dims=5)
        self.nd_window3d = SlidingWindow3DWidget(n_dims=5)
        self.nd_optimal = OptimalProjectionWidget(n_dims=5)
        self.nd_givens = GivensSliceWidget(n_dims=5)
        
        self.nd_stack.addWidget(self.nd_parallel)
        self.nd_stack.addWidget(self.nd_splo)
        self.nd_stack.addWidget(self.nd_window3d)
        self.nd_stack.addWidget(self.nd_optimal)
        self.nd_stack.addWidget(self.nd_givens)
        
        nd_layout.addWidget(self.nd_stack)
        
        self.tabs.addTab(self.tab_2d, "2D Triangle")
        self.tabs.addTab(self.tab_3d, "3D Triangle (Interactive)")
        self.tabs.addTab(nd_widget, "N-D Triangle (Academic Suite)")
        main_layout.addWidget(self.tabs)

        self.current_n_dims = 5
        self.current_nd_vertices = generate_triangle_nd(self.current_n_dims)
        self.update_nd_views()
        self.update_nd_view(0)

    def generate_new_nd_data(self):
        self.current_n_dims = self.nd_slider.value()
        self.current_nd_vertices = generate_triangle_nd(self.current_n_dims)
        self.window_slider.setMaximum(max(0, self.current_n_dims - 3))
        self.window_slider.setValue(0)
        self.update_nd_views()

    def update_nd_views(self):
        v, n = self.current_nd_vertices, self.current_n_dims
        w_start = self.window_slider.value()
        
        self.nd_parallel.set_data(v, n)
        self.nd_splo.set_data(v, n)
        self.nd_window3d.set_data(v, n, w_start)
        self.nd_optimal.set_data(v, n)
        self.nd_givens.set_data(v, n)
        
        self.window_slider_label.setText(f"Window Start: {w_start} (Dims {w_start+1}-{w_start+3})")

    def update_window_pos(self, value):
        self.nd_window3d.set_data(self.current_nd_vertices, self.current_n_dims, value)
        self.window_slider_label.setText(f"Window Start: {value} (Dims {value+1}-{value+3})")

    def update_nd_view(self, index):
        self.nd_stack.setCurrentIndex(index)
        is_window = (index == 2)
        self.window_slider.setVisible(is_window)
        self.window_slider_label.setVisible(is_window)

    def randomize_all(self):
        self.tab_2d.vertices = generate_triangle_2d()
        self.tab_2d.update()
        self.tab_3d.vertices = generate_triangle_3d()
        self.tab_3d.update()
        self.generate_new_nd_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())