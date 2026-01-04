from __future__ import annotations
from build123d import *
from parts.holder_half import build_holder_half
from parts.adapter import build_adapter

class TabletHolderAssembly:
    def __init__(self, **kwargs):
        self.params = {
            "tablet_w": 327.0,
            "tablet_h": 217.0,
            "tablet_t": 16.0,
            "wall": 8.0,
            "slot_t": 2.0,
            "visor_d": 50.0,
            "visor_angle": 20.0,
            "claw_grip": 15.0
        }
        self.params.update(kwargs)

    def get_parameters(self):
        return {
            "tablet_w": (200.0, 400.0, "Width"),
            "tablet_h": (150.0, 300.0, "Height"),
            "tablet_t": (5.0, 30.0, "Thickness"),
            "slot_t": (0.0, 10.0, "Clearance"),
            "wall": (5.0, 15.0, "Wall"),
            "visor_d": (10.0, 150.0, "Hood Depth"),
            "visor_angle": (0.0, 45.0, "Hood Angle"),
            "claw_grip": (5.0, 30.0, "Claw Grip")
        }

    def build(self) -> Compound:
        # 1. Создаем детали
        left_part = build_holder_half(**self.params, is_left=True)
        right_part = build_holder_half(**self.params, is_left=False)
        adapter_part = build_adapter(w=120, h=120, t=8, hole_dist=100)

        # 2. Метаданные
        left_part.label = "left_half"
        left_part.color = "#2c3e50"
        
        right_part.label = "right_half"
        right_part.color = "#5dade2"
        
        adapter_part.label = "vesa_adapter"
        adapter_part.color = "#e67e22"

        # 3. Позиционирование
        # Половины уже стоят на месте (относительно X=0).
        # Соединяем адаптер К холдеру. adapter_part переместится.
        adapter_part.joints["mount"].connect_to(left_part.joints["adapter_mount"])

        # 4. Итоговая сборка
        root = Compound(label="tablet_holder", children=[left_part, right_part, adapter_part])
        
        # anytree hierarchy
        left_part.parent = root
        right_part.parent = root
        adapter_part.parent = root
        
        return root
