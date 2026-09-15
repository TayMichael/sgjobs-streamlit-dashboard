# ============================================================
# PREPARE SGJOBS STREAMLIT DEPLOYMENT DATA
# WSL-SAFE VERSION
# ============================================================
#
# Run from:
#   conda activate pds
#   cd /mnt/c/SGJob_Project/streamlit_deploy
#   python prepare_deploy_data.py
#
# This script:
# - DOES NOT modify C:\SGJob_Project\output_v3
# - Copies the main V3 Parquet into ./data
# - Converts the two V3 bridge CSVs into Parquet inside ./data
#
# ============================================================

from pathlib import Path
import shutil
import gc

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

PROJECT_ROOT = Path("/mnt/c/SGJob_Project")
SOURCE_DIR = PROJECT_ROOT / "output_v3"

DEPLOY_DIR = Path(__file__).resolve().parent
DATA_DIR = DEPLOY_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

MAIN_SRC = SOURCE_DIR / "sgjob_v3_clean_features.parquet"
CATEGORY_SRC = SOURCE_DIR / "sgjob_v3_category_bridge.csv"
SKILL_SRC = SOURCE_DIR / "sgjob_v3_skill_bridge.csv"

MAIN_OUT = DATA_DIR / "sgjob_v3_clean_features.parquet"
CATEGORY_OUT = DATA_DIR / "sgjob_v3_category_bridge.parquet"
SKILL_OUT = DATA_DIR / "sgjob_v3_skill_bridge.parquet"

CHUNK_SIZE = 100_000


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def copy_main_parquet():
    if not MAIN_SRC.exists():
        raise FileNotFoundError(
            f"Main Parquet not found:\n{MAIN_SRC}"
        )

    shutil.copy2(
        MAIN_SRC,
        MAIN_OUT,
    )

    print(
        f"Copied main Parquet:\n"
        f"  {MAIN_OUT}\n"
    )


def csv_to_parquet(csv_path, parquet_path, columns):
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Bridge CSV not found:\n{csv_path}"
        )

    if parquet_path.exists():
        parquet_path.unlink()

    writer = None
    schema = None
    total_rows = 0

    try:
        for chunk_no, chunk in enumerate(
            pd.read_csv(
                csv_path,
                usecols=columns,
                chunksize=CHUNK_SIZE,
                low_memory=True,
            ),
            start=1,
        ):
            table = pa.Table.from_pandas(
                chunk,
                preserve_index=False,
            )

            if writer is None:
                schema = table.schema
                writer = pq.ParquetWriter(
                    parquet_path,
                    schema,
                    compression="snappy",
                    use_dictionary=True,
                )
            else:
                table = table.cast(
                    schema,
                    safe=False,
                )

            writer.write_table(table)
            total_rows += len(chunk)

            print(
                f"{csv_path.name} | "
                f"chunk {chunk_no:>3} | "
                f"cumulative {total_rows:,}"
            )

            del chunk, table
            gc.collect()

    finally:
        if writer is not None:
            writer.close()

    pf = pq.ParquetFile(parquet_path)

    if pf.metadata.num_rows != total_rows:
        raise RuntimeError(
            f"Row-count validation failed for {parquet_path.name}"
        )

    print(
        f"\nCreated:\n"
        f"  {parquet_path}\n"
        f"Rows: {pf.metadata.num_rows:,}\n"
        f"Columns: {pf.metadata.num_columns:,}\n"
    )


# ------------------------------------------------------------
# Run
# ------------------------------------------------------------

print("=" * 72)
print("PREPARING STREAMLIT DEPLOYMENT DATA")
print("=" * 72)

print(f"\nSource folder:\n  {SOURCE_DIR}")
print(f"\nDeployment data folder:\n  {DATA_DIR}\n")

copy_main_parquet()

csv_to_parquet(
    CATEGORY_SRC,
    CATEGORY_OUT,
    [
        "job_post_id",
        "category_name",
    ],
)

csv_to_parquet(
    SKILL_SRC,
    SKILL_OUT,
    [
        "job_post_id",
        "skill_name",
    ],
)

print("=" * 72)
print("DEPLOYMENT DATA READY")
print("=" * 72)

print("\nKeep these three files in the data folder:")
print(f"  {MAIN_OUT.name}")
print(f"  {CATEGORY_OUT.name}")
print(f"  {SKILL_OUT.name}")
