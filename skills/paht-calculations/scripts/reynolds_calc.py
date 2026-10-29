#!/usr/bin/env python3
import math

def calculate_flow(w: float, d: float, rho: float, mu: float, L: float = 1.0, e: float = 0.0002):
    """
    w: скорость [м/с]
    d: внутренний диаметр [м]
    rho: плотность [кг/м3]
    mu: динамическая вязкость [Па*с]
    L: длина трубопровода [м]
    e: абсолютная шероховатость [м] (по умолчанию 0.2 мм для стальных труб)
    """
    Re = (w * d * rho) / mu
    
    if Re < 2300:
        flow_type = "Ламинарный"
        lmbd = 64.0 / Re
    elif Re < 4000:
        flow_type = "Переходный"
        lmbd = 0.04
    elif Re < 100000 and (e / d) < 1e-4:
        flow_type = "Турбулентный (гидравлически гладкие трубы, Блазиус)"
        lmbd = 0.3164 / (Re ** 0.25)
    else:
        flow_type = "Турбулентный (шероховатые трубы, Альтшуль)"
        lmbd = 0.11 * ((e / d + 68.0 / Re) ** 0.25)
        
    delta_p = lmbd * (L / d) * (rho * (w ** 2)) / 2.0
    
    return {
        "Re": round(Re, 2),
        "flow_type": flow_type,
        "lambda": round(lmbd, 5),
        "delta_p_Pa": round(delta_p, 2),
        "delta_p_kPa": round(delta_p / 1000.0, 3)
    }

if __name__ == "__main__":
    res = calculate_flow(w=1.5, d=0.05, rho=1000.0, mu=0.001, L=25.0)
    for k, v in res.items():
        print(f"{k}: {v}")
