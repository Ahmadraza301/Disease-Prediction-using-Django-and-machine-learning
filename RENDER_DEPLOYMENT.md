# Deploy to Render.com

## Quick Deployment Steps

### 1. Render Configuration

When creating your web service on Render, use these settings:

**Build Command:**
```bash
./build.sh
```

**Start Command:**
```bash
gunicorn disease_prediction.wsgi:application
```

**Environment Variables:**
Add these in the Render dashboard:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.13.6` |
| `DEBUG` | `False` |

### 2. After Deployment

Once deployed, you'll need to create a superuser:

1. Go to your Render dashboard
2. Click on your service
3. Go to "Shell" tab
4. Run: `python manage.py createsuperuser`
5. Follow the prompts

### 3. Access Your App

- **Main App:** `https://your-app-name.onrender.com/`
- **Admin Panel:** `https://your-app-name.onrender.com/admin/`

### 4. Important Notes

- Free tier sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Database is SQLite (stored on disk, persists between deploys)
- Static files are served via WhiteNoise

### 5. Troubleshooting

If deployment fails:
1. Check the build logs in Render dashboard
2. Ensure all files are pushed to GitHub
3. Verify build.sh has execute permissions
4. Check that requirements.txt includes all dependencies

### 6. Local Development

To run locally with production settings:
```bash
DEBUG=True python manage.py runserver
```

To test production mode locally:
```bash
DEBUG=False python manage.py runserver --insecure
```

---

**Your app is ready for deployment!** 🚀
