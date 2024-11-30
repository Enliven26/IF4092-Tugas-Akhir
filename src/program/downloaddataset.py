import logging
import os

from datasets import Dataset, concatenate_datasets, load_dataset

DATASET_DIRECTORY = os.path.join("data", "datageneration", "datasets")
DATASET_PATH = os.path.join(DATASET_DIRECTORY, "dataset.parquet")
DATASET_CHUNK_NAME_PREFIX = "dataset_"
MAX_CHUNK_SIZE_MB = 40


def download_dataset(dataset_path: str):
    logging.info("Downloading dataset...")

    dataset_dir = os.path.dirname(dataset_path)
    os.makedirs(dataset_dir, exist_ok=True)

    dataset = load_dataset("JetBrains-Research/commit-chronicle")

    filtered_train = dataset["train"].filter(lambda x: x["language"] == "Kotlin")
    filtered_train.to_parquet(dataset_path)

    logging.info(f"Dataset saved to {dataset_path}")


def create_dataset_from_chunks(dataset_dir: str, output_path: str):
    logging.info("Combining dataset chunks...")

    parquet_files = [
        os.path.join(dataset_dir, f)
        for f in os.listdir(dataset_dir)
        if (
            os.path.basename(f).startswith(DATASET_CHUNK_NAME_PREFIX)
            and f.endswith(".parquet")
        )
    ]

    datasets: list[Dataset] = [
        Dataset.from_parquet(parquet_file) for parquet_file in parquet_files
    ]

    combined_dataset = concatenate_datasets(datasets)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    combined_dataset.to_parquet(output_path)

    logging.info(f"Combined dataset saved to {output_path}")


def create_dataset_chunks(dataset_path: str, output_dir: str, chunk_size_mb: int):
    logging.info("Creating dataset chunks...")

    os.makedirs(output_dir, exist_ok=True)

    dataset = Dataset.from_parquet(dataset_path)

    approx_rows_per_chunk = max(
        1,
        int((chunk_size_mb * 1024 * 1024) / (dataset.download_size / dataset.num_rows)),
    )

    num_chunks = (dataset.num_rows + approx_rows_per_chunk - 1) // approx_rows_per_chunk
    logging.info(f"Saving dataset in {num_chunks} chunks...")

    for i in range(num_chunks):
        chunk = dataset.shard(num_shards=num_chunks, index=i, contiguous=True)
        chunk_path = os.path.join(
            output_dir, f"{DATASET_CHUNK_NAME_PREFIX}{i + 1}.parquet"
        )
        chunk.to_parquet(chunk_path)
        logging.info(f"Saved chunk {i + 1} to {chunk_path}")


def main():
    logging.basicConfig(level=logging.INFO)

    first_chuck_path = os.path.join(
        DATASET_DIRECTORY, DATASET_CHUNK_NAME_PREFIX + "1.parquet"
    )

    is_first_chunk_exist = os.path.exists(first_chuck_path)

    if is_first_chunk_exist:
        logging.info(f"Dataset already exists in chunks in {DATASET_DIRECTORY}")

    if os.path.exists(DATASET_PATH):
        if is_first_chunk_exist:
            logging.info(f"Combined dataset already exists in {DATASET_PATH}")
            return

        create_dataset_chunks(DATASET_PATH, DATASET_DIRECTORY, MAX_CHUNK_SIZE_MB)

        return

    if is_first_chunk_exist:
        create_dataset_from_chunks(DATASET_DIRECTORY, DATASET_PATH)

    else:
        download_dataset(DATASET_PATH)
        create_dataset_chunks(DATASET_PATH, DATASET_DIRECTORY, MAX_CHUNK_SIZE_MB)


if __name__ == "__main__":
    main()
