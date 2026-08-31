# An integrated computational framework for profiling prophage and CRISPR architectures in probiotic *Lactobacillus*-related genomes

Reproducible code, data, and figures for a comparative genomics study of 65 candidate prophage regions across 20 probiotic/industrially-relevant *Lactobacillus*-related genomes spanning four genera.

PhiSpy predictions were treated as putative prophage regions rather than evidence of functional or inducible prophages. This repository independently evaluates all 65 PhiSpy-predicted regions using geNomad and CheckV, assigns putative functions to previously hypothetical prophage-associated proteins using ESM2, profiles CRISPR arrays and spacers, and evaluates host–phage relatedness using embedding-based comparative analyses and Mantel tests.

## Key findings

| Finding | Result |
|---|---|
| PhiSpy calls supported as viral sequences after independent validation | 44 / 65 (67.7%) — 14 classified as plasmid-derived, 7 unresolved |
| Confirmed-viral regions vs. rejected regions, mean CheckV completeness | 73.1% vs. 16.1% (plasmid) / 25.0% (unresolved) |
| Hypothetical prophage proteins resolved to a candidate function | 996 / 997 (high-confidence threshold); 27.7% to a clearly informative structural/mobility annotation |
| Cross-species prophage relatedness (network) | Well-supported link between an *L. paracasei* and an *L. rhamnosus* prophage |
| Host–phage cophylogeny, within *L. plantarum* (n=8) | Not significant (r=0.24, p=0.09) — inconclusive, underpowered |
| Host–phage cophylogeny, full panel (n=17, four genera) | **Significant** (r=0.47–0.50, p=0.002–0.005), robust to leave-one-out |

See `docs/METHODS.md` for full methodological detail and the stated limitations.

## Repository structure

```
.
├── data/
│   ├── genome_accessions.csv        # 20 NCBI accessions used in this study
│   ├── coordinates/                 # Raw PhiSpy prophage_coordinates.tsv, all 20 genomes
│   ├── processed/                   # Cross-validated master tables (see below)
│   ├── trees/                       # Core-genome (IQ-TREE) and 16S rRNA (FastTree) phylogenies
│   └── embeddings/                  # Raw ESM2 protein embeddings (2,591 proteins, .npz)
├── notebooks/                       # Google Colab-ready, GPU-accelerated analysis notebooks
├── scripts/                         # Genome download, PhiSpy run, CRISPR summary, data merge
├── figures/                         # All figures, regenerated and verified against raw data
└── docs/
    └── METHODS.md                   # Full methods writeup with tool versions
```

## Key data files

| File | Description |
|---|---|
| `data/processed/MASTER_prophage_validation_table.csv` | All 65 regions: PhiSpy coordinates + geNomad classification + CheckV quality tier |
| `data/processed/esm2_putative_function_calls.csv` | Candidate function for every previously-"hypothetical" prophage protein |
| `data/processed/CRISPR_summary_20_genomes.tsv` | Raw CRISPRCasTyper output: arrays, spacers, Cas operons per genome |
| `data/processed/genome_size_gc_verified.csv` | Genome size / GC%, computed directly from assembly FASTA |
| `data/processed/host_dist_20genome.csv`, `phage_dist_20genome.csv` | Distance matrices used in the full-panel Mantel test |
| `data/processed/spacer_prophage_high_confidence_table.csv` | The eight high-confidence spacer–prophage matches reported as Table 7 in the manuscript |

## Reproducing the analysis

All notebooks are designed to run on **Google Colab's free tier** (T4 GPU where needed) with no paid resources required.

1. **`notebooks/01_prophage_validation_geNomad_CheckV_ESM2.ipynb`** — full pipeline: extract regions → geNomad → CheckV → extract cargo proteins → ESM2 embed. Needs `Final_Genomes.zip` and `PhiSpy_Results.zip` (regenerate with `scripts/download_genomes.sh` + `scripts/run_phispy.sh`, or reconstruct `Final_Genomes` from `data/genome_accessions.csv` directly).
2. **`notebooks/02_regenerate_esm2_embeddings.ipynb`** — lightweight recovery notebook if you only need to re-embed proteins (skips geNomad/CheckV).
3. **`notebooks/03_cophylogeny_network_analysis.ipynb`** — builds the prophage relatedness network and runs the within-*L. plantarum* Mantel test. Needs `data/embeddings/esm2_embeddings.npz`, `data/processed/MASTER_prophage_validation_table.csv`, and `data/trees/core_gene_alignment_filtered_aln.treefile`.
4. **`notebooks/04_cophylogeny_20genome_16S.ipynb`** — builds the 16S rRNA tree from scratch and runs the full-panel Mantel test.

Local/offline dependencies are listed in `requirements.txt`. External bioinformatics tools (geNomad, CheckV, PhiSpy, CRISPRCasTyper, MAFFT, FastTree) are installed within the notebooks themselves — see `docs/METHODS.md` for exact versions and install commands.

### Why raw genome FASTA/GenBank files aren't included

The 20 genome assemblies (~100 MB combined) are large binary NCBI data and are not duplicated in this repository. Instead:
- `data/genome_accessions.csv` lists every accession used.
- `scripts/download_genomes.sh` fetches them directly from NCBI via the official Datasets CLI.
- The essential *derived* output needed for reproducibility — PhiSpy's `prophage_coordinates.tsv` per genome — **is** included in full (`data/coordinates/`, <10 KB total), so the rest of the pipeline can run without re-running PhiSpy at all if you just want to reproduce the downstream validation/network/cophylogeny results.

## Figures

Figures 1–9 correspond to the numbered figures in the manuscript. Additional analysis outputs are retained separately for reproducibility of the prophage-validation, relatedness, and Mantel analyses described in the manuscript. Figures were generated from the repository data and cross-checked against the reported numerical results.

## Citation

See `CITATION.cff`. If you use this code, data, or figures, please cite the associated publication (details to be added on acceptance) and, where relevant, the underlying tools: PhiSpy (Akhter et al. 2012), geNomad (Camargo et al. 2023), CheckV (Nayfach et al. 2021), ESM2 (Lin et al. 2023), CRISPRCasTyper (Russel et al. 2020).

## License

Code: MIT (see `LICENSE`). Data and figures: CC-BY-4.0. See `LICENSE` for details.
