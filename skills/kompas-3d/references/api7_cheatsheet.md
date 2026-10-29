# Шпаргалка по API7 КОМПАС-3D в Python

Данный справочник содержит проверенные, протестированные на реальной сборке КОМПАС-3D шаблоны кода на Python для низкоуровневой работы через библиотеку `ksapi` и COM-интерфейс `KOMPAS.Application.7`.

---

## 1. Подключение и инициализация

```python
import sys, os
import win32com.client

# 1. Автоматический запуск через COM (корректно запускает kStudy.exe / KOMPAS.exe)
try:
    com_app = win32com.client.Dispatch("KOMPAS.Application.7")
    com_app.Visible = True
except Exception as e:
    print("Ошибка запуска COM:", e)

# 2. Подключение через высокопроизводительный ksapi
kompas_bin = r"C:\Program Files\ASCON\KOMPAS-3D v25 Study\Bin"
if kompas_bin not in sys.path:
    sys.path.insert(0, kompas_bin)

import ksapi
from constants import constants as k_const
from constants3d import constants as c3d

app = ksapi.GetKompas()
app.SetVisible(True)
```

---

## 2. 2D Чертеж (Чертежи .cdw / Фрагменты .frw)

### 2.1 Создание документа и получение контейнеров
```python
docs = app.GetDocuments()
# Создание чертежа со стандартными настройками
doc = docs.AddWithDefaultSettings(k_const.ksDocumentDrawing, True)

# Приведение к интерфейсу 2D-документа
doc2d = ksapi.IKompasDocument2D(doc)
vlm = doc2d.GetViewsAndLayersManager()
views = vlm.GetViews()
active_view = views.GetActiveView()

# Контейнеры графики и обозначений
draw_cont = ksapi.IDrawingContainer(active_view)
sym_cont = ksapi.ISymbols2DContainer(active_view)
```

### 2.2 Формат листа и ориентация
```python
sheets = doc2d.GetLayoutSheets()
sheet = sheets.GetItem(0)
fmt = sheet.GetFormat()

# Форматы: 4 = A4, 3 = A3, 2 = A2, 1 = A1, 0 = A0
fmt.SetFormat(3)                  # A3
fmt.SetVerticalOrientation(False) # Горизонтальная ориентация
sheet.Update()
```

### 2.3 Основная надпись (Штамп ГОСТ 2.104)
```python
stamp = sheet.GetStamp()
# Номера граф:
# 1 - Наименование изделия
# 2 - Обозначение чертежа (шифр)
# 3 - Материал
# 9 - Организация / ВУЗ
# 110 - Разработал
# 111 - Проверил

stamp.GetText(1).SetStr("ПЛИТА НАПРАВЛЯЮЩАЯ")
stamp.GetText(2).SetStr("АБВГ.100.001")
stamp.GetText(9).SetStr("МГТУ им. Баумана")
stamp.GetText(110).SetStr("Иванов")
stamp.Update()
```

### 2.4 Геометрические примитивы
```python
# Отрезок:
line = draw_cont.GetLineSegments().Add()
line.SetX1(0); line.SetY1(0); line.SetX2(100); line.SetY2(0)
line.SetStyle(k_const.ksCSNormal) # 1 - Основная линия
line.Update()

# Окружность:
circ = draw_cont.GetCircles().Add()
circ.SetXc(50); circ.SetYc(50); circ.SetRadius(25)
circ.SetStyle(k_const.ksCSNormal)
circ.Update()

# Дуга окружности:
arc = draw_cont.GetArcs().Add()
arc.SetXc(0); arc.SetYc(0); arc.SetRadius(30)
arc.SetAngle1(0); arc.SetAngle2(90) # Углы в градусах
arc.SetDirection(True)              # True = против часовой стрелки
arc.SetStyle(k_const.ksCSNormal)
arc.Update()

# Текст (технические требования или надписи):
txt = draw_cont.GetDrawingTexts().Add()
txt.SetX(20); txt.SetY(30)
t_line = ksapi.IText(txt)
t_line.SetStr("1. *Размеры для справок.")
txt.Update()
```

### 2.5 Размеры (ISymbols2DContainer)
```python
# Линейный горизонтальный размер:
dim_lin = sym_cont.GetLineDimensions().Add()
dim_lin.SetX1(0); dim_lin.SetY1(0)
dim_lin.SetX2(100); dim_lin.SetY2(0)
dim_lin.SetX3(50); dim_lin.SetY3(-15) # Положение размерной линии
dim_lin.SetOrientation(k_const.ksLinDHorizontal)
dim_lin.Update()

# Диаметральный размер:
dim_d = sym_cont.GetDiametralDimensions().Add()
dim_d.SetXc(50); dim_d.SetYc(50); dim_d.SetRadius(25)
dim_d.SetAngle(45.0) # Угол полки в градусах
dim_d.Update()

# Радиальный размер:
dim_r = sym_cont.GetRadialDimensions().Add()
dim_r.SetXc(0); dim_r.SetYc(0); dim_r.SetRadius(30)
dim_r.SetAngle(60.0)
dim_r.Update()
```

