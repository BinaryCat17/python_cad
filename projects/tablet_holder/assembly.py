from __future__ import annotations
import json
import os
from build123d import *
from .holder_half import build_holder_half
from .adapter import build_adapter

class ProjectAssembly:
    def __init__(self):
        self.params = {}
        self.load_config()

    def load_config(self):
        """Загружает параметры из params.json. Ошибка если файла нет."""
        config_path = os.path.join(os.path.dirname(__file__), "params.json")
        if not os.path.exists(config_path):
             raise FileNotFoundError(f"Configuration file not found: {config_path}")
             
        with open(config_path, "r") as f:
            self.params = json.load(f)

    def build(self) -> Compound:
        """Строит сборку."""
        # 1. Build Parts (передаем весь словарь params)
        left_part = build_holder_half(self.params, is_left=True)
        right_part = build_holder_half(self.params, is_left=False)
        adapter_part = build_adapter(self.params)

        # 2. Metadata
        left_part.label = "Left Half"
        left_part.color = "#2c3e50"
        
        right_part.label = "Right Half"
        right_part.color = "#5dade2"
        
        adapter_part.label = "VESA Adapter"
        adapter_part.color = "#e67e22"

        # 3. Connect
        adapter_part.joints["mount"].connect_to(left_part.joints["adapter_mount"])

        # 4. Hierarchy
        root = Compound(label="Tablet Holder Assembly", children=[left_part, right_part, adapter_part])
        left_part.parent = root
        right_part.parent = root
        adapter_part.parent = root
        
        return root
