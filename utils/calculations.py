import math

def recommend_emitter_head(irrigation_type):
    return 10 if irrigation_type.lower() == 'drip' else 25

def recommend_pipe_class(material, head):
    if material == 'PVC':
        if head <= 25: return 'Class A (2.5 bar)'
        elif head <= 40: return 'Class B (4.0 bar)'
        elif head <= 60: return 'Class C (6.0 bar)'
        else: return 'Above Class C'
    elif material == 'HDPE':
        if head <= 6: return 'PN 6'
        elif head <= 10: return 'PN 10'
        elif head <= 16: return 'PN 16'
        else: return 'PN > 16'
    else:
        return 'Unknown'

def calculate_irrigation_design(crop, soil, material, irrigation_type, water_lpd, static_head, pipe_length, duration_hrs, elev_min, elev_max):
    flow_lps = water_lpd / (duration_hrs * 3600)
    Q = flow_lps / 1000  # m³/s
    nu = 8.5e-7
    roughness = {'PVC': 1.5e-6, 'HDPE': 3e-6, 'GI': 1.5e-4}.get(material, 1.5e-6)
    emitter_head = recommend_emitter_head(irrigation_type)
    friction_limit_pct = 0.2 if irrigation_type.lower() == 'drip' else 0.3
    total_static = static_head + emitter_head
    max_friction_head = friction_limit_pct * total_static

    diameters = [20, 25, 32, 40, 50, 63, 75, 90, 110]
    results = []

    for d_mm in diameters:
        D = d_mm / 1000
        A = math.pi * D**2 / 4
        v = Q / A
        if v > 2.0:
            continue

        Re = v * D / nu
        f = 64 / Re if Re < 2000 else 0.25 / (math.log10(roughness / (3.7 * D) + 5.74 / Re**0.9))**2
        hf = f * (pipe_length / D) * (v**2 / (2*9.81))
        if hf > max_friction_head:
            continue

        total_head = static_head + hf + emitter_head
        power_kw = (1000 * 9.81 * Q * total_head) / 0.6 / 1000
        motor = next((x for x in [0.5, 1, 2, 3, 5, 7.5, 10] if x >= power_kw), f"> 10 HP")

        results.append({
            'diameter': d_mm,
            'velocity': round(v, 2),
            'reynolds': round(Re),
            'friction_factor': round(f, 4),
            'friction_head': round(hf, 2),
            'total_head': round(total_head, 2),
            'pump_power_kw': round(power_kw, 2),
            'motor_hp': motor,
            'pipe_class': recommend_pipe_class(material, total_head)
        })

    if not results:
        return {
            'error': 'No suitable pipe diameter found under the friction and velocity constraints.',
            'all_options': []
        }

    best = min(results, key=lambda x: x['diameter'])
    best.update({
        'q': round(Q, 5),
        'static_head': round(static_head, 2),
        'emitter_head': emitter_head,
        'pipe_length': pipe_length,
        'pipe_material': material,
        'irrigation_type': irrigation_type,
        'elevation_min': round(elev_min, 2),
        'elevation_max': round(elev_max, 2),
        'all_options': results
    })
    return best