from __future__ import annotations
from build123d import *

def build_holder_half(params: dict, is_left: bool = True) -> Part:
    """Строит половину корпуса."""
    
    tablet_w = params["tablet_w"]
    tablet_h = params["tablet_h"]
    tablet_t = params["tablet_t"]
    wall = params["wall"]
    slot_t = params["slot_t"]
    visor_d = params["visor_d"]
    visor_angle = params["visor_angle"]
    claw_grip = params["claw_grip"]
    adapter_size = params.get("adapter_w", 120.0) # Тут можно оставить get если параметр общий
    hole_dist = params.get("adapter_hole_dist", 100.0)
    
    total_w = tablet_w + wall * 2
    half_w = total_w / 2
    total_h = tablet_h + wall * 2
    
    x_min = -half_w if is_left else 0
    x_max = 0 if is_left else half_w
    center_x = (x_min + x_max) / 2
    side_x = -half_w if is_left else half_w - wall

    with BuildPart() as obj:
        # 1. Backplate
        with Locations((center_x, 0, wall/2)):
            Box(half_w, total_h, wall)
        
        # 2. Side Wall
        with Locations((side_x + wall/2, 0, wall + tablet_t/2)):
            Box(wall, total_h, tablet_t)
        
        # Claw
        claw_width = wall + claw_grip
        claw_center_x = side_x + claw_width/2 if is_left else side_x + wall - claw_width/2
        with Locations((claw_center_x, 0, wall + tablet_t + wall/2)):
            Box(claw_width, total_h, wall)

        # 3. Rails
        for y_pos in [-total_h/2 + wall/2, total_h/2 - wall/2]:
            with Locations((center_x, y_pos, wall + tablet_t/2)):
                Box(half_w, wall, tablet_t)
            with Locations((center_x, y_pos, wall + tablet_t + wall/2)):
                Box(half_w, wall, wall)

        # 4. Hood
        with Locations((center_x, total_h/2 - wall/2, wall + tablet_t + wall)):
            with Locations(Rotation(visor_angle, 0, 0)):
                Box(half_w, wall, visor_d, align=(Align.CENTER, Align.CENTER, Align.MIN))
        
        # 5. Adapter Recess (Only on backplate Z=0)
        recess_align_x = Align.MAX if is_left else Align.MIN
        with Locations((0, 0, 0)):
            Box(adapter_size/2 + 0.5, adapter_size + 1.0, 3.0, 
                align=(recess_align_x, Align.CENTER, Align.MIN), 
                mode=Mode.SUBTRACT)

        # 6. Mounting Holes
        x_hole = hole_dist / 2
        hole_y_coords = [-hole_dist/2, hole_dist/2]
        for y_h in hole_y_coords:
            h_x = -x_hole if is_left else x_hole
            with Locations((h_x, y_h, 0)):
                Cylinder(radius=5.5/2, height=wall*2, mode=Mode.SUBTRACT)
                with Locations((0, 0, wall)):
                    Cylinder(radius=10.0/2, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

        # 7. Cable Cutout
        if not is_left:
            with Locations((side_x + wall/2, 0, wall + tablet_t/2)):
                Box(wall * 3, 50, tablet_t * 0.8, mode=Mode.SUBTRACT)

        # 8. Joints
        join_face = obj.faces().filter_by(Axis.X, 0).sort_by(Axis.Z)[0]
        RigidJoint("center_joint", obj.part, join_face.location)
        RigidJoint("adapter_mount", obj.part, Location((0, 0, 3), (0, 0, 0)))
    
    return obj.part
