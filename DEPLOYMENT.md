# WorkGuard - Deployment Guide

To make the app accessible to **anyone** (not just on your Mac), you need to publish it online. The easiest way is **Streamlit Community Cloud** (Free).

## Prerequisites
- A GitHub Account.
- Your Code pushed to a GitHub Repository.

## Steps to Deploy

### 1. Push to GitHub
1.  Create a new Repository on GitHub (e.g., `workguard-app`).
2.  Upload your files:
    - `app.py`
    - `requirements.txt`
    - `.gitignore`
    - (DO NOT upload `secrets.toml` or `.env`)

### 2. Connect to Streamlit Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"New App"**.
3.  Select your GitHub Repository (`workguard-app`).
4.  Click **"Deploy!"**.

### 3. Configure Secrets (CRITICAL)
Your app will fail initially because the cloud doesn't have your keys.
1.  In your deployed app, click on the **Settings** menu (bottom right).
2.  Go to **"Secrets"**.
3.  Paste the content of your local `secrets.toml` there:
    ```toml
    private_key = "YOUR_PRIVATE_KEY"
    ```
4.  Save. The app will restart and automatically grab the key.

## Result
You will get a URL like `https://workguard.streamlit.app` that you can send to **anyone**. They can upload files, pay via QR Code, and your "Company Wallet" will handle the transactions in the background.
