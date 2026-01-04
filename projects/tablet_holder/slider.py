from __future__ import annotations
from build123d import *

def build_slider(params: dict) -> Part:
    """Строит монолитный слайдер с глубокой интеграцией узлов."""
    wall = params["wall"]
    tt = params["tablet_t"]
    st = params.get("slider_front_t", 6.0)
    sw = params.get("slider_f_width", 140.0) # 140мм
    
    with BuildPart() as obj:
        # 1. Передний блок (Лапа + блок в пазу)
        with BuildSketch(Plane.YZ) as s1:
            with BuildLine():
                p1 = (0, st + 14)
                p2 = (-6, st + 14)
                p3 = (-6, st)
                p4 = (-60, st)
                p5 = (-60, 0)
                p6 = (0, 0)
                Polyline(p1, p2, p3, p4, p5, p6, close=True)
            make_face()
        extrude(amount=sw/2, both=True)

        # 2. Шейка (Neck)
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ) as s2:
                 Rectangle(60, wall + 4, align=(Align.MAX, Align.CENTER))
                 fillet(s2.vertices(), radius=2)
            extrude(amount=108/2, both=True)

        # 3. Задняя плита (Back Plate)
        with BuildPart(mode=Mode.ADD):
            with BuildSketch(Plane.YZ) as s3:
                with BuildLine():
                    p1 = (0, -wall)
                    p2 = (0, -wall-6)
                    p3 = (-65, -wall-6)
                    p4 = (-65, -wall)
                    Polyline(p1, p2, p3, p4, close=True)
                make_face()
            extrude(amount=160/2, both=True)

        # 4. Отверстия под болты-анкеры
        # Болты на x = +/- 50мм.
        with BuildPart(mode=Mode.SUBTRACT):
            # Отверстия на Y = -30 (середина шейки)
            # Центр отверстий по Z (мировой) = -wall/2
            with Locations(Plane.XY.offset(-wall/2) * Location((0, -30, 0))):
                for x_pos in [-50, 50]:
                    with Locations((x_pos, 0, 0)):
                        Cylinder(radius=5.5/2, height=40, align=Align.CENTER)

        RigidJoint("mount", obj.part, Location((0, 0, 0)))
    
    return obj.part