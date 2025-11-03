╔══════════════════════════════════════════════════════════════╗
║   STREAMLIT CLOUD DEPLOYMENT WITH LOCAL API (NGROK)         ║
╚══════════════════════════════════════════════════════════════╝

This guide shows you how to deploy your Streamlit UI to Streamlit Cloud
while keeping the FastAPI backend running locally using ngrok tunneling.

═══════════════════════════════════════════════════════════════

📋 PREREQUISITES
═══════════════════════════════════════════════════════════════

✅ Code pushed to GitHub: https://github.com/Darish05/Migraine_CICD.git
✅ Streamlit app updated with configurable API_URL
✅ Local API running (via Jenkins or docker-compose)
✅ ngrok account (free tier is fine)

═══════════════════════════════════════════════════════════════

PART 1: SETUP NGROK TO EXPOSE LOCAL API
═══════════════════════════════════════════════════════════════

Step 1: Install ngrok
───────────────────────────────────────────────────────────────
# Download ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz

# Extract
tar xvzf ngrok-v3-stable-linux-amd64.tgz

# Move to bin
sudo mv ngrok /usr/local/bin/

# Verify
ngrok version


Step 2: Get ngrok Auth Token
───────────────────────────────────────────────────────────────
1. Go to: https://dashboard.ngrok.com/signup
2. Sign up (free account)
3. Go to: https://dashboard.ngrok.com/get-started/your-authtoken
4. Copy your authtoken


Step 3: Configure ngrok
───────────────────────────────────────────────────────────────
# Add your authtoken (replace YOUR_AUTHTOKEN)
ngrok config add-authtoken YOUR_AUTHTOKEN


Step 4: Start Local API (if not running)
───────────────────────────────────────────────────────────────
cd /home/rhemi/IA3/Dar_mlops/Migraine_CICD

# Start services via docker-compose
sudo docker-compose up -d

# Verify API is running
curl http://localhost:8000/health


Step 5: Expose API with ngrok
───────────────────────────────────────────────────────────────
# Start ngrok tunnel for port 8000
ngrok http 8000

# You'll see output like:
# Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000

# IMPORTANT: Copy the HTTPS URL (e.g., https://abc123.ngrok-free.app)
# This is your PUBLIC_API_URL


Step 6: Keep ngrok Running
───────────────────────────────────────────────────────────────
# ngrok must stay running for Streamlit Cloud to access your API
# Open a new terminal tab for next steps
# Keep this terminal with ngrok running!

═══════════════════════════════════════════════════════════════

PART 2: DEPLOY TO STREAMLIT CLOUD
═══════════════════════════════════════════════════════════════

Step 1: Go to Streamlit Cloud
───────────────────────────────────────────────────────────────
1. Visit: https://share.streamlit.io/
2. Sign in with GitHub


Step 2: Deploy New App
───────────────────────────────────────────────────────────────
1. Click "New app"

2. Fill in details:
   Repository: Darish05/Migraine_CICD
   Branch: main
   Main file path: streamlit_app.py

3. Click "Advanced settings"


Step 3: Configure Secrets
───────────────────────────────────────────────────────────────
In the "Secrets" section, paste:

API_URL = "https://YOUR-NGROK-URL.ngrok-free.app"

Example:
API_URL = "https://abc123.ngrok-free.app"

(Replace with YOUR actual ngrok URL from Step 5 above)


Step 4: Deploy
───────────────────────────────────────────────────────────────
1. Click "Deploy!"
2. Wait 2-3 minutes for deployment
3. Your app will be available at:
   https://YOUR-APP-NAME.streamlit.app/


Step 5: Test the Deployment
───────────────────────────────────────────────────────────────
1. Open your Streamlit Cloud URL
2. Check sidebar - should show "✅ API Online"
3. Try making a prediction
4. Should connect to your local API via ngrok!

═══════════════════════════════════════════════════════════════

