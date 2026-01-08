from __future__ import annotations
import json
import os
from build123d import *
from .holder_half import build_holder_half
from .adapter import build_adapter
from .slider import build_slider

class ProjectAssembly:
    def __init__(self, params: dict = None):
        self.params = params if params else {}

    def build(self) -> list[Shape]:
        # 1. Создаем детали (4 четверти)
        lpt = build_holder_half(self.params, is_left=True, segment="top")
        lpb = build_holder_half(self.params, is_left=True, segment="bottom")
        rpt = build_holder_half(self.params, is_left=False, segment="top")
        rpb = build_holder_half(self.params, is_left=False, segment="bottom")
        
        ap = build_adapter(self.params)
        sp = build_slider(self.params)

        # 2. Позиционирование (возвращаем в 0,0,0)
        for p in [lpt, lpb, rpt, rpb]:
            p.location = Location((0, 0, 0))

        # Позиционируем адаптер и слайдер
        ap.location = lpt.location * lpt.joints["adapter_mount"].location * ap.joints["mount"].location.inverse()
        offset_y = self.params.get("slider_offset", 0.0)
        sp.location = lpb.location * lpb.joints["slider_start"].location * Pos(0, offset_y, 0)
        
        lpt.label, lpt.color = "Left Top", "#2c3e50"
        lpb.label, lpb.color = "Left Bottom", "#34495e"
        rpt.label, rpt.color = "Right Top", "#5dade2"
        rpb.label, rpb.color = "Right Bottom", "#3498db"
        
        ap.label, ap.color = "VESA Adapter", "#e67e22"
        sp.label, sp.color = "Spring Slider", "#95a5a6"

        # Возвращаем список деталей
        return [lpt, lpb, rpt, rpb, ap, sp]
