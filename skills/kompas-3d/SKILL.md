---
name: kompas-3d
description: >-
  Use this skill whenever the user wants to create, edit, inspect, or automate
  drawings (чертежи .cdw, .frw) and 3D models (детали .m3d, сборки .a3d) in
  КОМПАС-3D (including KOMPAS-3D Учебная версия / Study / Home v18-v25), export
  to PDF, DXF, DWG, STEP, STL, or apply ESKD/ГОСТ standards. Works across all
  LLM models (Gemini Flash, Claude Sonnet/Opus, etc.).
---

# Навык автоматизации КОМПАС-3D (Учебная и полная версии)

Этот навык обучает агента работать с САПР **КОМПАС-3D** (включая **КОМПАС-3D Учебная версия v18–v25**, Home и коммерческие версии) через официальный Python API (API7 / `ksapi` / COM). Навык спроектирован так, чтобы гарантированно и одинаково надежно работать на **любых языковых моделях** — от легких (Gemini Flash) до глубоких (Claude Sonnet / Opus).

---

## 🚀 Быстрый старт: три способа работы

В зависимости от задачи и используемой модели выберите наиболее подходящий способ:

### Способ 1: Декларативный JSON-спецификатор (Рекомендуется для Gemini Flash)
Модели семейств Flash идеально генерируют валидный JSON и не делают синтаксических ошибок в сложных COM-цепочках.
1. Создайте файл спецификации `spec.json` (чертеж или 3D-деталь).
2. Запустите сборщик:
   ```powershell
   python "C:\Users\jgthfnjh\.gemini\config\skills\kompas-3d\scripts\kompas_tool.py" build --spec spec.json --output part.m3d --export part.step --export part.stl
   ```
*(Примеры спецификаций смотрите в [examples/](./examples/)).*

### Способ 2: Высокоуровневая Python-библиотека `kompas_tool` (Рекомендуется для Claude)
Модели семейства Claude отлично справляются со скриптами, когда им предоставлен чистый типизированный интерфейс:
```python
import sys
sys.path.append(r"C:\Users\jgthfnjh\.gemini\config\skills\kompas-3d\scripts")
from kompas_tool import KompasSession

with KompasSession() as session:
    # 2D Чертеж по ЕСКД с основной надписью
    doc = session.create_drawing(
        format="A4", orientation="vertical",
        title="ВТУЛКА НАПРАВЛЯЮЩАЯ", code="ВТ.010.001", org="МГТУ им. Баумана"
    )
    doc.add_circle(100, 150, 30, style="normal")
    doc.add_circle(100, 150, 15, style="normal")
    doc.add_line(60, 150, 140, 150, style="axial")
    doc.add_dim_diametral(100, 150, 30, angle=45)
    doc.save("vtulka.cdw")
    doc.export("vtulka.pdf")
```

### Способ 3: Прямой CLI-интерфейс
Для быстрых типовых операций без написания кода:
```powershell
# Проверка окружения (версия, путь, соединение)
python "C:\Users\jgthfnjh\.gemini\config\skills\kompas-3d\scripts\kompas_tool.py" doctor

# Быстрое создание прямоугольной призмы 100x60x20 мм и экспорт в STEP
python "C:\Users\jgthfnjh\.gemini\config\skills\kompas-3d\scripts\kompas_tool.py" part box --length 100 --width 60 --height 20 --output plate.m3d --export-step plate.step

# Быстрое создание цилиндра/втулки с отверстием
python "C:\Users\jgthfnjh\.gemini\config\skills\kompas-3d\scripts\kompas_tool.py" part cylinder --radius 25 --height 50 --hole 12 --output bushing.m3d --export-stl bushing.stl

# Экспорт любого .cdw или .m3d в PDF, DXF, STEP, STL
python "C:\Users\jgthfnjh\.gemini\config\skills\kompas-3d\scripts\kompas_tool.py" export --input drawing.cdw --output drawing.pdf
```

---

## 🎯 Особенности моделей (Gemini Flash vs Claude)

Подробное руководство по различиям моделей находится в [references/models_guide.md](./references/models_guide.md).

| Модель | Сильные стороны | Типичная ловушка | Рекомендуемая тактика |
| :--- | :--- | :--- | :--- |
| **Gemini Flash** | Высокая скорость, огромный контекст, безошибочный JSON | Склонна выдумывать названия методов COM при написании низкоуровневого win32com кода "из головы" | Использовать `kompas_tool.py build --spec spec.json` либо готовые функции `kompas_tool` |
| **Claude (Sonnet / Opus)** | Точная геометрия, сложные тригонометрические расчеты, понимание сборок | Может забыть вызвать `sketch.EndEdit()` перед выдавливанием или искать `KOMPAS.exe` вместо `kStudy.exe` | Использовать `KompasSession` с контекстным менеджером `with helper as h: ...` |

---

## ⚠️ Важнейшие правила КОМПАС-3D (Учебная версия)

1. **Исполняемый файл Учебной версии**:
   В Учебной версии главный исполняемый файл называется **`kStudy.exe`** (а не `KOMPAS.exe`).
   При вызове COM (`win32com.client.Dispatch("KOMPAS.Application.7")`) Windows находит его автоматически через системный реестр.
2. **Разрядность Python**:
   КОМПАС-3D v18–v25 — строго 64-битное приложение. Python обязан быть **64-битным**.
3. **Согласование эскизов (3D)**:
   При создании 3D-операций (выдавливание, вырезание) эскиз обязан быть:
   - Открыт на редактирование: `doc2d = sketch.BeginEdit(False)`
   - Наполнен замкнутым контуром (без самопересечений)
   - Закрыт перед операцией: `sketch.EndEdit()`
4. **Форматы сохранения и экспорта**:
   `SaveAs` в КОМПАС-3D автоматически распознает формат по расширению:
   - 2D: `.cdw` (родной), `.pdf` (векторный PDF), `.dxf`, `.dwg`, `.png`
   - 3D: `.m3d` (родной), `.step` / `.stp`, `.stl` (для 3D-печати), `.iges`
5. **Стили линий по ГОСТ**:
   - `1` — `ksCSNormal` (Основная, контур)
   - `2` — `ksCSThin` (Тонкая, размеры, штриховка)
   - `3` — `ksCSAxial` (Осевая, штрихпунктирная)
   - `4` — `ksCSDotted` (Штриховая, невидимый контур)

---

## 📚 Справочные материалы

- **[references/api7_cheatsheet.md](./references/api7_cheatsheet.md)** — Полный низкоуровневый справочник API7 (создание линий, дуг, окружностей, штампа, 3D-тел, фасок, скруглений).
- **[references/educational_edition.md](./references/educational_edition.md)** — Специфика Учебной версии (водяные знаки, пути, права, совместимость).
- **[references/eskd_gost_reference.md](./references/eskd_gost_reference.md)** — Стандарты ЕСКД: форматы листов, графки штампа ГОСТ 2.104, допуски и шероховатость.
- **[references/models_guide.md](./references/models_guide.md)** — Детальное руководство для Gemini, Claude и других моделей.