---

## 3. 3D Моделирование (Детали .m3d)

### 3.1 Создание детали и выбор плоскости
```python
doc = docs.AddWithDefaultSettings(k_const.ksDocumentPart, True)
doc3d = ksapi.IKompasDocument3D(doc)
part = doc3d.GetTopPart()

# Имя и обозначение
part.SetName("Корпус")
part.SetMarking("КРП.001.00")

# Получение базовых плоскостей:
# c3d.o3d_planeXOY = 1
# c3d.o3d_planeXOZ = 2
# c3d.o3d_planeYOZ = 3
planeXOY = part.GetDefaultObject(c3d.o3d_planeXOY)
container = part.GetModelContainer()
```

### 3.2 Создание эскиза
```python
sketches = container.GetSketchs()
sketch = sketches.Add()
sketch.SetPlane(planeXOY)
sketch.Update()

# ВАЖНО: открыть на редактирование с readOnly=False
doc2d = sketch.BeginEdit(False)
draw_cont = ksapi.IDrawingContainer(doc2d.GetViewsAndLayersManager().GetViews().GetActiveView())

# Добавляем прямоугольник (контур должен быть строго замкнут)
lines = draw_cont.GetLineSegments()
def add_line(x1, y1, x2, y2):
    l = lines.Add()
    l.SetX1(x1); l.SetY1(y1); l.SetX2(x2); l.SetY2(y2)
    l.SetStyle(k_const.ksCSNormal)
    l.Update()

add_line(-40, -25,  40, -25)
add_line( 40, -25,  40,  25)
add_line( 40,  25, -40,  25)
add_line(-40,  25, -40, -25)

# ВАЖНО: завершить редактирование эскиза перед 3D-операцией
sketch.EndEdit()
```

### 3.3 Базовое выдавливание (o3d_baseExtrusion)
```python
extrusions = container.GetExtrusions()
base_ext = extrusions.Add(c3d.o3d_baseExtrusion) # 24
base_ext.SetProfiles([sketch])                   # Список эскизов
base_ext.SetDirection(c3d.dtNormal)              # Прямое направление (0)
base_ext.SetExtrusionType(True, c3d.ksDTValue)   # По расстоянию (0)
base_ext.SetDepth(True, 20.0)                    # Глубина 20 мм
base_ext.Update()
```

### 3.4 Вырезание выдавливанием (o3d_cutExtrusion)
```python
# Эскиз отверстия
sk_hole = sketches.Add()
sk_hole.SetPlane(planeXOY)
sk_hole.Update()

doc2d_hole = sk_hole.BeginEdit(False)
draw_cont_hole = ksapi.IDrawingContainer(doc2d_hole.GetViewsAndLayersManager().GetViews().GetActiveView())
circ = draw_cont_hole.GetCircles().Add()
circ.SetXc(0); circ.SetYc(0); circ.SetRadius(12)
circ.SetStyle(k_const.ksCSNormal)
circ.Update()
sk_hole.EndEdit()

# Вырезание
cut_ext = extrusions.Add(c3d.o3d_cutExtrusion) # 26
cut_ext.SetProfiles([sk_hole])
cut_ext.SetDirection(c3d.dtNormal)
cut_ext.SetExtrusionType(True, c3d.ksDTValue)
cut_ext.SetDepth(True, 20.0)
cut_ext.Update()
```

---

## 4. Сохранение и экспорт

Метод `SaveAs()` в КОМПАС-3D определяет целевой формат автоматически по расширению:

```python
# 2D Чертеж:
doc.SaveAs(os.path.abspath("drawing.cdw")) # Родной формат КОМПАС
doc.SaveAs(os.path.abspath("drawing.pdf")) # Векторный PDF
doc.SaveAs(os.path.abspath("drawing.dxf")) # AutoCAD DXF
doc.SaveAs(os.path.abspath("drawing.dwg")) # AutoCAD DWG

# 3D Деталь:
doc.SaveAs(os.path.abspath("part.m3d"))  # Родная 3D-модель
doc.SaveAs(os.path.abspath("part.step")) # STEP AP214 / AP203
doc.SaveAs(os.path.abspath("part.stl"))  # Полигональный STL для 3D-печати
doc.SaveAs(os.path.abspath("part.iges")) # IGES

# Закрытие документа (0 = без сохранения изменений в исходнике)
doc.Close(0)
```
