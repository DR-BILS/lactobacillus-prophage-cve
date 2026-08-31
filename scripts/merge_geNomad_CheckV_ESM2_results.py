# Run this in your Colab session (variables meta_df, checkv_df, genomad_df, prot_df,
# esm2_df already exist from the earlier cells) to produce ONE correct master table.

import pandas as pd

# --- fix: group by accession + prophage_id, not prophage_id alone ---
protein_summary = prot_df.groupby(["accession", "prophage_id"]).agg(
    n_proteins=("protein_id", "count"),
    n_hypothetical=("is_hypothetical", "sum"),
).reset_index()
protein_summary["pct_hypothetical"] = (
    protein_summary["n_hypothetical"] / protein_summary["n_proteins"] * 100
).round(1)

esm2_summary = esm2_df.groupby(["accession", "prophage_id"]).agg(
    n_resolved_high=("confidence", lambda x: (x == "high").sum()),
    n_resolved_medium=("confidence", lambda x: (x == "medium").sum()),
    n_resolved_low=("confidence", lambda x: (x == "low").sum()),
).reset_index()

# --- one master table, with robust geNomad header normalization ---
# geNomad can append a |provirus_<id> suffix to some sequence headers.
# PhiSpy headers do not contain this suffix, so normalize before merging.
def normalize_header(x):
    if pd.isna(x):
        return x
    x = str(x).strip()
    return x.split("|provirus_", 1)[0]

master = meta_df.copy()
master["_merge_header"] = master["header"].map(normalize_header)

# `genomad_df` should contain the viral summary; `plasmid_df` is optional but
# recommended so the final table explicitly distinguishes plasmid from unresolved calls.
plasmid_df = globals().get("plasmid_df", globals().get("genomad_plasmid_df", pd.DataFrame()))

if not genomad_df.empty:
    g = genomad_df.rename(columns={genomad_df.columns[0]: "header"}).copy()
    g["_merge_header"] = g["header"].map(normalize_header)
    g = g.add_prefix("genomad_").rename(columns={"genomad__merge_header": "_merge_header"})
    master = master.merge(g, on="_merge_header", how="left")
master["genomad_call"] = "unclassified"
if "genomad_virus_score" in master:
    master.loc[master["genomad_virus_score"].notna(), "genomad_call"] = "virus"
if not plasmid_df.empty:
    pld = plasmid_df.rename(columns={plasmid_df.columns[0]: "header"}).copy()
    pld["_merge_header"] = pld["header"].map(normalize_header)
    pld["_plasmid_call"] = "plasmid"
    pld = pld[["_merge_header", "_plasmid_call"]].drop_duplicates("_merge_header")
    master = master.merge(pld, on="_merge_header", how="left")
    master.loc[master["genomad_call"].eq("unclassified") & master["_plasmid_call"].eq("plasmid"), "genomad_call"] = "plasmid"
    master = master.drop(columns=["_plasmid_call"], errors="ignore")
master["genomad_confirmed"] = master["genomad_call"].eq("virus")

checkv = checkv_df.rename(columns={checkv_df.columns[0]: "header"}).copy()
checkv["_merge_header"] = checkv["header"].map(normalize_header)
checkv = checkv.add_prefix("checkv_").rename(columns={"checkv__merge_header": "_merge_header"})
master = master.merge(checkv, on="_merge_header", how="left")

master = master.merge(protein_summary, on=["accession", "prophage_id"], how="left")
master = master.merge(esm2_summary, on=["accession", "prophage_id"], how="left")

for col in ["n_resolved_high", "n_resolved_medium", "n_resolved_low"]:
    master[col] = master[col].fillna(0).astype(int)

master = master.drop(columns=["_merge_header"], errors="ignore")
master.to_csv(f"{OUT}/MASTER_prophage_validation_table.csv", index=False)
print(f"Master table: {master.shape[0]} rows x {master.shape[1]} columns")
print("geNomad calls:", master["genomad_call"].value_counts(dropna=False).to_dict() if "genomad_call" in master else "see genomad_virus_score")
assert len(master) == 65, "Expected 65 prophage regions"
assert master["genomad_call"].eq("virus").sum() == 44, "Expected 44 geNomad-confirmed viral regions"
assert master["genomad_call"].eq("plasmid").sum() == 14, "Expected 14 plasmid-classified regions"
assert master["genomad_call"].eq("unclassified").sum() == 7, "Expected 7 unresolved regions"

# sanity check the bug is actually fixed -- these two pp1 rows should now differ
display(master[master["prophage_id"] == "pp1"][["accession", "length", "n_proteins", "n_hypothetical"]].head())
