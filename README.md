# Drew Meme Generator Web App

A Flask web application that automatically finds trending memes from Reddit with faces and swaps them with Drew's face using AI-powered face detection and swapping.

## Features

- Automatically fetches trending memes from Reddit
- Detects faces in memes using InsightFace
- Swaps faces with Drew's face seamlessly
- Simple one-button interface
- Caches results for better performance

## Prerequisites

- Python 3.8 or higher
- Reddit API credentials ([Get them here](https://www.reddit.com/prefs/apps))
- xAI API key for Grok ([Get it here](https://x.ai))
- Drew's face image (drew_face.jpg)

## Local Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd meme_app
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download InsightFace model:**
   ```bash
   python -c "from insightface.model_zoo import get_model; get_model('inswapper_128.onnx', download=True)"
   ```

5. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

6. **Place Drew's face image:**
   - Put `drew_face.jpg` in the root directory
   - Ensure it's a clear, front-facing photo with one face

7. **Run the app:**
   ```bash
   python app.py
   ```

8. **Open your browser:**
   - Navigate to `http://localhost:5000`

## Deployment Options

### Option 1: Render.com (Recommended for Beginners)

**Pros:**
- Free tier available
- Automatic deployments from GitHub
- Easy to set up
- Built-in SSL/HTTPS
- Good for small-medium traffic

**Cons:**
- Free tier spins down after 15 mins of inactivity (slow cold starts)
- Limited resources on free tier
- InsightFace models may be too large for free tier

**Steps:**
1. Push code to GitHub
2. Sign up at [render.com](https://render.com)
3. Create new "Web Service"
4. Connect your GitHub repo
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `gunicorn app:app`
7. Add environment variables in dashboard
8. Deploy

**Estimated Cost:** Free - $7/month for starter tier

---

### Option 2: Railway.app

**Pros:**
- Very easy deployment
- Generous free tier ($5 credit/month)
- Good performance
- Automatic HTTPS
- Better for ML models than Render

**Cons:**
- Free tier limited to $5/month usage
- May need to upgrade for consistent uptime
- Fewer configuration options

**Steps:**
1. Push code to GitHub
2. Sign up at [railway.app](https://railway.app)
3. Create new project from GitHub repo
4. Railway auto-detects Flask app
5. Add environment variables
6. Deploy automatically

**Estimated Cost:** $5-15/month after free tier

---

### Option 3: DigitalOcean App Platform

**Pros:**
- Reliable and scalable
- Good documentation
- Can handle ML workloads well
- Professional-grade infrastructure

**Cons:**
- No free tier (starts at $5/month)
- Slightly more complex setup
- May need larger instance for InsightFace

**Steps:**
1. Push code to GitHub
2. Sign up at [digitalocean.com](https://digitalocean.com)
3. Create new App
4. Connect GitHub repo
5. DigitalOcean detects Python app
6. Add environment variables
7. Choose instance size (recommend Basic $12/month)
8. Deploy

**Estimated Cost:** $12-25/month

---

### Option 4: AWS Elastic Beanstalk

**Pros:**
- Very scalable
- Part of AWS ecosystem
- Auto-scaling capabilities
- Professional infrastructure

**Cons:**
- Most complex setup
- Can get expensive quickly
- Steeper learning curve
- Overkill for small projects

**Steps:**
1. Install AWS CLI and EB CLI
2. Run `eb init` and `eb create`
3. Configure environment variables in AWS console
4. Deploy with `eb deploy`

**Estimated Cost:** $15-50/month minimum

---

### Option 5: Fly.io

**Pros:**
- Free tier available (3 shared VMs)
- Fast global deployment
- Good for ML workloads
- Modern platform

**Cons:**
- Command-line focused
- Free tier may not have enough resources
- Less intuitive than Render/Railway

**Steps:**
1. Install flyctl CLI
2. Run `fly launch` in project directory
3. Add environment variables with `fly secrets set`
4. Deploy with `fly deploy`

**Estimated Cost:** Free - $10/month

---

### Option 6: Heroku

**Pros:**
- Very popular and well-documented
- Easy to use
- Good ecosystem

**Cons:**
- No free tier anymore (min $5/month)
- Can be expensive at scale
- Less generous than alternatives

**Steps:**
1. Install Heroku CLI
2. Run `heroku create`
3. Set config vars: `heroku config:set KEY=value`
4. Deploy: `git push heroku main`

**Estimated Cost:** $5-25/month

---

## Recommendation Summary

| Service | Best For | Cost | Ease of Setup |
|---------|----------|------|---------------|
| **Railway** | Best overall balance | $5-15/mo | ⭐⭐⭐⭐⭐ |
| **Render** | Beginners (if it runs) | Free-$7/mo | ⭐⭐⭐⭐⭐ |
| **Fly.io** | Tech-savvy developers | Free-$10/mo | ⭐⭐⭐⭐ |
| **DigitalOcean** | Production apps | $12-25/mo | ⭐⭐⭐⭐ |
| **Heroku** | Quick prototypes | $5-25/mo | ⭐⭐⭐⭐ |
| **AWS EB** | Enterprise/scalability | $15-50/mo | ⭐⭐ |

**My Recommendation:** Start with **Railway** - it has the best balance of ease, cost, and capability for this ML-based app.

## Important Notes

### Model Size Considerations
- InsightFace models are ~150MB
- Some free tiers may struggle with this
- Consider upgrading to paid tier if app is slow

### Cold Starts
- Many platforms spin down apps after inactivity
- First request after idle period will be slow (30-60 seconds)
- Consider paid tier with "always-on" for better UX

### API Rate Limits
- Reddit API has rate limits
- xAI Grok API has usage limits
- Monitor usage to avoid unexpected costs

## Environment Variables Required

```
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_app_name
XAI_API_KEY=your_xai_api_key
DREW_FACE_PATH=drew_face.jpg
```

## Troubleshooting

### "No face detected in drew_face.jpg"
- Ensure the image is clear and front-facing
- Try a different photo with better lighting

### "No suitable meme with face found"
- Reddit may not have suitable memes at the moment
- Try again in a few minutes
- Check Reddit API credentials

### Slow performance
- First run downloads face detection models (~150MB)
- Cold starts on free tiers can be slow
- Consider upgrading to paid tier

### Memory errors
- InsightFace models are memory-intensive
- Upgrade to larger instance size
- Minimum 1GB RAM recommended

## License

MIT License - feel free to modify and use as you wish!
