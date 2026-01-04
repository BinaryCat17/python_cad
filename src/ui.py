import json
import os
import sys
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
        
        # Load Application Config
        self.config = self._load_config()
        width = self.config.get("app", {}).get("window_width", 1280)
        height = self.config.get("app", {}).get("window_height", 800)
        self.resize(width, height)
        
        # Initialize Project
        self.assembly_class = assembly_class
        self.params = self._load_project_params(assembly_class)
        self.assembly = assembly_class(self.params)
        
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
        self.tree_widget.itemChanged.connect(self._on_item_changed)
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

    def _load_project_params(self, assembly_class):
        """Загружает параметры проекта из params.json в папке проекта."""
        try:
            # Пытаемся найти params.json в той же папке, где определен класс сборки
            module_path = sys.modules[assembly_class.__module__].__file__
            project_dir = os.path.dirname(module_path)
            params_path = os.path.join(project_dir, "params.json")
            
            if os.path.exists(params_path):
                with open(params_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load project params: {e}")
        return {}

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
            # 1. Build (теперь возвращает список деталей)
            parts = self.assembly.build()
            if not isinstance(parts, list):
                parts = [parts]
            
            # 2. Render and get actor names
            actor_groups = self.renderer.update_scene(parts)
            
            # 3. Update Tree
            self.tree_widget.blockSignals(True) # Предотвращаем срабатывание при заполнении
            self.tree_widget.clear()
            for i, part in enumerate(parts):
                item = self._populate_tree(part, self.tree_widget.invisibleRootItem())
                if item and i < len(actor_groups):
                    # Сохраняем список имен акторов в элементе дерева
                    item.setData(0, Qt.UserRole, actor_groups[i])
                    item.setCheckState(0, Qt.Checked)
            self.tree_widget.expandAll()
            self.tree_widget.blockSignals(False)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Build Error: {e}")

    def _on_item_changed(self, item, column):
        """Обработка изменения состояния чекбокса."""
        if column == 0:
            visible = item.checkState(0) == Qt.Checked
            actor_names = item.data(0, Qt.UserRole)
            if actor_names:
                for name in actor_names:
                    if name in self.interactor.renderer.actors:
                        self.interactor.renderer.actors[name].SetVisibility(visible)
                self.interactor.render()

    def _populate_tree(self, node, parent_item):
        """Рекурсивно заполняет дерево. Возвращает созданный элемент."""
        if not isinstance(node, Shape):
            return None

        label = getattr(node, "label", "Part")
        type_name = type(node).__name__
        
        item = QTreeWidgetItem(parent_item)
        item.setText(0, label)
        item.setText(1, type_name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(0, Qt.Checked)
        
        # Если это Compound (вложенный), обходим его детей
        if isinstance(node, Compound):
            try:
                for i, child in enumerate(node):
                    if isinstance(child, Shape):
                        self._populate_tree(child, item)
            except:
                pass
        
        return item

    def closeEvent(self, event):
        self._save_config()
        self.interactor.close()
        super().closeEvent(event)