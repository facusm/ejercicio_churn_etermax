"""
EDA Bivariado — Churn D1 (Videojuegos Móviles)
================================================
Análisis de tasa de churn segmentado por variables clave.
Genera tablas de resumen + 4 gráficos ejecutivos en formato PNG.
"""

import sys
from pathlib import Path

# ── Asegurar que el directorio del pipeline esté en sys.path ──
PROJECT_DIR = Path(r"c:\Users\Facundo San Martino\Desktop\Proyectos\etermax")
sys.path.insert(0, str(PROJECT_DIR))

import polars as pl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from churn_feature_pipeline import build_churn_features, DATA_PATH

# ═════════════════════════════════════════════════════════════════════════════
# Paso 1 — Ingesta de datos
# ═════════════════════════════════════════════════════════════════════════════
print("Cargando DataFrame enriquecido...")
df = build_churn_features(DATA_PATH)
print(f"  → {df.shape[0]:,} filas × {df.shape[1]} columnas\n")

TARGET = "target_churn_indicator"


# ═════════════════════════════════════════════════════════════════════════════
# Paso 2 — Agregaciones con Polars
# ═════════════════════════════════════════════════════════════════════════════
def agg_churn(df: pl.DataFrame, group_col: str, sort_col: str | None = None,
              descending: bool = True) -> pl.DataFrame:
    """
    Agrupa por `group_col` y calcula volumen de usuarios y tasa de churn (%).
    Ordena por `sort_col` (o por churn_rate desc si no se indica).
    """
    agg = (
        df.lazy()
        .group_by(group_col)
        .agg(
            pl.len().alias("usuarios"),
            (pl.col(TARGET).mean() * 100).alias("churn_rate"),
        )
        .collect()
    )
    sort_key = sort_col or "churn_rate"
    return agg.sort(sort_key, descending=descending)


# 1) install_date — ordenado cronológicamente
tbl_date = agg_churn(df, "install_date", sort_col="install_date", descending=False)

# 2) is_weekend_day1 — ordenado por la flag (0, 1)
tbl_wknd = agg_churn(df, "is_weekend_day1", sort_col="is_weekend_day1", descending=False)

# 3) time_of_day — ordenado por tasa de churn descendente
tbl_tod = agg_churn(df, "time_of_day")

# 4) age_segment — ordenado por tasa de churn descendente
tbl_age = agg_churn(df, "age_segment")

# Imprimir tablas
for nombre, tabla in [
    ("install_date", tbl_date),
    ("is_weekend_day1", tbl_wknd),
    ("time_of_day", tbl_tod),
    ("age_segment", tbl_age),
]:
    print(f"{'=' * 60}")
    print(f"  Churn por {nombre}")
    print(f"{'=' * 60}")
    print(tabla)
    print()


# ═════════════════════════════════════════════════════════════════════════════
# Paso 3 — Visualización ejecutiva
# ═════════════════════════════════════════════════════════════════════════════

# ── Estilo global ──
plt.rcParams.update({
    "figure.facecolor":   "#FAFAFA",
    "axes.facecolor":     "#FAFAFA",
    "axes.edgecolor":     "#CCCCCC",
    "axes.grid":          True,
    "grid.color":         "#E8E8E8",
    "grid.linewidth":     0.6,
    "font.family":        "sans-serif",
    "font.sans-serif":    ["Segoe UI", "Helvetica Neue", "Arial"],
    "font.size":          11,
    "axes.titlesize":     14,
    "axes.titleweight":   "bold",
    "axes.labelsize":     12,
    "xtick.labelsize":    10,
    "ytick.labelsize":    10,
    "figure.dpi":         150,
    "savefig.dpi":        200,
    "savefig.bbox":       "tight",
    "savefig.pad_inches": 0.25,
})

PALETTE_PRIMARY = "#3A86FF"   # azul corporativo
PALETTE_ACCENT  = "#FF6B6B"   # acento para highlights
PALETTE_WEEKEND = ["#64748B", "#F97316"]  # gris / naranja


