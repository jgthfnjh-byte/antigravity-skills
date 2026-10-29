#!/usr/bin/env python3

def calculate_rectification(F: float, x_F: float, x_D: float, x_W: float):
    """
    F: расход исходной смеси [кг/с или кмоль/ч]
    x_F, x_D, x_W: мольные или массовые доли легколетучего компонента
    """
    D = F * (x_F - x_W) / (x_D - x_W)
    W = F * (x_D - x_F) / (x_D - x_W)
    
    return {
        "Feed_F": F,
        "Distillate_D": round(D, 3),
        "Bottoms_W": round(W, 3),
        "Check_Sum": round(D + W, 3)
    }

if __name__ == "__main__":
    print(calculate_rectification(F=1000.0, x_F=0.35, x_D=0.96, x_W=0.03))
