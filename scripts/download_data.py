"""
Download the (small) precomputed supplementary tables the tool needs.
Public data, MIT-licensed, from the dataset authors' analysis repo.

    python scripts/download_data.py

The full genome-scale AnnData (~22M cells) is NOT needed — we use the authors'
precomputed enrichment + QC tables. For the GRN-edge detail (optional, later),
grab GWCD4i.DE_stats.h5ad via the CZI Virtual Cells Platform:
    vcp data search "Primary Human CD4+ T Cell Perturb-seq" --exact
"""
import urllib.request
from pathlib import Path

BASE = ("https://raw.githubusercontent.com/emdann/"
        "GWT_perturbseq_analysis_2025/master/metadata/suppl_tables")

FILES = {
    "cluster_autoimmune_enrichment_results.csv": "cluster_autoimmune_enrichment_results.suppl_table.csv",
    "guide_kd_efficiency.csv": "guide_kd_efficiency.suppl_table.csv",
    "sgrna_library_metadata.csv": "sgrna_library_metadata.suppl_table.csv",
    "Th2_Th1_polarization_signature_DE_results_full.csv": "Th2_Th1_polarization_signature_DE_results_full.suppl_table.csv",
}

def main() -> None:
    out = Path(__file__).resolve().parent.parent / "data"
    out.mkdir(exist_ok=True)
    for local, remote in FILES.items():
        dest = out / local
        if dest.exists():
            print(f"✓ {local} (already present)")
            continue
        print(f"↓ {local} …", flush=True)
        urllib.request.urlretrieve(f"{BASE}/{remote}", dest)
    print("Done. Now run:  streamlit run app.py")

if __name__ == "__main__":
    main()
