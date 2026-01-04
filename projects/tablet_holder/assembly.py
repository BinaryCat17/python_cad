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
        config_path = os.path.join(os.path.dirname(__file__), "params.json")
        with open(config_path, "r") as f:
            self.params = json.load(f)

    def build(self) -> Compound:
        # 1. Создаем детали
        lp = build_holder_half(self.params, is_left=True)
        rp = build_holder_half(self.params, is_left=False)
        ap = build_adapter(self.params)

        # 2. ФИКСАЦИЯ ОСНОВЫ
        # Мы НЕ используем connect_to для половин, так как они строятся в 0,0,0.
        # Мы ПРИНУДИТЕЛЬНО обнуляем их трансформации.
        lp.location = Location((0, 0, 0))
        rp.location = Location((0, 0, 0))
        
        # 3. ПРИВЯЗКА АДАПТЕРА
        # Важно: мы перемещаем АДАПТЕР к ЛЕВОЙ ЧАСТИ.
        ap.joints["mount"].connect_to(lp.joints["adapter_mount"])

        # 4. Сборка
        lp.label, lp.color = "Left Half", "#2c3e50"
        rp.label, rp.color = "Right Half", "#5dade2"
        ap.label, ap.color = "VESA Adapter", "#e67e22"

        # Создаем финальный объект
        # В 0.10.0 порядок детей важен для отрисовки.
        root = Compound(label="Tablet Holder Assembly", children=[lp, rp, ap])
        return root
