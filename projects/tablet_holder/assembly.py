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

        # 2. ПОЗИЦИОНИРОВАНИЕ (БЕЗ МАГИИ)
        # Половины строго в нуле.
        lp.location = Location((0, 0, 0))
        rp.location = Location((0, 0, 0))
        
        # Адаптер: совмещаем его джойнт "mount" с джойнтом "adapter_mount" левой части.
        # Вместо connect_to, который может двигать lp, мы сами вычисляем позицию ap.
        # ap.location = lp.location * lp_joint_loc * ap_joint_loc_inv
        
        target_loc = lp.location * lp.joints["adapter_mount"].location * ap.joints["mount"].location.inverse()
        ap.location = target_loc

        # 3. Сборка
        lp.label, lp.color = "Left Half", "#2c3e50"
        rp.label, rp.color = "Right Half", "#5dade2"
        ap.label, ap.color = "VESA Adapter", "#e67e22"

        root = Compound(label="Tablet Holder Assembly", children=[lp, rp, ap])
        return root