def _bar_chart(ax, labels, values, volumes, color, title, xlabel, ylabel="Tasa de Churn (%)",
               highlight_max: bool = True, rotation: int = 0):
    """Genera un bar chart minimalista y profesional sobre el eje dado."""
    bars = ax.bar(labels, values, color=color, width=0.55, edgecolor="white",
                  linewidth=0.8, zorder=3)

    # Resaltar la barra con mayor churn
    if highlight_max and len(values) > 1:
        max_idx = values.index(max(values))
        bars[max_idx].set_color(PALETTE_ACCENT)
        bars[max_idx].set_edgecolor("#E05555")

    # Etiquetas sobre cada barra: porcentaje + volumen
    for bar, val, vol in zip(bars, values, volumes):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val:.1f}%\n(n={vol:,})", ha="center", va="bottom", fontsize=8,
                fontweight="semibold", color="#333333")

    ax.set_title(title, pad=14, color="#1A1A2E")
    ax.set_xlabel(xlabel, labelpad=8, color="#555555")
    ax.set_ylabel(ylabel, labelpad=8, color="#555555")
    ax.set_ylim(0, max(values) * 1.25 if values else 1)
    ax.tick_params(axis="x", rotation=rotation)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))

    # Quitar spines superiores y derecho
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_and_save(table: pl.DataFrame, group_col: str, title: str,
                  xlabel: str, filename: str, color=PALETTE_PRIMARY,
                  rotation: int = 0, figsize=(8, 4.5)):
    """Crea un gráfico individual, lo guarda como PNG y cierra la figura."""
    labels = [str(v) for v in table[group_col].to_list()]
    values = table["churn_rate"].to_list()
    volumes = table["usuarios"].to_list()

    fig, ax = plt.subplots(figsize=figsize)
    _bar_chart(ax, labels, values, volumes, color, title, xlabel, rotation=rotation)
    fig.tight_layout()

    out = PROJECT_DIR / "plots" / filename
    fig.savefig(out)
    plt.close(fig)
    print(f"  Guardado → {out}")


# ── Gráfico 1: Churn por Fecha de Instalación ──
print("Generando gráficos...\n")
plot_and_save(
    tbl_date, "install_date",
    title="Tasa de Churn D1 por Fecha de Instalación (hora local ART)",
    xlabel="Fecha de instalación (UTC-3)",
    filename="churn_by_install_date.png",
    rotation=45, figsize=(12, 5),
)

# ── Gráfico 2: Churn por Weekend Day+1 ──
# Relabelar para claridad ejecutiva
tbl_wknd_plot = tbl_wknd.with_columns(
    pl.when(pl.col("is_weekend_day1") == 1)
    .then(pl.lit("Sí (Sáb/Dom)"))
    .otherwise(pl.lit("No (Lun-Vie)"))
    .alias("weekend_label")
)
plot_and_save(
    tbl_wknd_plot, "weekend_label",
    title="Tasa de Churn D1 — ¿El día +1 es fin de semana?",
    xlabel="Día siguiente es fin de semana",
    filename="churn_by_weekend_day1.png",
    color=PALETTE_WEEKEND[0],
    figsize=(6, 4.5),
)

# ── Gráfico 3: Churn por Franja Horaria ──
# Orden lógico de las franjas
tod_order = ["Madrugada", "Mañana", "Tarde", "Noche"]
tbl_tod_sorted = tbl_tod.filter(
    pl.col("time_of_day").is_in(tod_order)
).sort(
    pl.col("time_of_day").cast(pl.Utf8).replace_strict(
        {v: str(i) for i, v in enumerate(tod_order)}
    )
)
plot_and_save(
    tbl_tod_sorted, "time_of_day",
    title="Tasa de Churn D1 por Franja Horaria",
    xlabel="Franja horaria (UTC-3)",
    filename="churn_by_time_of_day.png",
)

# ── Gráfico 4: Churn por Segmento de Edad ──
plot_and_save(
    tbl_age, "age_segment",
    title="Tasa de Churn D1 por Segmento de Edad",
    xlabel="Segmento etario",
    filename="churn_by_age_segment.png",
    rotation=25,
)

# ── Gráfico 5: Churn por Plataforma ──
tbl_platform = agg_churn(df, "platform")
print(f"{'=' * 60}")
print(f"  Churn por platform")
print(f"{'=' * 60}")
print(tbl_platform)
print()

plot_and_save(
    tbl_platform, "platform",
    title="Tasa de Churn D1 por Plataforma",
    xlabel="Plataforma",
    filename="churn_by_platform.png",
    figsize=(6, 4.5),
)

# ── Gráfico 6: Churn por Volumen de Interacción (total_events binned) ──
df_binned = df.with_columns(
    pl.when(pl.col("total_events") <= 10)
    .then(pl.lit("0-10"))
    .when(pl.col("total_events") <= 50)
    .then(pl.lit("11-50"))
    .when(pl.col("total_events") <= 150)
    .then(pl.lit("51-150"))
    .otherwise(pl.lit("+150"))
    .alias("total_events_bin")
)

