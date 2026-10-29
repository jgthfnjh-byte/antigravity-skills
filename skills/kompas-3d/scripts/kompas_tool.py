# -*- coding: utf-8 -*-
"""
KOMPAS-3D Automation Tool & Library
Unified automation framework for KOMPAS-3D (Educational / Study / Home / Commercial).
Compatible with Python 3.8+ 64-bit on Windows.
Designed for deterministic AI agent execution (Gemini Flash, Claude Sonnet/Opus, GPT-4o, etc.).
"""

import os
import sys
import json
import argparse
import platform
from typing import List, Tuple, Dict, Any, Optional

# Enforce Windows
if platform.system() != "Windows":
    raise SystemError("KOMPAS-3D automation is only supported on Microsoft Windows.")

# Auto-locate KOMPAS Bin Directory
def find_kompas_bin() -> str:
    """Find the Bin directory of KOMPAS-3D on this system."""
    import winreg

    # 1. Try registry LocalServer32
    clsids = [
        r"CLSID\{8C3719B5-0DF2-4C12-9CA8-3AF4827A3BBB}\LocalServer32",  # Standard / Visual
        r"CLSID\{1A4C2A9B-3B2A-49D1-B75F-3810DD4A2086}\LocalServer32",  # Invisible
    ]
    for clsid in clsids:
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, clsid) as key:
                val, _ = winreg.QueryValueEx(key, "")
                cleaned = val.strip().strip('"')
                candidate = os.path.dirname(cleaned)
                if os.path.exists(candidate) and os.path.exists(os.path.join(candidate, "ksapi.py")):
                    return candidate
        except Exception:
            pass

    # 2. Program Files inspection
    for base in [r"C:\Program Files\ASCON", r"C:\Program Files (x86)\ASCON"]:
        if os.path.exists(base):
            for item in sorted(os.listdir(base), reverse=True):
                bin_candidate = os.path.join(base, item, "Bin")
                if os.path.exists(bin_candidate) and os.path.exists(os.path.join(bin_candidate, "ksapi.py")):
                    return bin_candidate

    raise FileNotFoundError("Could not find KOMPAS-3D Bin directory. Ensure KOMPAS-3D is installed.")

# Initialize environment
KOMPAS_BIN = find_kompas_bin()
if KOMPAS_BIN not in sys.path:
    sys.path.insert(0, KOMPAS_BIN)

import ksapi
from constants import constants as k_const
try:
    from constants3d import constants as k_const3d
except ImportError:
    k_const3d = None

STYLE_MAP = {
    "normal": k_const.ksCSNormal,          # 1 - Основная
    "основная": k_const.ksCSNormal,
    "thin": k_const.ksCSThin,              # 2 - Тонкая
    "тонкая": k_const.ksCSThin,
    "axial": k_const.ksCSAxial,            # 3 - Осевая
    "осевая": k_const.ksCSAxial,
    "dotted": k_const.ksCSDotted,          # 4 - Штриховая
    "штриховая": k_const.ksCSDotted,
    "thick": k_const.ksCSThick,            # 5 - Утолщенная
    "утолщенная": k_const.ksCSThick,
}

FORMAT_MAP = {
    "A0": 0, "a0": 0,
    "A1": 1, "a1": 1,
    "A2": 2, "a2": 2,
    "A3": 3, "a3": 3,
    "A4": 4, "a4": 4,
}

STAMP_FIELD_MAP = {
    "title": 1, "наименование": 1,
    "code": 2, "номер": 2, "обозначение": 2,
    "material": 3, "материал": 3,
    "litter": 4, "литера": 4,
    "weight": 5, "масса": 5,
    "scale": 6, "масштаб": 6,
    "sheet": 7, "лист": 7,
    "sheets": 8, "листов": 8,
    "org": 9, "предприятие": 9, "организация": 9,
    "author": 110, "разраб": 110, "разработал": 110,
    "checker": 111, "пров": 111, "проверил": 111,
    "tech": 112, "тконтр": 112,
    "norm": 114, "нконтр": 114,
    "approver": 115, "утв": 115, "утвердил": 115,
}


