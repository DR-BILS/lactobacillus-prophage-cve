# Methods

Detailed, reproducible methods for every analysis in this repository. Tool versions are pinned exactly as used.

## 1. Genome dataset

20 genome assemblies spanning four genera of probiotic/industrially-relevant *Lactobacillus*-related species (see `data/genome_accessions.csv` for the full accession list). Genomes and their RefSeq/GenBank annotations were downloaded from the NCBI Assembly database (`scripts/download_genomes.sh`).

## 2. Prophage prediction

PhiSpy v5.0.10 was run on each genome's `.gbff` annotation file (`scripts/run_phispy.sh`), producing per-genome `prophage_coordinates.tsv` files (provided pre-computed in `data/coordinates/`). This identified 65 candidate prophage regions across the 20 genomes.

## 3. Independent cross-validation (geNomad + CheckV)

All 65 PhiSpy-predicted regions were independently evaluated using two complementary tools:

- **geNomad v1.7.0** (`end-to-end` mode) — a deep-learning viral/plasmid classifier, trained on a curated marker-gene database rather than PhiSpy's compositional scoring. Output: `data/processed/prophage_regions_virus_summary.tsv` and `prophage_regions_plasmid_summary.tsv`.
- **CheckV v1.0.1** — estimates completeness and contamination against a reference database of known viral genomes, assigning a discrete quality tier (Complete / High-quality / Medium-quality / Low-quality / Not-determined).

Full pipeline: `notebooks/01_prophage_validation_geNomad_CheckV_ESM2.ipynb` (designed to run on a free-tier Google Colab T4 GPU instance).

**Result:** 44/65 regions (67.7%) were classified as viral; 14/65 (21.5%) were classified as plasmid-derived; and 7/65 (10.8%) remained unresolved. geNomad-confirmed regions averaged 73.1% CheckV completeness vs. 16.1% (plasmid) and 25.0% (unresolved).

## 4. Functional annotation of hypothetical prophage proteins (ESM2)

All coding sequences within a called prophage region (≥50% reciprocal overlap with PhiSpy coordinates) were extracted with their translations. Each protein was embedded using **ESM2** (`esm2_t12_35M_UR50D`; Lin et al. 2023) via mean-pooling of final-layer residue representations, producing one 480-dimensional vector per protein (`data/embeddings/esm2_embeddings.npz`, 2,591 proteins).

**Anisotropy correction:** raw ESM2 embeddings occupy a narrow region of vector space, which inflates cosine similarity between *any* two proteins toward a uniformly high value (empirically observed range: 0.96–1.00) regardless of true relatedness. This was corrected by subtracting the global mean vector across all 2,591 proteins before any similarity comparison (Mu & Viswanath, 2018, "All-but-the-Top"). This expanded the usable similarity range for downstream similarity analysis.

Each protein annotated only as "hypothetical protein" was assigned the product annotation of its nearest neighbour (by corrected cosine similarity) among proteins in the same dataset that already carried an informative annotation. High-confidence threshold: similarity ≥ 0.80.

Output: `data/processed/esm2_putative_function_calls.csv`.

## 5. Prophage relatedness network

For every pair of geNomad-confirmed prophages, a **reciprocal-best-hit similarity** was computed: for every protein in region A, its single best match in region B (and vice versa), averaged across all best-hit pairs. Region pairs in the top 5% of the resulting similarity distribution were connected in a network (`notebooks/03_cophylogeny_network_analysis.ipynb`).

## 6. Host–phage cophylogeny (Mantel tests)

Two tests, at two taxonomic scales:

1. **Within *L. plantarum* (n=8 strains)** — host distances from the existing core-genome phylogeny (`data/trees/core_gene_alignment_filtered_aln.treefile`, IQ-TREE). Result: Pearson r=0.24, p=0.09 (**inconclusive** — underpowered, not evidence against co-diversification).
2. **Full panel (n=17 genomes with ≥1 geNomad-confirmed prophage)** — host distances from a new 16S rRNA phylogeny spanning all 20 genomes across four genera (`data/trees/16S_tree.nwk`; MAFFT v7.505 L-INS-i alignment, FastTree v2.1.11 GTR model). Result: Pearson r=0.47–0.50, p=0.002–0.005; Spearman r=0.43, p=0.02; positive correlations were retained in all leave-one-out analyses (r=0.41–0.57).

Pipeline: `notebooks/04_cophylogeny_20genome_16S.ipynb`.

## 7. CRISPR/Cas profiling

CRISPRCasTyper (cctyper) v1.8.0 was run on all 20 genomes. Per-genome CRISPR array counts and spacer counts were aggregated with `scripts/generate_CRISPR_summary.py`, producing `data/processed/CRISPR_summary_20_genomes.tsv` (14 total arrays, 281 total spacers, 9/20 genomes CRISPR-positive).

## 8. Genome size / GC content

Computed directly from each genome's assembly FASTA (simple base-counting), not from any third-party tool — see `data/processed/genome_size_gc_verified.csv`.

## Known limitations

- The within-species Mantel test (n=8) is underpowered; treat as inconclusive, not negative evidence.
- 16S rRNA has limited resolution *within* a single species (several *L. plantarum* strains are an unresolved polytomy in the 16S tree) — it is the right tool for the cross-species test, not a replacement for the core-genome tree.
- ESM2 function-transfer calls above the 0.80 threshold should be read as candidate annotations, not confirmed function — many "high-confidence" calls reflect within-dataset strain relatedness rather than deep remote homology. We report the additional, more conservative "structurally informative annotation" rate (27.7%) alongside the raw resolution rate (99.9%) for this reason.
- The relatedness network contained two links between *L. paracasei* and *L. rhamnosus* prophage regions and a weaker link between an *L. reuteri* region and a low-quality, 39%-complete *L. gasseri* region. Sequence relatedness does not establish contemporary phage circulation or transmission.
