# Grathr Daily Login — GitHub Actions

Logs into Grathr automatically every **Monday–Friday at 9:00 AM IST**.  
Runs 100% in the cloud — no laptop, no phone, nothing needs to be on.

---

## Setup (one-time, ~5 minutes)

### Step 1 — Create a GitHub account
Go to https://github.com and sign up (free).

---

### Step 2 — Create a new repository
1. Click the **+** button (top right) → **New repository**
2. Name it anything, e.g. `grathr-bot`
3. Set it to **Private** (so your credentials stay safe)
4. Click **Create repository**

---

### Step 3 — Upload the files
Upload these two files to your repo:
- `login.py` → root of the repo
- `.github/workflows/daily-login.yml` → exactly this folder path

You can drag-and-drop them on the GitHub website.

---

### Step 4 — Add your credentials as Secrets
GitHub Secrets keep your password safe — they're never visible after saving.

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add:
   - Name: `GRATHR_USERNAME` → Value: your Grathr email
   - Name: `GRATHR_PASSWORD` → Value: your Grathr password

---

### Step 5 — Done! ✅
GitHub Actions will now run automatically every weekday at 9:00 AM IST.

---

## Test it manually
To trigger a login right now without waiting:
1. Go to your repo → **Actions** tab
2. Click **Grathr Daily Login** → **Run workflow** → **Run workflow**

---

## Check if it worked
- Go to **Actions** tab in your repo
- A green ✅ = login succeeded
- A red ❌ = something failed (click it to see the log)

---

## Troubleshooting
If login fails, the most likely cause is that Grathr's HTML selectors differ.  
Open `login.py` and update these lines to match Grathr's actual form:
```python
USERNAME_SELECTOR = 'input[name="email"]'
PASSWORD_SELECTOR = 'input[name="password"]'
SUBMIT_SELECTOR   = 'button[type="submit"]'
SUCCESS_URL_PART  = "/dashboard"
```
To find the right selectors: open Grathr's login page in Chrome →
right-click the email field → **Inspect** → look at the `name` or `id` attribute.
