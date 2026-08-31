import os
import csv

input_dir = "CRISPR_Results"
output_file = "CRISPR_summary_20_genomes.tsv"

results = []

for genome in sorted(os.listdir(input_dir)):

    folder = os.path.join(input_dir, genome)

    if not os.path.isdir(folder):
        continue

    crispr_file = os.path.join(folder, "crisprs_all.tab")
    cas_file = os.path.join(folder, "cas_operons_putative.tab")

    crispr_arrays = 0
    spacers = 0
    cas_operons = 0
    cas_types = set()

    # CRISPR arrays and spacers
    if os.path.exists(crispr_file):
        with open(crispr_file) as f:
            lines = f.readlines()[1:]

            for line in lines:
                if line.strip():
                    crispr_arrays += 1
                    cols = line.strip().split("\t")
                    spacers += int(cols[5])

    # Cas systems
    if os.path.exists(cas_file):
        with open(cas_file) as f:
            lines = f.readlines()[1:]

            for line in lines:
                if line.strip():
                    cas_operons += 1
                    cols = line.strip().split("\t")
                    cas_types.add(cols[7])

    results.append([
        genome,
        crispr_arrays,
        spacers,
        cas_operons,
        ";".join(sorted(cas_types))
    ])


with open(output_file,"w",newline="") as f:

    writer = csv.writer(f,delimiter="\t")

    writer.writerow([
        "Genome",
        "CRISPR_arrays",
        "Spacer_count",
        "Cas_operons",
        "Cas_types"
    ])

    writer.writerows(results)


print("CRISPR summary generated:", output_file)