class KompasSession:
    """Manages connection and interaction with KOMPAS-3D application."""

    def __init__(self, visible: bool = True):
        self.visible = visible
        self.app = None
        self._ensure_app()

    def _ensure_app(self):
        # 1. Connect to running instance
        self.app = ksapi.GetKompas()
        if not self.app:
            # 2. Launch using COM
            try:
                import win32com.client
                com_app = win32com.client.Dispatch("KOMPAS.Application.7")
                com_app.Visible = self.visible
                self.app = ksapi.GetKompas()
            except Exception as e:
                # Fallback to direct ksapi.OpenKompas
                for exe in ["kStudy.exe", "KOMPAS.exe", "kHome.exe"]:
                    full_exe = os.path.join(KOMPAS_BIN, exe)
                    if os.path.exists(full_exe):
                        port = ksapi.OpenKompas(full_exe)
                        if port != 0:
                            self.app = ksapi.IApplication(port)
                            break

        if not self.app:
            raise RuntimeError("Failed to start or connect to KOMPAS-3D application.")

        if self.visible:
            self.app.SetVisible(True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # We leave KOMPAS open for user inspection by default
        pass

    def doctor(self) -> Dict[str, Any]:
        """Perform system diagnostics."""
        docs = self.app.GetDocuments()
        doc_count = docs.GetCount() if docs else 0
        return {
            "status": "OK",
            "python_version": sys.version,
            "architecture": platform.architecture()[0],
            "kompas_bin": KOMPAS_BIN,
            "kompas_version": getattr(self.app, "GetOpenVersion", lambda: "v25")(),
            "open_documents": doc_count,
            "visible": self.visible,
        }

    def close_all(self, save: bool = False):
        """Close all open documents."""
        docs = self.app.GetDocuments()
        if not docs:
            return
        while docs.GetCount() > 0:
            doc = docs.GetItem(0)
            doc.Close(1 if save else 0)

    def create_drawing(self, format: str = "A4", orientation: str = "vertical",
                       title: str = "", code: str = "", org: str = "", author: str = "") -> "DrawingDoc":
        """Create a new 2D Drawing document (.cdw)."""
        docs = self.app.GetDocuments()
        doc = docs.AddWithDefaultSettings(k_const.ksDocumentDrawing, True)
        d_doc = DrawingDoc(doc, self.app)
        d_doc.set_sheet(format, orientation)
        if title or code or org or author:
            d_doc.set_stamp({
                "title": title,
                "code": code,
                "org": org,
                "author": author,
            })
        return d_doc

    def create_part(self, title: str = "", code: str = "") -> "PartDoc":
        """Create a new 3D Part document (.m3d)."""
        docs = self.app.GetDocuments()
        doc = docs.AddWithDefaultSettings(k_const.ksDocumentPart, True)
        p_doc = PartDoc(doc, self.app)
        if title or code:
            p_doc.set_properties(title=title, code=code)
        return p_doc

    def open_document(self, path: str):
        """Open an existing document (.cdw, .m3d, .frw, etc.)."""
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: {abs_path}")
        docs = self.app.GetDocuments()
        doc = docs.Open(abs_path, True, False)
        ext = os.path.splitext(abs_path)[1].lower()
        if ext in [".cdw", ".frw"]:
            return DrawingDoc(doc, self.app)
        elif ext in [".m3d", ".a3d"]:
            return PartDoc(doc, self.app)
        return doc


class DrawingDoc:
    """Wrapper for KOMPAS 2D Drawing (.cdw)."""

    def __init__(self, doc, app):
        self.doc = doc
        self.app = app
        self.doc2d = ksapi.IKompasDocument2D(doc)
        self.vlm = self.doc2d.GetViewsAndLayersManager()
        self.active_view = self.vlm.GetViews().GetActiveView()
        self.draw_cont = ksapi.IDrawingContainer(self.active_view)
        self.sym_cont = ksapi.ISymbols2DContainer(self.active_view)

    def set_sheet(self, format: str = "A4", orientation: str = "vertical"):
        """Configure sheet format and orientation."""
        sheets = self.doc2d.GetLayoutSheets()
        if not sheets or sheets.GetCount() == 0:
            return
        sheet = sheets.GetItem(0)
        fmt = sheet.GetFormat()
        fmt_val = FORMAT_MAP.get(format.upper(), 4)
        is_vert = (orientation.lower() in ["vertical", "вертикальная", "vert", "v"])
        fmt.SetFormat(fmt_val)
        fmt.SetVerticalOrientation(is_vert)
        sheet.Update()

    def set_stamp(self, fields: Dict[Any, str]):
        """Set fields in the standard ESKD title block."""
        sheets = self.doc2d.GetLayoutSheets()
        if not sheets or sheets.GetCount() == 0:
            return
        sheet = sheets.GetItem(0)
        stamp = sheet.GetStamp()
        for k, v in fields.items():
            if not v:
                continue
            col_id = STAMP_FIELD_MAP.get(str(k).lower(), k if isinstance(k, int) else None)
            if col_id is not None:
                txt = stamp.GetText(int(col_id))
                if txt:
                    txt.SetStr(str(v))
        stamp.Update()

    def add_line(self, x1: float, y1: float, x2: float, y2: float, style: str = "normal"):
        """Add a 2D line segment."""
        line = self.draw_cont.GetLineSegments().Add()
        line.SetX1(float(x1))
        line.SetY1(float(y1))
        line.SetX2(float(x2))
        line.SetY2(float(y2))
        line.SetStyle(STYLE_MAP.get(style.lower(), k_const.ksCSNormal))
        line.Update()
        return line

    def add_rect(self, x1: float, y1: float, x2: float, y2: float, style: str = "normal"):
        """Add a rectangle defined by opposite corners (x1, y1) and (x2, y2)."""
        self.add_line(x1, y1, x2, y1, style)
        self.add_line(x2, y1, x2, y2, style)
        self.add_line(x2, y2, x1, y2, style)
        self.add_line(x1, y2, x1, y1, style)

    def add_circle(self, xc: float, yc: float, radius: float, style: str = "normal"):
        """Add a 2D circle."""
        circle = self.draw_cont.GetCircles().Add()
        circle.SetXc(float(xc))
        circle.SetYc(float(yc))
        circle.SetRadius(float(radius))
        circle.SetStyle(STYLE_MAP.get(style.lower(), k_const.ksCSNormal))
        circle.Update()
        return circle

    def add_arc(self, xc: float, yc: float, radius: float, a1_deg: float, a2_deg: float,
                ccw: bool = True, style: str = "normal"):
        """Add a 2D arc with start and end angles in degrees."""
        arc = self.draw_cont.GetArcs().Add()
        arc.SetXc(float(xc))
        arc.SetYc(float(yc))
        arc.SetRadius(float(radius))
        arc.SetAngle1(float(a1_deg))
        arc.SetAngle2(float(a2_deg))
        arc.SetDirection(ccw)
        arc.SetStyle(STYLE_MAP.get(style.lower(), k_const.ksCSNormal))
        arc.Update()
        return arc

    def add_text(self, x: float, y: float, text: str, height: float = 5.0, angle: float = 0.0):
        """Add free text to the drawing."""
        d_txt = self.draw_cont.GetDrawingTexts().Add()
        d_txt.SetX(float(x))
        d_txt.SetY(float(y))
        d_txt.SetAngle(float(angle))
        t = ksapi.IText(d_txt)
        if t:
            t.SetStr(str(text))
        d_txt.Update()
        return d_txt

    def add_dim_linear(self, x1: float, y1: float, x2: float, y2: float,
                       x3: Optional[float] = None, y3: Optional[float] = None,
                       orientation: str = "horizontal"):
        """Add a linear dimension."""
        dim = self.sym_cont.GetLineDimensions().Add()
        dim.SetX1(float(x1))
        dim.SetY1(float(y1))
        dim.SetX2(float(x2))
        dim.SetY2(float(y2))
        # Default offset if x3/y3 not provided
        px = x3 if x3 is not None else (x1 + x2) / 2.0
        py = y3 if y3 is not None else min(y1, y2) - 15.0
        dim.SetX3(float(px))
        dim.SetY3(float(py))

        ori_map = {
            "horizontal": k_const.ksLinDHorizontal,
            "vertical": k_const.ksLinDVertical,
            "parallel": k_const.ksLinDParallel,
        }
        dim.SetOrientation(ori_map.get(orientation.lower(), k_const.ksLinDHorizontal))
        dim.Update()
        return dim

    def add_dim_diametral(self, xc: float, yc: float, radius: float, angle: float = 45.0):
        """Add a diametral dimension to a circle."""
        dim = self.sym_cont.GetDiametralDimensions().Add()
        dim.SetXc(float(xc))
        dim.SetYc(float(yc))
        dim.SetRadius(float(radius))
        dim.SetAngle(float(angle))
        dim.Update()
        return dim

    def add_dim_radial(self, xc: float, yc: float, radius: float, angle: float = 45.0):
        """Add a radial dimension to an arc/circle."""
        dim = self.sym_cont.GetRadialDimensions().Add()
        dim.SetXc(float(xc))
        dim.SetYc(float(yc))
        dim.SetRadius(float(radius))
        dim.SetAngle(float(angle))
        dim.Update()
        return dim

    def save(self, path: Optional[str] = None) -> bool:
        """Save drawing to disk."""
        if path:
            return bool(self.doc.SaveAs(os.path.abspath(path)))
        return bool(self.doc.Save())

    def export(self, path: str) -> bool:
        """Export to PDF, DXF, DWG, PNG, BMP."""
        abs_path = os.path.abspath(path)
        res = self.doc.SaveAs(abs_path)
        return bool(res and os.path.exists(abs_path))

    def close(self, save: bool = False):
        """Close document."""
        self.doc.Close(1 if save else 0)


class SketchHelper:
    """Context manager for drawing contours inside a 3D sketch."""

    def __init__(self, sketch):
        self.sketch = sketch
        self.doc2d = None
        self.draw_cont = None

    def __enter__(self):
        self.doc2d = self.sketch.BeginEdit(False)
        vlm = self.doc2d.GetViewsAndLayersManager()
        active_view = vlm.GetViews().GetActiveView()
        self.draw_cont = ksapi.IDrawingContainer(active_view)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sketch.EndEdit()

    def add_line(self, x1: float, y1: float, x2: float, y2: float):
        line = self.draw_cont.GetLineSegments().Add()
        line.SetX1(float(x1))
        line.SetY1(float(y1))
        line.SetX2(float(x2))
        line.SetY2(float(y2))
        line.SetStyle(k_const.ksCSNormal)
        line.Update()
        return line

    def add_rect(self, x1: float, y1: float, x2: float, y2: float):
        self.add_line(x1, y1, x2, y1)
        self.add_line(x2, y1, x2, y2)
        self.add_line(x2, y2, x1, y2)
        self.add_line(x1, y2, x1, y1)

    def add_circle(self, xc: float, yc: float, radius: float):
        circ = self.draw_cont.GetCircles().Add()
        circ.SetXc(float(xc))
        circ.SetYc(float(yc))
        circ.SetRadius(float(radius))
        circ.SetStyle(k_const.ksCSNormal)
        circ.Update()
        return circ


class PartDoc:
    """Wrapper for KOMPAS 3D Part (.m3d)."""

    def __init__(self, doc, app):
        self.doc = doc
        self.app = app
        self.doc3d = ksapi.IKompasDocument3D(doc)
        self.part = self.doc3d.GetTopPart()
        self.container = self.part.GetModelContainer()

    def set_properties(self, title: str = "", code: str = ""):
        if title:
            self.part.SetName(title)
        if code:
            self.part.SetMarking(code)

    def get_plane(self, plane_name: str = "XOY"):
        """Get standard base coordinate plane (XOY, XOZ, YOZ)."""
        p_name = plane_name.upper().strip()
        plane_const = k_const3d.o3d_planeXOY
        if p_name == "XOZ":
            plane_const = k_const3d.o3d_planeXOZ
        elif p_name == "YOZ":
            plane_const = k_const3d.o3d_planeYOZ
        return self.part.GetDefaultObject(plane_const)

    def create_sketch(self, plane="XOY") -> Tuple[Any, SketchHelper]:
        """Create a new sketch on the specified plane."""
        plane_obj = plane if not isinstance(plane, str) else self.get_plane(plane)
        sketches = self.container.GetSketchs()
        sketch = sketches.Add()
        sketch.SetPlane(plane_obj)
        sketch.Update()
        return sketch, SketchHelper(sketch)

    def extrude_base(self, sketch, depth: float = 10.0, direction: str = "normal"):
        """Extrude base operation (o3d_baseExtrusion)."""
        exts = self.container.GetExtrusions()
        ext = exts.Add(k_const3d.o3d_baseExtrusion)
        ext.SetProfiles([sketch])
        dir_val = k_const3d.dtNormal if direction == "normal" else k_const3d.dtReverse
        ext.SetDirection(dir_val)
        ext.SetExtrusionType(True, k_const3d.ksDTValue)
        ext.SetDepth(True, float(depth))
        ext.Update()
        return ext

    def extrude_boss(self, sketch, depth: float = 10.0, direction: str = "normal"):
        """Extrude boss operation (o3d_bossExtrusion)."""
        exts = self.container.GetExtrusions()
        ext = exts.Add(k_const3d.o3d_bossExtrusion)
        ext.SetProfiles([sketch])
        dir_val = k_const3d.dtNormal if direction == "normal" else k_const3d.dtReverse
        ext.SetDirection(dir_val)
        ext.SetExtrusionType(True, k_const3d.ksDTValue)
        ext.SetDepth(True, float(depth))
        ext.Update()
        return ext

    def extrude_cut(self, sketch, depth: float = 10.0, direction: str = "normal"):
        """Extrude cut operation (o3d_cutExtrusion)."""
        exts = self.container.GetExtrusions()
        ext = exts.Add(k_const3d.o3d_cutExtrusion)
        ext.SetProfiles([sketch])
        dir_val = k_const3d.dtNormal if direction == "normal" else k_const3d.dtReverse
        ext.SetDirection(dir_val)
        ext.SetExtrusionType(True, k_const3d.ksDTValue)
        ext.SetDepth(True, float(depth))
        ext.Update()
        return ext

    def create_box(self, length: float, width: float, height: float, plane: str = "XOY"):
        """Quick primitive: create a 3D box centered at origin."""
        sk, helper = self.create_sketch(plane)
        with helper as h:
            h.add_rect(-length/2.0, -width/2.0, length/2.0, width/2.0)
        return self.extrude_base(sk, depth=height)

    def create_cylinder(self, radius: float, height: float, hole_radius: float = 0.0, plane: str = "XOY"):
        """Quick primitive: create a solid or hollow 3D cylinder."""
        sk, helper = self.create_sketch(plane)
        with helper as h:
            h.add_circle(0, 0, radius)
        base = self.extrude_base(sk, depth=height)
        if hole_radius > 0:
            sk_hole, h_hole = self.create_sketch(plane)
            with h_hole as h2:
                h2.add_circle(0, 0, hole_radius)
            self.extrude_cut(sk_hole, depth=height)
        return base

    def save(self, path: Optional[str] = None) -> bool:
        """Save 3D Part to disk (.m3d)."""
        if path:
            return bool(self.doc.SaveAs(os.path.abspath(path)))
        return bool(self.doc.Save())

    def export(self, path: str) -> bool:
        """Export 3D Part to STEP, STL, IGES, PDF."""
        abs_path = os.path.abspath(path)
        res = self.doc.SaveAs(abs_path)
        return bool(res and os.path.exists(abs_path))

    def close(self, save: bool = False):
        """Close document."""
        self.doc.Close(1 if save else 0)


def build_from_spec(spec: Dict[str, Any], output_path: Optional[str] = None,
                    export_paths: Optional[List[str]] = None) -> Dict[str, Any]:
    """Execute a declarative JSON specification for a 2D Drawing or 3D Part."""
    model_type = spec.get("type", "drawing").lower()

    with KompasSession(visible=spec.get("visible", True)) as session:
        if model_type in ["drawing", "чертеж", "2d"]:
            doc = session.create_drawing(
                format=spec.get("format", "A4"),
                orientation=spec.get("orientation", "vertical"),
                title=spec.get("stamp", {}).get("title", ""),
                code=spec.get("stamp", {}).get("code", ""),
                org=spec.get("stamp", {}).get("org", ""),
                author=spec.get("stamp", {}).get("author", ""),
            )
            if "stamp" in spec:
                doc.set_stamp(spec["stamp"])

            for elem in spec.get("elements", []):
                e_type = elem.get("type", "").lower()
                style = elem.get("style", "normal")
                if e_type in ["line", "линия"]:
                    doc.add_line(elem["x1"], elem["y1"], elem["x2"], elem["y2"], style)
                elif e_type in ["rect", "rectangle", "прямоугольник"]:
                    doc.add_rect(elem["x1"], elem["y1"], elem["x2"], elem["y2"], style)
                elif e_type in ["circle", "окружность"]:
                    doc.add_circle(elem["xc"], elem["yc"], elem["radius"], style)
                elif e_type in ["arc", "дуга"]:
                    doc.add_arc(elem["xc"], elem["yc"], elem["radius"], elem["a1"], elem["a2"],
                                elem.get("ccw", True), style)
                elif e_type in ["text", "текст"]:
                    doc.add_text(elem["x"], elem["y"], elem["text"], elem.get("height", 5.0), elem.get("angle", 0.0))
                elif e_type in ["dim_linear", "размер_линейный"]:
                    doc.add_dim_linear(elem["x1"], elem["y1"], elem["x2"], elem["y2"],
                                       elem.get("x3"), elem.get("y3"), elem.get("orientation", "horizontal"))
                elif e_type in ["dim_diametral", "размер_диаметральный"]:
                    doc.add_dim_diametral(elem["xc"], elem["yc"], elem["radius"], elem.get("angle", 45.0))
                elif e_type in ["dim_radial", "размер_радиальный"]:
                    doc.add_dim_radial(elem["xc"], elem["yc"], elem["radius"], elem.get("angle", 45.0))

            saved = None
            if output_path:
                doc.save(output_path)
                saved = os.path.abspath(output_path)

            exported = []
            if export_paths:
                for exp in export_paths:
                    if doc.export(exp):
                        exported.append(os.path.abspath(exp))

            # Auto-deliver to Desktop
            desktop_files = []
            try:
                desk_dir = os.path.join(os.path.expanduser("~/Desktop"), "KOMPAS_Files")
                os.makedirs(desk_dir, exist_ok=True)
                all_files = ([saved] if saved else []) + exported
                for f in all_files:
                    if f and os.path.exists(f):
                        shutil.copy2(f, desk_dir)
                        desktop_files.append(os.path.join(desk_dir, os.path.basename(f)))
            except Exception:
                pass

            return {"status": "SUCCESS", "type": "drawing", "saved": saved, "exported": exported, "desktop_delivery": desktop_files}

        elif model_type in ["part", "деталь", "3d"]:
            part = session.create_part(
                title=spec.get("title", ""),
                code=spec.get("code", "")
            )

            for op in spec.get("operations", []):
                op_type = op.get("type", "").lower()
                plane = op.get("plane", "XOY")
                depth = float(op.get("depth", 10.0))

                if op_type in ["box", "призма"]:
                    part.create_box(op["length"], op["width"], op["height"], plane)
                elif op_type in ["cylinder", "цилиндр"]:
                    part.create_cylinder(op["radius"], op["height"], op.get("hole_radius", 0.0), plane)
                elif op_type in ["extrude", "выдавливание", "base_extrude"]:
                    sk, helper = part.create_sketch(plane)
                    with helper as h:
                        for elem in op.get("sketch", []):
                            e_type = elem.get("type", "").lower()
                            if e_type in ["line", "линия"]:
                                h.add_line(elem["x1"], elem["y1"], elem["x2"], elem["y2"])
                            elif e_type in ["rect", "rectangle"]:
                                h.add_rect(elem["x1"], elem["y1"], elem["x2"], elem["y2"])
                            elif e_type in ["circle", "окружность"]:
                                h.add_circle(elem["xc"], elem["yc"], elem["radius"])
                    part.extrude_base(sk, depth=depth)
                elif op_type in ["cut", "вырезание", "cut_extrude"]:
                    sk, helper = part.create_sketch(plane)
                    with helper as h:
                        for elem in op.get("sketch", []):
                            e_type = elem.get("type", "").lower()
                            if e_type in ["circle", "окружность"]:
                                h.add_circle(elem["xc"], elem["yc"], elem["radius"])
                            elif e_type in ["rect", "rectangle"]:
                                h.add_rect(elem["x1"], elem["y1"], elem["x2"], elem["y2"])
                    part.extrude_cut(sk, depth=depth)

            saved = None
            if output_path:
                part.save(output_path)
                saved = os.path.abspath(output_path)

            exported = []
            if export_paths:
                for exp in export_paths:
                    if part.export(exp):
                        exported.append(os.path.abspath(exp))

            # Auto-deliver to Desktop
            desktop_files = []
            try:
                desk_dir = os.path.join(os.path.expanduser("~/Desktop"), "KOMPAS_Files")
                os.makedirs(desk_dir, exist_ok=True)
                all_files = ([saved] if saved else []) + exported
                for f in all_files:
                    if f and os.path.exists(f):
                        shutil.copy2(f, desk_dir)
                        desktop_files.append(os.path.join(desk_dir, os.path.basename(f)))
            except Exception:
                pass

            return {"status": "SUCCESS", "type": "part", "saved": saved, "exported": exported, "desktop_delivery": desktop_files}

    return {"status": "ERROR", "message": f"Unsupported model type: {model_type}"}


def main():
    parser = argparse.ArgumentParser(description="KOMPAS-3D Automation CLI")
    subparsers = parser.add_subparsers(dest="command")

    # doctor
    subparsers.add_parser("doctor", help="Check KOMPAS environment and connection")

    # info
    subparsers.add_parser("info", help="Show KOMPAS version and open documents")

    # build
    build_p = subparsers.add_parser("build", help="Build drawing or 3D part from JSON spec")
    build_p.add_argument("--spec", required=True, help="Path to JSON specification file")
    build_p.add_argument("--output", help="Path to save output file (.cdw or .m3d)")
    build_p.add_argument("--export", action="append", help="Export to format (.pdf, .step, .stl, .dxf)")

    # drawing new
    draw_p = subparsers.add_parser("drawing", help="2D Drawing operations")
    draw_sub = draw_p.add_subparsers(dest="draw_cmd")
    new_draw_p = draw_sub.add_parser("new", help="Create new drawing")
    new_draw_p.add_argument("--format", default="A4", help="Sheet format (A4, A3, A2, A1, A0)")
    new_draw_p.add_argument("--orientation", default="vertical", help="Orientation (vertical, horizontal)")
    new_draw_p.add_argument("--title", default="", help="Part title in stamp")
    new_draw_p.add_argument("--code", default="", help="Drawing code in stamp")
    new_draw_p.add_argument("--org", default="", help="Organization in stamp")
    new_draw_p.add_argument("--output", required=True, help="Path to save .cdw file")
    new_draw_p.add_argument("--export-pdf", help="Path to export .pdf")

    # part primitives
    part_p = subparsers.add_parser("part", help="3D Part operations")
    part_sub = part_p.add_subparsers(dest="part_cmd")
    box_p = part_sub.add_parser("box", help="Create rectangular prism")
    box_p.add_argument("--length", type=float, required=True)
    box_p.add_argument("--width", type=float, required=True)
    box_p.add_argument("--height", type=float, required=True)
    box_p.add_argument("--output", required=True, help="Output .m3d file")
    box_p.add_argument("--export-step", help="Export .step file")
    box_p.add_argument("--export-stl", help="Export .stl file")

    cyl_p = part_sub.add_parser("cylinder", help="Create cylinder or bushing")
    cyl_p.add_argument("--radius", type=float, required=True)
    cyl_p.add_argument("--height", type=float, required=True)
    cyl_p.add_argument("--hole", type=float, default=0.0, help="Hole radius (0 for solid)")
    cyl_p.add_argument("--output", required=True, help="Output .m3d file")
    cyl_p.add_argument("--export-step", help="Export .step file")
    cyl_p.add_argument("--export-stl", help="Export .stl file")

    # export
    exp_p = subparsers.add_parser("export", help="Convert KOMPAS file to other formats")
    exp_p.add_argument("--input", required=True, help="Input .cdw or .m3d file")
    exp_p.add_argument("--output", required=True, help="Output file (.pdf, .dxf, .step, .stl)")

    args = parser.parse_args()

    if args.command == "doctor":
        with KompasSession() as session:
            doc_info = session.doctor()
            print(json.dumps(doc_info, indent=2, ensure_ascii=False))

    elif args.command == "info":
        with KompasSession() as session:
            doc_info = session.doctor()
            print(f"KOMPAS Bin: {doc_info['kompas_bin']}")
            print(f"Open Documents: {doc_info['open_documents']}")

    elif args.command == "build":
        with open(args.spec, "r", encoding="utf-8") as f:
            spec_data = json.load(f)
        exports = args.export if args.export else []
        res = build_from_spec(spec_data, args.output, exports)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "drawing" and args.draw_cmd == "new":
        with KompasSession() as session:
            doc = session.create_drawing(
                format=args.format,
                orientation=args.orientation,
                title=args.title,
                code=args.code,
                org=args.org
            )
            doc.save(args.output)
            print(f"Drawing saved to: {os.path.abspath(args.output)}")
            if args.export_pdf:
                doc.export(args.export_pdf)
                print(f"PDF exported to: {os.path.abspath(args.export_pdf)}")

    elif args.command == "part" and args.part_cmd == "box":
        with KompasSession() as session:
            part = session.create_part(title="Плита")
            part.create_box(args.length, args.width, args.height)
            part.save(args.output)
            print(f"Part saved to: {os.path.abspath(args.output)}")
            if args.export_step:
                part.export(args.export_step)
                print(f"STEP exported to: {os.path.abspath(args.export_step)}")
            if args.export_stl:
                part.export(args.export_stl)
                print(f"STL exported to: {os.path.abspath(args.export_stl)}")

    elif args.command == "part" and args.part_cmd == "cylinder":
        with KompasSession() as session:
            part = session.create_part(title="Втулка")
            part.create_cylinder(args.radius, args.height, args.hole)
            part.save(args.output)
            print(f"Part saved to: {os.path.abspath(args.output)}")
            if args.export_step:
                part.export(args.export_step)
                print(f"STEP exported to: {os.path.abspath(args.export_step)}")
            if args.export_stl:
                part.export(args.export_stl)
                print(f"STL exported to: {os.path.abspath(args.export_stl)}")

    elif args.command == "export":
        with KompasSession() as session:
            doc = session.open_document(args.input)
            if hasattr(doc, "export"):
                res = doc.export(args.output)
                print(f"Export result: {res} -> {os.path.abspath(args.output)}")
            else:
                print("Failed: unsupported document type for export.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
