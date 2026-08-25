"""
Análisis: última vuelta Abu Dhabi GP 2021 - Verstappen vs Hamilton
Requiere: fastf1, pandas, matplotlib
"""

import fastf1
import pandas as pd
import matplotlib.pyplot as plt


# 1. Cargar la sesión con FastF1

session = fastf1.get_session(2021, "Abu Dhabi", "R")
session.load()

df = session.laps.copy()

# session.laps ya trae las columnas de tiempo como Timedelta nativo,
# así que no hace falta parsear strings como con un CSV.
df["LapTimeSec"] = df["LapTime"].dt.total_seconds()


# 2. Filtrar VER y HAM en las últimas vueltas

LAP_START, LAP_END = 49, 58  # ventana de análisis (ajusta si quieres ver más vueltas)

foc = df[
    (df["Driver"].isin(["VER", "HAM"]))
    & (df["LapNumber"].between(LAP_START, LAP_END))
].sort_values(["LapNumber", "Driver"]).copy()

cols = [
    "Driver", "LapNumber", "LapTimeSec", "Compound", "TyreLife",
    "FreshTyre", "Stint", "PitInTime", "PitOutTime", "TrackStatus", "Position",
]
print("=== Tabla comparativa VER vs HAM (últimas vueltas) ===")
print(foc[cols].to_string(index=False))

# 3. Delta de la última vuelta (la vuelta de carrera real, post-SC)

last_lap = df["LapNumber"].max()

ham_last = df[(df["Driver"] == "HAM") & (df["LapNumber"] == last_lap)]
ver_last = df[(df["Driver"] == "VER") & (df["LapNumber"] == last_lap)]

ham_time = ham_last["LapTimeSec"].values[0]
ver_time = ver_last["LapTimeSec"].values[0]
delta = ham_time - ver_time

print(f"\n=== Vuelta {int(last_lap)} (bandera verde real) ===")
print(f"HAM: {ham_time:.3f}s | Compuesto: {ham_last['Compound'].values[0]} "
      f"| Vida neumático: {ham_last['TyreLife'].values[0]:.0f} vueltas")
print(f"VER: {ver_time:.3f}s | Compuesto: {ver_last['Compound'].values[0]} "
      f"| Vida neumático: {ver_last['TyreLife'].values[0]:.0f} vueltas")
print(f"-> VER más rápido por {delta:.3f} segundos")

# ---------------------------------------------------------------
# 4. Identificar cuándo entró el Safety Car (cambio en TrackStatus)
# ---------------------------------------------------------------
sc_laps = df[df["TrackStatus"].astype(str).str.contains("4")]["LapNumber"].unique()
print(f"\nVueltas con Safety Car activo (TrackStatus contiene '4'): {sorted(sc_laps)}")

# ---------------------------------------------------------------
# 5. Gráfica: ritmo por vuelta VER vs HAM
# ---------------------------------------------------------------
ham_series = foc[foc["Driver"] == "HAM"].set_index("LapNumber")["LapTimeSec"]
ver_series = foc[foc["Driver"] == "VER"].set_index("LapNumber")["LapTimeSec"]

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(ham_series.index, ham_series.values, marker="o", label="Hamilton (Mercedes)", color="#27F4D2")
ax.plot(ver_series.index, ver_series.values, marker="o", label="Verstappen (Red Bull)", color="#1E5BC6")

# Sombrear la ventana del Safety Car
ax.axvspan(53, 57, color="yellow", alpha=0.15, label="Safety Car")

ax.set_xlabel("Número de vuelta")
ax.set_ylabel("Tiempo de vuelta (s)")
ax.set_title("Ritmo por vuelta — Últimas 10 vueltas, Abu Dhabi GP 2021")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("ritmo_ver_ham_abu_dhabi_2021.png", dpi=150)
plt.show()

print("\nGráfica guardada como ritmo_ver_ham_abu_dhabi_2021.png")
