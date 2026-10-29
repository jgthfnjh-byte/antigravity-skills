#!/usr/bin/env python3
import math

def calculate_heat_exchanger(Q_watt: float, K_coeff: float, t_h_in: float, t_h_out: float, t_c_in: float, t_c_out: float):
    """
    Q_watt: тепловая нагрузка [Вт]
    K_coeff: коэффициент теплопередачи [Вт/(м2*К)]
    t_h_in, t_h_out: температуры горячего теплоносителя [C]
    t_c_in, t_c_out: температуры холодного теплоносителя [C]
    """
    dt_1 = t_h_in - t_c_out
    dt_2 = t_h_out - t_c_in
    
    dt_max = max(dt_1, dt_2)
    dt_min = min(dt_1, dt_2)
    
    if dt_min <= 0:
        raise ValueError("Температурный напор на выходе меньше или равен нулю! Проверьте температуры.")
        
    if dt_max / dt_min < 1.001:
        dt_mean = dt_max
    else:
        dt_mean = (dt_max - dt_min) / math.log(dt_max / dt_min)
        
    F_area = Q_watt / (K_coeff * dt_mean)
    
    return {
        "dt_max": round(dt_max, 2),
        "dt_min": round(dt_min, 2),
        "dt_mean_K": round(dt_mean, 2),
        "F_required_m2": round(F_area, 3)
    }

if __name__ == "__main__":
    res = calculate_heat_exchanger(Q_watt=250000.0, K_coeff=400.0, t_h_in=95.0, t_h_out=50.0, t_c_in=15.0, t_c_out=45.0)
    for k, v in res.items():
        print(f"{k}: {v}")
