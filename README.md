# LowEarthOrbit_BMS (From Task Description)
Battery Management Systems (BMS) in LEO missions, considering eclipse cycling, temperature swings, radiation, and mission lifetime. You will translate orbital and load profiles into BMS requirements (sensing accuracy, SOC/SOH estimation, balancing strategy, redundancy) and compare terrestrial and space‑specific BMS architectures.

## LEO BMS Mini Demo
This is a mini demo from an orbital/load profile into battery-management requirements for a Low Earth Orbit mission.

### Why Python
I chose Python because it is compact, easy to inspect, and a good fit for requirement-generation logic that may later expand into data-driven sizing, degradation models, or standards-based rule checks.

### Data structures
The tool uses plain dictionaries and lists so the output can be serialized directly to JSON and also mapped easily into markdown, requirement databases, or a future web API.

Inputs: Orbit and load assumptions.

Computed: Sizing and operating quantities derived from those assumptions.

BMS_Requirements: Concise requirement snippet that can seed a systems engineering flow.

Current model
The script takes:

- Orbital period
- Eclipse duration
- Average payload power
- Nominal battery voltage

It then computes for two mission styles:

- Required usable eclipse capacity
- Average eclipse current and C-rate
- Recommended SOC operating window
- Short requirement snippet

### The two cases are intentionally simple:

Short-lived high-power assumes higher payload demand but allows a wider usable fraction of installed capacity.

Long-lived low-power assumes lower demand but preserves life with a tighter usable fraction and SOC window.

### How to extend it
A more detailed requirement generator would likely add:

- Cell model layer: OCV-SOC curves, temperature derating, internal resistance, charge acceptance.

- Mission profile layer: time-series eclipse/sunlight loads, attitude modes, safe mode, peak pulses.

- Lifetime layer: cycle fade and calendar fade versus DOD, temperature, and upper charge voltage.

- Reliability layer: single-fault tolerance, cross-strapped sensors, independent protection cutoffs, FDIR logic.

- Standards layer: machine-readable rules derived from NASA, ECSS, or project-specific verification requirements.

- Output layer: traceable requirements with IDs, rationale, verification method, and margin bookkeeping.

## Example

 python bms_requirements_tool.py --orbital-period 95 --eclipse-duration 35 --avg-payload-power 120 --battery-voltage 28 --format md

### Sample Ouput
short-lived high-power
Required eclipse energy: 105.0 Wh

Required usable capacity: 3.75 Ah

Recommended installed capacity: 6.25 Ah

Average eclipse C-rate: 1.029

Recommended SOC window: 0.25 to 0.75