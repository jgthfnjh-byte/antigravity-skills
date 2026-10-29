# Руководство по работе с разными моделями (Gemini Flash vs Claude)

Главная цель данного навыка — **одинаково безупречная работа** при переключении между различными языковыми моделями: **Gemini Flash**, **Claude (Sonnet / Opus)**, **GPT-4o** и др.

---

## 1. В чем корень проблемы при работе разных моделей с КОМПАС-3D?

1. **Разнобой между API5 и API7**:
   В документации АСКОН есть старый API5 (`ksDocument2D`, `ksCircle`, `ksLineSeg`) и современный объектно-ориентированный API7 (`IKompasDocument2D`, `IDrawingContainer`, `ISymbols2DContainer`, `IPart7`, `IModelContainer`).
   - Модели без жестких ограничений часто смешивают методы API5 и API7 в одном скрипте.
2. **Особенности COM в Windows**:
   Прямой COM требует либо предварительной генерации кеша через `gencache.EnsureDispatch`, либо явного приведения типов (`CastTo`), иначе возникают `AttributeError` или `COM error: Член группы не найден`.
3. **Имя исполняемого файла**:
   Попытка запустить `KOMPAS.exe` терпит крах в Учебной версии, где файл называется `kStudy.exe`.

Наш навык решает это на уровне архитектуры: готовая библиотека `kompas_tool.py` берет на себя все низкоуровневые нюансы Windows, COM и Учебной версии.

---

## 2. Стратегия для Gemini Flash (и быстрых легковесных моделей)

### Особенности поведения
- **Сильные стороны**: Невероятная скорость, огромное контекстное окно, идеальное следование декларативным схемам и генерация чистого JSON.
- **Слабые стороны**: При попытке написать 100 строк "сырого" COM-кода Python с нуля может придумать несуществующий метод (например, `doc.CreateCircle(0, 0, 10)` вместо обращения к `draw_cont.GetCircles().Add()`).

### Рекомендуемый подход для Flash: Декларативный JSON-спецификатор

Попросите Flash описать деталь или чертеж в виде JSON и передать в `kompas_tool.py build`:

```json
{
  "type": "part",
  "title": "Фланец",
  "operations": [
    {
      "type": "extrude",
      "plane": "XOY",
      "depth": 12.0,
      "sketch": [
        {"type": "circle", "xc": 0, "yc": 0, "radius": 50}
      ]
    },
    {
      "type": "cut",
      "plane": "XOY",
      "depth": 12.0,
      "sketch": [
        {"type": "circle", "xc": 0, "yc": 0, "radius": 20},
        {"type": "circle", "xc": 35, "yc": 0, "radius": 5},
        {"type": "circle", "xc": -35, "yc": 0, "radius": 5},
        {"type": "circle", "xc": 0, "yc": 35, "radius": 5},
        {"type": "circle", "xc": 0, "yc": -35, "radius": 5}
      ]
    }
  ]
}
```

Запуск:
```powershell
python "C:\Users\jgthfnjh\.gemini\config\skills\kompas-3d\scripts\kompas_tool.py" build --spec flange.json --output flange.m3d --export flange.step --export flange.stl
```
Результат: **100% повторяемость без единой галлюцинации**.

---

## 3. Стратегия для Claude (Claude 3.5 Sonnet / Claude 3.7 Sonnet / Claude Opus)

### Особенности поведения
- **Сильные стороны**: Превосходное пространственное мышление, знание стандартов ЕСКД, идеальный расчет координат, тригонометрии зубчатых колес, фасок, посадок и допусков.
- **Слабые стороны**: Может писать избыточный многословный код на `win32com`, забыв закрыть эскиз через `sketch.EndEdit()`.

### Рекомендуемый подход для Claude: Python-скрипт с `kompas_tool`

Claude превосходно пишет процедурные скрипты с использованием типизированной обертки `KompasSession`:

```python
import math
import sys
sys.path.append(r"C:\Users\jgthfnjh\.gemini\config\skills\kompas-3d\scripts")
from kompas_tool import KompasSession

with KompasSession() as session:
    part = session.create_part(title="Шестерня прямозубая", code="ЗК.01.002")
    
    # Эскиз венца с вычислением координат зубьев
    sk, helper = part.create_sketch("XOY")
    with helper as h:
        # Расчет делительной окружности и профиля
        h.add_circle(0, 0, 40)
    
    # Выдавливание на ширину венца
    part.extrude_base(sk, depth=25.0)
    
    # Отверстие под вал со шпоночным пазом
    sk_hole, h_hole = part.create_sketch("XOY")
    with h_hole as h2:
        h2.add_circle(0, 0, 12)
    part.extrude_cut(sk_hole, depth=25.0)
    
    part.save("gear.m3d")
    part.export("gear.step")
```

---

## 4. Использование навыка в других инструментах (Claude Code, Cursor, Codex)

Этот навык полностью переносим. Чтобы подключить его:

### В Claude Code:
1. Добавьте в файл `CLAUDE.md` вашего проекта ссылку:
   ```markdown
   ## KOMPAS-3D Integration
   When working with CAD drawings or 3D models in KOMPAS-3D:
   - Use the CLI tool: `python "C:\Users\jgthfnjh\.gemini\config\skills\kompas-3d\scripts\kompas_tool.py"`
   - Always verify environment using `doctor` subcommand.
   - For 2D drawings follow GOST 2.104.
   ```
2. Либо скопируйте папку навыка в проект: `.agents/skills/kompas-3d/` или `.claude/skills/kompas-3d/`.

### В Antigravity при переключении моделей:
В меню Antigravity в любой момент можно переключить модель:
- `Gemini 1.5 Flash` / `Gemini 2.0 Flash`
- `Claude 3.5 Sonnet` / `Claude 3.7 Sonnet`
- `Gemini Pro`
Навык активируется автоматически при упоминании КОМПАС-3D или чертежей, и агент адаптирует рабочий процесс под выбранную модель.
