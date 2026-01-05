from __future__ import annotations
from build123d import *

def build_slider(params: dict) -> Part:
    """Строит монолитный слайдер с усиленной Г-образной платформой."""
    wall, tt = params["wall"], params["tablet_t"]
    st, sw = params.get("slider_front_t", 6.0), params.get("slider_f_width", 140.0)
    
    # Планшет (18мм) начинается от Z=st (6.0)
    tablet_front_z = st + tt
    
    with BuildPart() as obj:
        # 1. Передняя панель + Зацеп (в передней выемке st)
        # Z: 0...st (в координатах джойнта, что соответствует 8...14 в корпусе)
        with BuildSketch(Plane.YZ) as s1:
            with BuildLine() as bl:
                # Y - вертикаль, Z - глубина
                p1 = (0, 0)
                p2 = (-60, 0)
                p3 = (-60, st)
                # Заменяем p4 на "косынку" p4a -> p4b
                p4a = (-40, st) 
                p4b = (-15, st + 20) # Уменьшили высоту, чтобы не конфликтовать с p5
                p5 = (-10, tablet_front_z + 12)
                p6 = (20, tablet_front_z + 16)
                p7 = (20, tablet_front_z + 4)
                p8 = (0, tablet_front_z)
                
                Polyline(p1, p2, p3, p4a, p4b, p5, p6, p7, p8, close=True)
                
                # Используем детерминированный подход из holder_half
                def get_closest(pts, target):
                    return sorted(pts, key=lambda p: (p.X - target[0])**2 + (p.Y - target[1])**2)[0]
                
                # Скругляем углы косынки для плавности и прочности
                fillet(get_closest(bl.vertices(), p4a), radius=10.0)
                fillet(get_closest(bl.vertices(), p4b), radius=25.0)
                fillet(get_closest(bl.vertices(), p5), radius=5.0)
                fillet(get_closest(bl.vertices(), p6), radius=5.0)
                fillet(get_closest(bl.vertices(), p7), radius=5.0)
                fillet(get_closest(bl.vertices(), p8), radius=10.0)
            make_face()
        extrude(amount=sw/2, both=True)

        # 2. Шейка (Neck) - должна быть в толщине основной стенки (wall)
        # Z: -wall...0 (соответствует 0...8 в корпусе)
        with BuildPart(mode=Mode.ADD):
            with Locations((0, -30, -wall/2)):
                Box(108, 60, wall)

        # 3. Задняя плита (Back Plate) - должна быть ЗА корпусом
        # Z: -(wall+6)...-wall (соответствует -6...0 в мировых координатах)
        with BuildPart(mode=Mode.ADD):
            with Locations((0, -32.5, -wall - 3)):
                Box(170, 65, 6)

        # 4. Отверстия под болты (смещены на 20мм ниже для прочности)
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Plane.XY.offset(-wall/2) * Location((0, -50, 0))):
                for x_pos in [-50, 50]:
                    with Locations((x_pos, 0, 0)):
                        Cylinder(radius=5.5/2, height=40, align=Align.CENTER)

        RigidJoint("mount", obj.part, Location((0, 0, 0)))
    
    return obj.part
