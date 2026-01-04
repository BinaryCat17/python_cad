import json
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QTreeWidget, QTreeWidgetItem, QHeaderView, QSplitter)
from PySide6.QtCore import Qt
from pyvistaqt import QtInteractor
from src.renderer import CADRenderer
from build123d import Shape, Compound

CONFIG_FILE = "config.json"

class CADMainWindow(QMainWindow):
    def __init__(self, assembly_class):
        super().__init__()
        self.setWindowTitle("Python CAD")
        
        # Load Config
        self.config = self._load_config()
        width = self.config.get("app", {}).get("window_width", 1280)
        height = self.config.get("app", {}).get("window_height", 800)
        self.resize(width, height)
        
        self.assembly = assembly_class()
        
        # Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 1. Scene Graph (Tree)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Item", "Type"])
        self.tree_widget.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree_widget.setFixedWidth(300)
        splitter.addWidget(self.tree_widget)
        
        # 2. 3D View
        self.interactor = QtInteractor(self)
        splitter.addWidget(self.interactor.interactor)
        splitter.setSizes([300, 980])
        
        # Renderer
        self.renderer = CADRenderer(self.interactor)
        
        # Build and Show
        self.refresh_view()
        self._restore_camera()

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_config(self):
        # Save window size
        if "app" not in self.config:
            self.config["app"] = {}
        self.config["app"]["window_width"] = self.width()
        self.config["app"]["window_height"] = self.height()
        
        # Save camera
        cam = self.interactor.camera
        self.config["camera"] = {
            "position": list(cam.position),
            "focal_point": list(cam.focal_point),
            "view_up": list(cam.up)
        }
        
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def _restore_camera(self):
        cam_cfg = self.config.get("camera")
        if cam_cfg:
            self.interactor.camera.position = cam_cfg.get("position", (100, 100, 100))
            self.interactor.camera.focal_point = cam_cfg.get("focal_point", (0, 0, 0))
            self.interactor.camera.up = cam_cfg.get("view_up", (0, 0, 1))
            self.interactor.render()

    def refresh_view(self):
        """Перестраивает модель и обновляет дерево."""
        try:
            # 1. Build
            root_compound = self.assembly.build()
            
            # 2. Render
            self.renderer.render_assembly(self.assembly) # Renderer expects assembly wrapper
            # Hack: modify renderer to accept root directly? 
            # Actually renderer calls assembly.build(). Let's keep it consistent.
            
            # 3. Update Tree
            self.tree_widget.clear()
            self._populate_tree(root_compound, self.tree_widget.invisibleRootItem())
            self.tree_widget.expandAll()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Build Error: {e}")

    def _populate_tree(self, node, parent_item):
        """Рекурсивно заполняет дерево."""
        if not isinstance(node, Shape):
            return

        label = getattr(node, "label", "Part")
        type_name = type(node).__name__
        
        item = QTreeWidgetItem(parent_item)
        item.setText(0, label)
        item.setText(1, type_name)
        
        # Recurse for children
        # In build123d, 'children' property usually holds the sub-shapes
        if hasattr(node, "children"):
             for child in node.children:
                 # Только если ребенок - это Shape
                 if isinstance(child, Shape):
                     self._populate_tree(child, item)

    def closeEvent(self, event):
        self._save_config()
        self.interactor.close()
        super().closeEvent(event)