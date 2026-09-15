# SGJobs Streamlit Deployment Copy

This folder is a deployment-only copy. It does **not** replace the validated local `app.py`.

## Files

- `app_deploy.py` - cloud-friendly Streamlit app using repository-relative paths.
- `requirements.txt` - Python packages for Streamlit Community Cloud.
- `prepare_deploy_data.py` - copies/converts your existing V3 outputs into this folder's `data/` directory.
- `data/` - deployment data files go here.
- `.streamlit/config.toml` - basic cloud settings.

## 1. Prepare data on your Windows PC

From PowerShell or WSL, run the preparation script from this deployment folder. The script reads from `C:\SGJob_Project\output_v3` and does not modify those source files.

```bash
python prepare_deploy_data.py
```

Expected preferred deployment files:

```text
data/
├─ sgjob_v3_clean_features.parquet
├─ sgjob_v3_category_bridge.parquet
└─ sgjob_v3_skill_bridge.parquet
```

## 2. Test the deployment copy locally

```bash
streamlit run app_deploy.py
```

This uses only files inside this deployment folder.

## 3. GitHub repository structure

```text
sgjobs-streamlit-deploy/
├─ app_deploy.py
├─ requirements.txt
├─ prepare_deploy_data.py
├─ data/
│  ├─ sgjob_v3_clean_features.parquet
│  ├─ sgjob_v3_category_bridge.parquet
│  └─ sgjob_v3_skill_bridge.parquet
└─ .streamlit/
   └─ config.toml
```

## 4. Deploy on Streamlit Community Cloud

Connect the GitHub repository, select `app_deploy.py` as the app file, and deploy.

## Important

Keep your validated local file unchanged. This deployment copy deliberately uses `Path(__file__)` and a repository-relative `data/` directory instead of `/mnt/c/...`.
