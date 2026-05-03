import argparse, json

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def recommend_soc_window(mission_years, eclipse_c_rate, dod_frac):
    if mission_years >= 5:
        base_low, base_high = 0.30, 0.70
    elif mission_years >= 2:
        base_low, base_high = 0.25, 0.75
    else:
        base_low, base_high = 0.20, 0.80
    if eclipse_c_rate > 0.5 or dod_frac > 0.40:
        base_low += 0.05
        base_high -= 0.05
    return round(clamp(base_low, 0.15, 0.45), 2), round(clamp(base_high, 0.55, 0.85), 2)

def assess_case(name, orbital_period_min, eclipse_duration_min, avg_payload_power_w, nominal_battery_voltage_v, mission_years=3, usable_fraction=None):
    eclipse_h = eclipse_duration_min / 60.0
    required_energy_wh = avg_payload_power_w * eclipse_h
    if usable_fraction is None:
        usable_fraction = 0.35 if mission_years >= 5 else 0.60
    usable_capacity_ah = required_energy_wh / nominal_battery_voltage_v
    installed_capacity_ah = usable_capacity_ah / usable_fraction
    avg_current_a = avg_payload_power_w / nominal_battery_voltage_v
    avg_c_rate = avg_current_a / installed_capacity_ah if installed_capacity_ah else 0.0
    soc_low, soc_high = recommend_soc_window(mission_years, avg_c_rate, usable_fraction)
    snippet = {
        "case": name,
        "inputs": {
            "orbital_period_min": orbital_period_min,
            "eclipse_duration_min": eclipse_duration_min,
            "avg_payload_power_w": avg_payload_power_w,
            "nominal_battery_voltage_v": nominal_battery_voltage_v,
            "mission_years": mission_years
        },
        "computed": {
            "required_eclipse_energy_wh": round(required_energy_wh, 2),
            "required_usable_capacity_ah": round(usable_capacity_ah, 3),
            "assumed_usable_fraction_of_installed_capacity": round(usable_fraction, 2),
            "recommended_installed_capacity_ah": round(installed_capacity_ah, 3),
            "average_eclipse_current_a": round(avg_current_a, 3),
            "average_eclipse_c_rate": round(avg_c_rate, 3),
            "recommended_soc_window": [soc_low, soc_high]
        },
        "bms_requirements": {
            "voltage_sensing_accuracy": "<= +-5 mV per cell goal; tighter (approx +-1 mV) beneficial for low-margin, high-energy missions",
            "current_sensing_accuracy": "<= +-1% FS with calibrated low-drift shunt path for SOC integration",
            "temperature_sensing": "cell-level sensing with hot/cold qualification and heater inhibit logic",
            "soc_estimation": "coulomb counting anchored by OCV/rest opportunities and temperature compensation",
            "soh_estimation": "track fade via delivered Ah/Wh, internal resistance trend, and end-of-discharge voltage margin",
            "balancing": "passive balancing acceptable for small series strings; schedule near end-of-charge and inhibit during eclipse unless dispersion is mission-limiting",
            "redundancy": "independent pack protection path for OV/UV/OCP/OTP, watchdog/FDIR, and graceful degradation strategy"
        }
    }
    return snippet

def main():
    ap = argparse.ArgumentParser(description='Simple LEO BMS requirement generator')
    ap.add_argument('--orbital-period', type=float, required=True)
    ap.add_argument('--eclipse-duration', type=float, required=True)
    ap.add_argument('--avg-payload-power', type=float, required=True)
    ap.add_argument('--battery-voltage', type=float, required=True)
    ap.add_argument('--format', choices=['json','md'], default='json')
    args = ap.parse_args()

    cases = [
        assess_case('short-lived high-power', args.orbital_period, args.eclipse_duration, args.avg_payload_power*1.5, args.battery_voltage, mission_years=1, usable_fraction=0.60),
        assess_case('long-lived low-power', args.orbital_period, args.eclipse_duration, args.avg_payload_power*0.6, args.battery_voltage, mission_years=7, usable_fraction=0.35),
    ]

    if args.format == 'json':
        print(json.dumps(cases, indent=2))
    else:
        for c in cases:
            print(f"## {c['case']}")
            print()
            print(f"- Required eclipse energy: {c['computed']['required_eclipse_energy_wh']} Wh")
            print(f"- Required usable capacity: {c['computed']['required_usable_capacity_ah']} Ah")
            print(f"- Recommended installed capacity: {c['computed']['recommended_installed_capacity_ah']} Ah")
            print(f"- Average eclipse C-rate: {c['computed']['average_eclipse_c_rate']}")
            print(f"- Recommended SOC window: {c['computed']['recommended_soc_window'][0]} to {c['computed']['recommended_soc_window'][1]}")
            print()
            print('```json')
            print(json.dumps(c['bms_requirements'], indent=2))
            print('```')
            print()

if __name__ == '__main__':
    main()