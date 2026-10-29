# -*- coding: utf-8 -*-
"""
Пример создания 2D-чертежа ступенчатого вала по ГОСТ/ЕСКД в КОМПАС-3D.
"""

import os
import sys

# Подключение библиотеки инструментария
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from kompas_tool import KompasSession

def create_shaft_drawing():
    with KompasSession() as session:
        # Создаем чертеж формата A4 (вертикальный)
        doc = session.create_drawing(
            format="A4",
            orientation="vertical",
            title="ВАЛ СТУПЕНЧАТЫЙ",
            code="ВЛ.002.01",
            org="МГТУ им. Н.Э. Баумана",
            author="Инженер"
        )

        # Центр вала на листе
        cx, cy = 105.0, 160.0

        # Ступени вала (длина, диаметр):
        # 1 ступень: d=20, L=30
        # 2 ступень: d=30, L=40
        # 3 ступень: d=25, L=30
        # Общая длина: 100 мм

        # Осевая линия (штрихпунктирная)
        doc.add_line(cx - 60, cy, cx + 60, cy, style="axial")

        # 1-я ступень (-50..-20 по X, -10..10 по Y)
        doc.add_rect(cx - 50, cy - 10, cx - 20, cy + 10, style="normal")

        # 2-я ступень (-20..20 по X, -15..15 по Y)
        doc.add_rect(cx - 20, cy - 15, cx + 20, cy + 15, style="normal")

        # 3-я ступень (20..50 по X, -12.5..12.5 по Y)
        doc.add_rect(cx + 20, cy - 12.5, cx + 50, cy + 12.5, style="normal")

        # Линейные размеры длин ступеней:
        doc.add_dim_linear(cx - 50, cy - 10, cx - 20, cy - 10, y3=cy - 30)
        doc.add_dim_linear(cx - 20, cy - 15, cx + 20, cy - 15, y3=cy - 30)
        doc.add_dim_linear(cx + 20, cy - 12.5, cx + 50, cy - 12.5, y3=cy - 30)

        # Габаритная общая длина (100 мм)
        doc.add_dim_linear(cx - 50, cy - 10, cx + 50, cy - 12.5, y3=cy - 45)

        # Диаметры ступеней (по вертикали)
        doc.add_dim_linear(cx - 35, cy - 10, cx - 35, cy + 10, x3=cx - 65, orientation="vertical")
        doc.add_dim_linear(cx, cy - 15, cx, cy + 15, x3=cx + 65, orientation="vertical")

        # Технические требования
        doc.add_text(25, 75, "1. *Размеры для справок.", height=3.5)
        doc.add_text(25, 68, "2. Неуказанные предельные отклонения: H14, h14, +-IT14/2.", height=3.5)
        doc.add_text(25, 61, "3. Радиальное биение поверхностей относительно общей оси не более 0.03 мм.", height=3.5)

        out_cdw = os.path.abspath("shaft_drawing.cdw")
        out_pdf = os.path.abspath("shaft_drawing.pdf")

        doc.save(out_cdw)
        doc.export(out_pdf)

        print(f"Чертеж сохранен: {out_cdw}")
        print(f"PDF экспортирован: {out_pdf}")

if __name__ == "__main__":
    create_shaft_drawing()
