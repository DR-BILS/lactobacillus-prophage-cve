#!/usr/bin/env bash
# Downloads all 20 genome assemblies (FASTA + GenBank annotation) used in this study
# directly from NCBI, using the official NCBI Datasets command-line tool.
#
# Install NCBI Datasets CLI first if you don't have it:
#   curl -o datasets 'https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/datasets'
#   chmod +x datasets
#
# Usage: ./download_genomes.sh [output_dir]

set -euo pipefail
OUTDIR="${1:-Final_Genomes}"
mkdir -p "$OUTDIR"

ACCESSIONS_CSV="$(dirname "$0")/../data/genome_accessions.csv"
tail -n +2 "$ACCESSIONS_CSV" | cut -d',' -f1 | while read -r acc; do
    echo ">>> Downloading $acc ..."
    datasets download genome accession "$acc" \
        --include genome,gbff \
        --filename "${OUTDIR}/${acc}.zip"
    unzip -o -q "${OUTDIR}/${acc}.zip" -d "${OUTDIR}/${acc}_raw"
    mkdir -p "${OUTDIR}/${acc}"
    find "${OUTDIR}/${acc}_raw" -name "*.fna" -exec cp {} "${OUTDIR}/${acc}/genomic.fna" \;
    find "${OUTDIR}/${acc}_raw" -name "*.gbff" -exec cp {} "${OUTDIR}/${acc}/genomic.gbff" \;
    rm -rf "${OUTDIR}/${acc}_raw" "${OUTDIR}/${acc}.zip"
done

echo "Done. Genomes are in ${OUTDIR}/<accession>/{genomic.fna,genomic.gbff}"