📊 ARCHITECTURE
═══════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│                    INTERNET / USERS                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT CLOUD                                │
│  https://your-app.streamlit.app                            │
│  ┌─────────────────────────────────────────┐               │
│  │  streamlit_app.py                       │               │
│  │  (UI Only - No Backend)                 │               │
│  └─────────────────────────────────────────┘               │
└───────────────────────┬─────────────────────────────────────┘
                        │ API_URL
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    NGROK TUNNEL                             │
│  https://abc123.ngrok-free.app                             │
│  (Public endpoint)                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              YOUR LOCAL MACHINE                             │
│                                                             │
│  ┌──────────────────────────────────────┐                  │
│  │  FastAPI (Port 8000)                 │                  │
│  │  - /predict endpoint                 │                  │
│  │  - /health endpoint                  │                  │
│  │  - /models-info endpoint             │                  │
│  └──────────────────────────────────────┘                  │
│                                                             │
│  ┌──────────────────────────────────────┐                  │
│  │  MLflow (Port 5000)                  │                  │
│  │  - Model tracking                    │                  │
│  └──────────────────────────────────────┘                  │
│                                                             │
│  ┌──────────────────────────────────────┐                  │
│  │  ML Models (in Docker volumes)       │                  │
│  │  - 8 Classification models           │                  │
│  │  - 8 Regression models               │                  │
│  └──────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════

🔄 DEVELOPMENT WORKFLOW
═══════════════════════════════════════════════════════════════

1. Edit Code Locally
   ├─ Edit streamlit_app.py or app.py
   └─ Test locally at http://localhost:8501

2. Push to GitHub
   ├─ git add .
   ├─ git commit -m "Update feature"
   └─ git push origin main

3. Automatic Deployment
   └─ Streamlit Cloud auto-deploys on push!

4. Keep API Running
   ├─ Ensure docker-compose is running
   ├─ Keep ngrok tunnel active
   └─ API accessible via ngrok URL

═══════════════════════════════════════════════════════════════

⚠️  IMPORTANT NOTES
═══════════════════════════════════════════════════════════════

1. NGROK FREE TIER LIMITATIONS:
   - URL changes every time you restart ngrok
   - Update API_URL in Streamlit secrets after restart
   - Sessions expire after 2 hours (restart ngrok)
   
2. KEEP SERVICES RUNNING:
   - docker-compose must be running
   - ngrok must be running
   - If either stops, Streamlit Cloud app will show "API Offline"

3. SECURITY:
   - Your local API is exposed to internet via ngrok
   - ngrok free tier shows warning page (users must click "Visit Site")
   - For production, use ngrok paid plan or deploy API to cloud

4. UPDATING API_URL:
   - Go to: https://share.streamlit.io/
   - Click on your app
   - Settings → Secrets
   - Update API_URL with new ngrok URL
   - Click "Save"
   - App will automatically restart

═══════════════════════════════════════════════════════════════

🚀 QUICK START COMMANDS
═══════════════════════════════════════════════════════════════

# Terminal 1: Start local services
cd /home/rhemi/IA3/Dar_mlops/Migraine_CICD
sudo docker-compose up -d

# Terminal 2: Start ngrok
ngrok http 8000

# Copy the ngrok HTTPS URL, then deploy to Streamlit Cloud!

═══════════════════════════════════════════════════════════════

🔧 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════

Issue: "API Offline" in Streamlit Cloud
Solution: 
  - Check if docker-compose is running: sudo docker-compose ps
  - Check if ngrok is running: ps aux | grep ngrok
  - Verify API_URL in Streamlit secrets matches ngrok URL

Issue: "502 Bad Gateway" from ngrok
Solution:
  - Restart docker-compose: sudo docker-compose restart
  - Check API health: curl http://localhost:8000/health

Issue: ngrok URL changed
Solution:
  - Get new URL from ngrok terminal
  - Update in Streamlit Cloud → App Settings → Secrets
  - Save (app will restart automatically)

═══════════════════════════════════════════════════════════════

💡 ALTERNATIVE: DEPLOY API TO CLOUD
═══════════════════════════════════════════════════════════════

For production, consider deploying the API to:

1. Render (https://render.com)
   - Free tier available
   - Deploy from GitHub
   - Persistent URL (no ngrok needed)

2. Railway (https://railway.app)
   - $5/month credit free
   - Easy Docker deployment

3. AWS EC2 / Azure / GCP
   - Full control
   - More complex setup

Then update API_URL in Streamlit secrets to permanent URL.

═══════════════════════════════════════════════════════════════

✅ READY TO DEPLOY!
═══════════════════════════════════════════════════════════════

Follow the steps above and your Streamlit UI will be publicly
accessible while keeping the ML backend running locally!

Questions? Check the troubleshooting section above.

═══════════════════════════════════════════════════════════════
