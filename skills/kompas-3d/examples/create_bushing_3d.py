# -*- coding: utf-8 -*-
"""
Пример создания 3D-детали втулки с фланцем и отверстием в КОМПАС-3D.
"""

import os
import sys

scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from kompas_tool import KompasSession

def create_bushing():
    with KompasSession() as session:
        part = session.create_part(title="Втулка с фланцем", code="ВТ.005.00")

        # 1. Базовый фланец (d=60 мм, толщина 10 мм)
        sk_flange, h_flange = part.create_sketch("XOY")
        with h_flange as h:
            h.add_circle(0, 0, 30)
        part.extrude_base(sk_flange, depth=10.0)

        # 2. Тело втулки (d=35 мм, длина 40 мм)
        sk_body, h_body = part.create_sketch("XOY")
        with h_body as h:
            h.add_circle(0, 0, 17.5)
        part.extrude_boss(sk_body, depth=50.0)

        # 3. Сквозное осевое отверстие (d=20 мм, глубина 50 мм)
        sk_hole, h_hole = part.create_sketch("XOY")
        with h_hole as h:
            h.add_circle(0, 0, 10.0)
        part.extrude_cut(sk_hole, depth=50.0)

        # 4. Крепежные отверстия на фланце (4 шт, d=6 мм по окружности d=46 мм)
        sk_bolts, h_bolts = part.create_sketch("XOY")
        with h_bolts as h:
            h.add_circle(23, 0, 3)
            h.add_circle(-23, 0, 3)
            h.add_circle(0, 23, 3)
            h.add_circle(0, -23, 3)
        part.extrude_cut(sk_bolts, depth=10.0)

        out_m3d = os.path.abspath("bushing.m3d")
        out_step = os.path.abspath("bushing.step")
        out_stl = os.path.abspath("bushing.stl")

        part.save(out_m3d)
        part.export(out_step)
        part.export(out_stl)

        print(f"3D-деталь сохранена: {out_m3d}")
        print(f"STEP экспортирован: {out_step}")
        print(f"STL экспортирован: {out_stl}")

if __name__ == "__main__":
    create_bushing()
