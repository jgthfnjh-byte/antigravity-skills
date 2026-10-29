# 🚀 Antigravity Engineering Skills Bundle

Комплексный пакет инженерных навыков (Skills), разработанный для **Google Antigravity**, адаптированный для интеграции в **Google AI Studio**, **Gemini 4 Argon / Pro** и автономные агентные пайплайны.

---

## 📦 Каталог навыков

| Навык | Путь | Описание |
| :--- | :--- | :--- |
| **kompas-3d** | `skills/kompas-3d/` | Автоматизация КОМПАС-3D (v18-v25 / Study). Генерация 2D-чертежей ЕСКД (.cdw), 3D-деталей (.m3d), экспорт в STEP/PDF/STL через CLI `kompas_tool.py` и JSON-спецификации. |
| **kompas-argon-bridge** | `skills/kompas-argon-bridge/` | Гибридный мост между Google AI Studio (Argon) и локальным КОМПАС-3D. Форматы передачи геометрии (декларативный JSON, массивы координат сплайнов). |
| **paht-calculations** | `skills/paht-calculations/` | Расчеты процессов и аппаратов химической технологии (ПАХТ): гидродинамика ($Re, \lambda, \Delta P$), теплообменники ($Nu, Pr, \Delta t_{ср}, F$), ректификационные колонны. |
| **gost-materials** | `skills/gost-materials/` | Справочник конструкционных материалов по ГОСТ (Ст3сп, 20, 45, 09Г2С, 12Х18Н10Т) и правила оформления чертежей по ЕСКД (ГОСТ 2.109-73, 2.301-68). |
| **exact-engineering-calculations** | `skills/exact-engineering-calculations/` | Детерминированные инженерные и физико-химические расчеты с обязательным запуском Python-кода (Code Execution) для исключения арифметических галлюцинаций. |
| **smart-workflow-routing** | `skills/smart-workflow-routing/` | Практический алгоритм маршрутизации задач между Antigravity (локальный агент), Google AI Studio (Argon/Pro) и мобильным приложением Gemini. |

---

## ⚡ Инструкция по подключению в Google AI Studio

### Вариант 1: Автозагрузка через System Instructions
Добавьте в поле **System Instructions** профиля Google AI Studio следующую инструкцию:

```markdown
У тебя есть доступ к внешней базе инженерных скиллов на GitHub:
https://github.com/ВАШ_НИК/ВАШ_РЕПОЗИТОРИЙ.git

Если задача связана со специализированной предметной областью (КОМПАС-3D, ПАХТ, ЕСКД, расчет оборудования):
1. Проверь наличие папки /custom_skills.
2. Если папки нет — склонируй репозиторий в терминале:
   git clone --depth 1 https://github.com/ВАШ_НИК/ВАШ_РЕПОЗИТОРИЙ.git /custom_skills
3. Прочитай соответствующий SKILL.md из /custom_skills/[название_навыка]/ и строго следуй его спецификациям.
```

### Вариант 2: Использование в интерактивном апплете / контейнере
Склонируйте репозиторий в корень проекта:
```bash
git clone https://github.com/ВАШ_НИК/ВАШ_РЕПОЗИТОРИЙ.git custom_skills
```

---

## 🛠️ Структура репозитория

```text
antigravity-skills/
├── README.md                           # Главный каталог и инструкция
├── skills/
│   ├── kompas-3d/                      # Навык КОМПАС-3D
│   │   ├── SKILL.md
│   │   ├── examples/                   # Примеры JSON-спецификаций и скриптов
│   │   ├── references/                 # ЕСКД, API7, форматы спецификаций
│   │   └── scripts/                    # kompas_tool.py (CLI и COM-интерфейс)
│   ├── kompas-argon-bridge/            # Мост AI Studio ↔ КОМПАС-3D
│   │   └── SKILL.md
│   ├── paht-calculations/              # Процессы и аппараты (ПАХТ)
│   │   ├── SKILL.md
│   │   └── scripts/                    # Python-скрипты (Re, LMTD, колонны)
│   ├── gost-materials/                 # Справочник сталей и ГОСТов
│   │   └── SKILL.md
│   ├── exact-engineering-calculations/ # Code Execution расчеты
│   │   └── SKILL.md
│   └── smart-workflow-routing/         # Маршрутизация задач
│       └── SKILL.md
```

Лицензия: MIT