bin_order = ["0-10", "11-50", "51-150", "+150"]
tbl_events_bin = agg_churn(df_binned, "total_events_bin")
# Ordenar respetando la progresión lógica de los rangos
tbl_events_bin = tbl_events_bin.with_columns(
    pl.col("total_events_bin").replace_strict(
        {v: str(i) for i, v in enumerate(bin_order)}
    ).alias("_sort_key")
).sort("_sort_key").drop("_sort_key")

print(f"{'=' * 60}")
print(f"  Churn por total_events (binned)")
print(f"{'=' * 60}")
print(tbl_events_bin)
print()

plot_and_save(
    tbl_events_bin, "total_events_bin",
    title="Tasa de Churn D1 por Volumen de Interacción",
    xlabel="Total de eventos (agrupado)",
    filename="churn_by_total_events.png",
    figsize=(8, 4.5),
)

# ── Gráfico 7: Churn por Descubrimiento de Eventos (barras agrupadas) ──
# Calcular churn rate para cada has_done_event_X, agrupando por flag (0/1)
event_discovery_data = []
for i in range(1, 6):
    col_name = f"has_done_event_{i}"
    agg = (
        df.lazy()
        .group_by(col_name)
        .agg(
            pl.len().alias("usuarios"),
            (pl.col(TARGET).mean() * 100).alias("churn_rate"),
        )
        .collect()
        .sort(col_name)
    )
    for row in agg.iter_rows(named=True):
        event_discovery_data.append({
            "event": f"Event {i}",
            "group": "Interactuó" if row[col_name] == 1 else "No interactuó",
            "churn_rate": row["churn_rate"],
            "usuarios": row["usuarios"],
        })

tbl_discovery = pl.DataFrame(event_discovery_data)

print(f"{'=' * 60}")
print(f"  Churn por descubrimiento de eventos")
print(f"{'=' * 60}")
print(tbl_discovery)
print()

# Gráfico de barras agrupadas
import numpy as np

events = [f"Event {i}" for i in range(1, 6)]
no_inter = tbl_discovery.filter(pl.col("group") == "No interactuó")
si_inter = tbl_discovery.filter(pl.col("group") == "Interactuó")

x = np.arange(len(events))
bar_width = 0.32

fig, ax = plt.subplots(figsize=(11, 5))

bars_no = ax.bar(x - bar_width / 2,
                 no_inter["churn_rate"].to_list(),
                 width=bar_width, color="#94A3B8", edgecolor="white",
                 linewidth=0.8, label="No interactuó", zorder=3)
bars_si = ax.bar(x + bar_width / 2,
                 si_inter["churn_rate"].to_list(),
                 width=bar_width, color=PALETTE_PRIMARY, edgecolor="white",
                 linewidth=0.8, label="Interactuó", zorder=3)

# Etiquetas con porcentaje + volumen
for bar, val, vol in zip(bars_no,
                         no_inter["churn_rate"].to_list(),
                         no_inter["usuarios"].to_list()):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
            f"{val:.1f}%\n(n={vol:,})", ha="center", va="bottom", fontsize=8,
            fontweight="semibold", color="#333333")

for bar, val, vol in zip(bars_si,
                         si_inter["churn_rate"].to_list(),
                         si_inter["usuarios"].to_list()):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
            f"{val:.1f}%\n(n={vol:,})", ha="center", va="bottom", fontsize=8,
            fontweight="semibold", color="#333333")

all_vals = no_inter["churn_rate"].to_list() + si_inter["churn_rate"].to_list()
ax.set_ylim(0, max(all_vals) * 1.25 if all_vals else 1)
ax.set_title("Tasa de Churn D1 — Descubrimiento de Eventos", pad=14,
             fontsize=14, fontweight="bold", color="#1A1A2E")
ax.set_xlabel("Evento", labelpad=8, color="#555555")
ax.set_ylabel("Tasa de Churn (%)", labelpad=8, color="#555555")
ax.set_xticks(x)
ax.set_xticklabels(events)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
ax.legend(loc="upper right", framealpha=0.9, edgecolor="#CCCCCC")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()

out = PROJECT_DIR / "plots" / "churn_by_events_discovery.png"
fig.savefig(out)
plt.close(fig)
print(f"  Guardado → {out}")

print("\n✅ EDA bivariado completo. 7 gráficos generados.")
