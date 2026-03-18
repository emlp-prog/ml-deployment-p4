import os
from pathlib import Path

from huggingface_hub import HfApi


def main():
    hf_token = os.getenv("HF_TOKEN")
    hf_space_id = os.getenv("HF_SPACE_ID")

    if not hf_token:
        raise RuntimeError("HF_TOKEN is required to deploy to Hugging Face Spaces.")
    if not hf_space_id:
        raise RuntimeError("HF_SPACE_ID is required and must look like 'username/space-name'.")

    repo_root = Path(__file__).resolve().parents[1]
    api = HfApi(token=hf_token)
    api.upload_folder(
        repo_id=hf_space_id,
        repo_type="space",
        folder_path=str(repo_root),
        path_in_repo=".",
        commit_message=os.getenv("HF_COMMIT_MESSAGE", "Deploy from GitHub Actions"),
        ignore_patterns=[
            "venv/**",
            ".venv/**",
            "__pycache__/**",
            ".pytest_cache/**",
            ".coverage",
            "htmlcov/**",
            ".git/**",
            ".github/**",
            ".env",
            "*.db",
            "data/ml_api.db",
        ],
    )
    print(f"Deployment pushed to Hugging Face Space: {hf_space_id}")


if __name__ == "__main__":
    main()
