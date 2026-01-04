from __future__ import annotations
import json
import os
from build123d import *
from .holder_half import build_holder_half
from .adapter import build_adapter

class ProjectAssembly:
    def __init__(self, params: dict = None):
        self.params = params if params else {}

    def build(self) -> list[Shape]:
        # 1. Создаем детали
        lp = build_holder_half(self.params, is_left=True)
        rp = build_holder_half(self.params, is_left=False)
        ap = build_adapter(self.params)

        # 2. ЯВНОЕ ПОЗИЦИОНИРОВАНИЕ
        lp.location = Location((0, 0, 0))
        rp.location = Location((0, 0, 0))
        ap.location = lp.location * lp.joints["adapter_mount"].location * ap.joints["mount"].location.inverse()
        
        lp.label, lp.color = "Left Half", "#2c3e50"
        rp.label, rp.color = "Right Half", "#5dade2"
        ap.label, ap.color = "VESA Adapter", "#e67e22"

        # Возвращаем список деталей для сохранения атрибутов
        return [lp, rp, ap]
