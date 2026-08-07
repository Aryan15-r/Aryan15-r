# GitHub Profile Automated Setup Checklist

Follow these exact steps to complete deployment of your automated GitHub profile for **Aryan15-r**:

---

## 1. Create the Special Profile Repository
1. Go to [github.com/new](https://github.com/new)
2. Repository name: **`Aryan15-r`** (must match your username exactly)
3. Set to **Public**
4. Check **Add a README file**
5. Click **Create repository**

---

## 2. Commit & Push Profile Files
Copy the generated files from:
`E:\Aryan15-r`

Commit and push `README.md` and `.github/workflows/snake.yml` to your `Aryan15-r/Aryan15-r` main branch.

---

## 3. Enable GitHub Actions Permissions (For Snake Animation)
1. Go to `https://github.com/Aryan15-r/Aryan15-r/settings/actions`
2. Scroll to **Workflow permissions** at the bottom.
3. Select **Read and write permissions**
4. Click **Save**
5. Go to **Actions** tab -> **Generate Snake Animation** -> Click **Run workflow**.
   - This creates the `output` branch containing `github-snake.svg` and `github-snake-dark.svg`.

---

## 4. Self-Host GitHub Readme Stats (Free on Vercel)
1. Generate Classic GitHub Token:
   - Go to [github.com/settings/tokens](https://github.com/settings/tokens) -> **Tokens (classic)**
   - Click **Generate new token (classic)**
   - Expiration: **No expiration**
   - Select scope: **`repo`**
   - Copy token immediately.
2. Fork `anuraghazra/github-readme-stats`:
   - Go to [github.com/anuraghazra/github-readme-stats](https://github.com/anuraghazra/github-readme-stats) -> Click **Fork**.
3. Deploy on Vercel:
   - Go to [vercel.com](https://vercel.com) -> Sign in with GitHub.
   - Click **Add New...** -> **Project** -> Import `github-readme-stats` fork.
   - Under **Environment Variables**, add:
     - Key: `PAT_1`
     - Value: `(your classic token)`
   - Click **Deploy**.
4. Update `README.md`:
   - Replace `github-readme-stats.vercel.app` in `README.md` with your custom Vercel URL `your-instance.vercel.app`.

---

## 5. Dithered Terminal Portrait Banner (Phase 1)
- If you have your portrait image, place it in this folder.
- Run `python generate_banner.py` to compile `dark.svg` and `light.svg` and push them to your `main` branch.
