"""Run dataset preprocessing over the manifests to produce cache."""
import time
from src.pipeline.preprocess import preprocess_manifest_files

if __name__ == "__main__":
    print("Starting trace dataset preprocessing...")
    t0 = time.time()
    df = preprocess_manifest_files(sample_rows_per_file=1000)
    print(f"Preprocessing completed in {round(time.time() - t0, 2)}s.")
    print(f"Processed {len(df)} files/channels. Total records sampled: {df['record_count'].sum()}")
