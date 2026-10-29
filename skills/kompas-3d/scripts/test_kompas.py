# -*- coding: utf-8 -*-
"""
KOMPAS-3D Skill Verification & Health Check Test Suite
"""

import os
import sys
import tempfile
import platform

# Add scripts directory to path
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from kompas_tool import KompasSession, find_kompas_bin

def run_tests():
    print("=" * 60)
    print("   КОМПАС-3D: Проверка работоспособности навыка")
    print("=" * 60)

    # 1. Python Architecture
    arch = platform.architecture()[0]
    print(f"[1/6] Архитектура Python: {arch} ... ", end="")
    if arch == "64bit":
        print("OK (64-бит)")
    else:
        print(f"ОШИБКА: Требуется 64-битный Python, обнаружен {arch}")
        return False

    # 2. KOMPAS Bin Discovery
    print("[2/6] Поиск каталога KOMPAS Bin ... ", end="")
    try:
        bin_dir = find_kompas_bin()
        print(f"OK ({bin_dir})")
    except Exception as e:
        print(f"ОШИБКА: {e}")
        return False

    # 3. Connection Test
    print("[3/6] Проверка соединения с КОМПАС-3D ... ", end="")
    try:
        session = KompasSession(visible=True)
        diag = session.doctor()
        print(f"OK (Версия: {diag['kompas_version']})")
    except Exception as e:
        print(f"ОШИБКА: {e}")
        return False

    tmp_dir = tempfile.mkdtemp(prefix="kompas_test_")

    try:
        # 4. 2D Drawing Test
        print("[4/6] Тест создания 2D-чертежа (ЕСКД A4, геометрия, штамп, экспорт в PDF) ... ", end="")
        dwg = session.create_drawing(
            format="A4", orientation="vertical",
            title="ТЕСТОВЫЙ ЧЕРТЕЖ", code="ТСТ.001.00", org="Тест"
        )
        dwg.add_rect(20, 20, 100, 80)
        dwg.add_circle(60, 50, 20)
        dwg.add_dim_linear(20, 20, 100, 20, y3=10)
        dwg.add_dim_diametral(60, 50, 20)
        cdw_file = os.path.join(tmp_dir, "test_draw.cdw")
        pdf_file = os.path.join(tmp_dir, "test_draw.pdf")
        dwg.save(cdw_file)
        dwg.export(pdf_file)
        dwg.close(save=False)

        if os.path.exists(cdw_file) and os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 1000:
            print("OK")
        else:
            print("ОШИБКА: Файлы чертежа не сформированы корректно")
            return False

        # 5. 3D Part Test
        print("[5/6] Тест 3D-моделирования (эскиз, базовое выдавливание, вырезание, экспорт в STEP/STL) ... ", end="")
        part = session.create_part(title="Тестовая деталь", code="ДЕТ.001.00")
        part.create_box(80, 50, 20)
        sk_cut, h_cut = part.create_sketch("XOY")
        with h_cut as h:
            h.add_circle(0, 0, 10)
        part.extrude_cut(sk_cut, depth=20)

        m3d_file = os.path.join(tmp_dir, "test_part.m3d")
        step_file = os.path.join(tmp_dir, "test_part.step")
        stl_file = os.path.join(tmp_dir, "test_part.stl")
        part.save(m3d_file)
        part.export(step_file)
        part.export(stl_file)
        part.close(save=False)

        if os.path.exists(m3d_file) and os.path.exists(step_file) and os.path.exists(stl_file):
            print("OK")
        else:
            print("ОШИБКА: Файлы 3D-детали не сформированы корректно")
            return False

        # 6. JSON Spec Builder Test
        print("[6/6] Тест сборщика декларативных спецификаций JSON ... ", end="")
        from kompas_tool import build_from_spec
        spec = {
            "type": "drawing",
            "format": "A4",
            "elements": [
                {"type": "line", "x1": 0, "y1": 0, "x2": 50, "y2": 50}
            ]
        }
        res = build_from_spec(spec)
        session.close_all(save=False)
        if res.get("status") == "SUCCESS":
            print("OK")
        else:
            print(f"ОШИБКА: {res}")
            return False

    finally:
        # Cleanup
        session.close_all(save=False)
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("=" * 60)
    print("   ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ! Навык готов к работе.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
