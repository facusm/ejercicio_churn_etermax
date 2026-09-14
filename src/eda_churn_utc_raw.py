import sys
from pathlib import Path
import polars as pl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

def main():
    PROJECT_DIR = Path(__file__).resolve().parent.parent
    DATA_PATH = PROJECT_DIR / "data" / "dataset_raw.csv"
    PLOT_PATH = PROJECT_DIR / "plots" / "churn_by_install_date_UTC.png"
    
    print(f"Leyendo dataset crudo desde: {DATA_PATH}")
    
    # Lectura cruda (sin offset, sin limpiar filas)
    df = pl.read_csv(DATA_PATH)
    df = df.with_columns(
        pl.col("install_time").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S", strict=False)
    )
    
    # Extraemos solo la fecha UTC
    df = df.with_columns(
        pl.col("install_time").dt.date().alias("install_date")
    )
    
    # Agregación para obtener tasa de churn y volumetría
    agg = (
        df.group_by("install_date")
        .agg([
            pl.len().alias("usuarios"),
            (pl.col("target_churn_indicator").mean() * 100).alias("churn_rate")
        ])
        .sort("install_date")
    )
    
    print("Resultados crudos por fecha:")
    print(agg)
    
    # Visualización
    # Filtramos nulos (por si la conversión de fecha falló en alguna fila)
    agg = agg.drop_nulls("install_date")
    
    labels = [str(d) for d in agg["install_date"].to_list()]
    values = agg["churn_rate"].to_list()
    volumes = agg["usuarios"].to_list()
    
    plt.figure(figsize=(12, 6))
    
    # Azul neutro uniforme
    bars = plt.bar(labels, values, color="#3A86FF", edgecolor="white", width=0.6, linewidth=1, zorder=3)
    
    for bar, val, vol in zip(bars, values, volumes):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                 f"{val:.1f}%\n(n={vol:,})", ha="center", va="bottom", fontsize=9,
                 color="#333333", fontweight="semibold")
                 
    # Configuración de ejes y estética
    # Límite Y mínimo 110% para no cortar barras anómalas
    plt.ylim(0, max(110.0, max(values) * 1.2))
    
    plt.title("Tasa de Churn D1 por Fecha de Instalación (UTC crudo)", pad=15, fontsize=14, fontweight="bold", color="#1A1A2E")
    plt.xlabel("Fecha de instalación (UTC crudo)", labelpad=10, color="#555555")
    plt.ylabel("Tasa de Churn (%)", labelpad=10, color="#555555")
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    
    plt.grid(axis="y", linestyle="--", alpha=0.6, zorder=0)
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    
    plt.tight_layout()
    PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(PLOT_PATH, dpi=200, bbox_inches="tight")
    plt.close()
    
    print(f"\nGráfico guardado exitosamente en: {PLOT_PATH}")

if __name__ == "__main__":
    main()
