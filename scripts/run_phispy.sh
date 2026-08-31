#!/usr/bin/env bash
# Runs PhiSpy v5.0.10 on every downloaded genome to (re)generate the prophage
# coordinate files already provided in data/coordinates/.
#
# Requires: pip install phispy  (or conda install -c bioconda phispy)
#
# Usage: ./run_phispy.sh [genomes_dir] [output_dir]

set -euo pipefail
GENOMES_DIR="${1:-Final_Genomes}"
OUT_DIR="${2:-PhiSpy_Results}"
mkdir -p "$OUT_DIR"

for acc_dir in "$GENOMES_DIR"/*/; do
    acc=$(basename "$acc_dir")
    echo ">>> Running PhiSpy on $acc ..."
    mkdir -p "${OUT_DIR}/${acc}"
    PhiSpy.py "${acc_dir}/genomic.gbff" \
        -o "${OUT_DIR}/${acc}" \
        --output_choice 512
    # PhiSpy writes prophage_coordinates.tsv; rename for consistency with data/coordinates/
    mv "${OUT_DIR}/${acc}/prophage_coordinates.tsv" "${OUT_DIR}/${acc}/${acc}_prophage_coordinates.tsv" 2>/dev/null || true
done

echo "Done. Coordinates are in ${OUT_DIR}/<accession>/<accession>_prophage_coordinates.tsv"
