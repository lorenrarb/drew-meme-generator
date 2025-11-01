import os
import json
import time
import pickle
import requests
from io import BytesIO
from flask import Flask, render_template, jsonify, send_file
import praw
from xai_sdk import Client
import cv2
import numpy as np
from PIL import Image
from insightface.app import FaceAnalysis
import insightface
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration from environment variables
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'drewmemeapp')
XAI_API_KEY = os.getenv('XAI_API_KEY')

# Validate required environment variables
if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET or not XAI_API_KEY:
    raise ValueError("Missing required environment variables: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, XAI_API_KEY")

# Paths
DREW_FACE_PATH = os.getenv('DREW_FACE_PATH', 'drew_face.jpg')
OUTPUT_DIR = 'static/output'
CACHE_FILE = 'reddit_meme_cache.pkl'
CACHE_SECONDS = 7200

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize clients
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

xai_client = Client(api_key=XAI_API_KEY)

# Initialize face analysis (lazy load)
face_app = None
swapper = None

def get_face_app():
    global face_app
    if face_app is None:
        face_app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        face_app.prepare(ctx_id=0, det_size=(640, 640))
    return face_app

def get_swapper():
    global swapper
    if swapper is None:
        model_path = os.path.expanduser("~/.insightface/models/inswapper_128.onnx")
        swapper = insightface.model_zoo.get_model(model_path, download=False, download_zip=False)
    return swapper

# Cache functions
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'rb') as f:
            d = pickle.load(f)
            if time.time() - d['ts'] < CACHE_SECONDS:
                return d['memes']
    return []

def save_cache(memes):
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump({'memes': memes, 'ts': time.time()}, f)

# Fetch memes from Reddit
def fetch_reddit_memes(limit=12):
    memes = []
    sub = reddit.subreddit('memes+dankmemes')
    for p in sub.hot(limit=limit*2):
        u = p.url.lower()
        if u.endswith(('.jpg','.png')) and not p.over_18 and p.score > 200:
            memes.append({
                'source': 'Reddit',
                'title': p.title,
                'url': p.url,
                'score': p.score,
                'comments': p.num_comments,
                'created_utc': p.created_utc
            })
    return sorted(memes, key=lambda x: x['score'] + x['comments']*1.5, reverse=True)[:limit]

# Pick best meme using AI
def pick_best_meme(memes):
    if not memes:
        return None

    prompt = """You are a meme-expert. Pick ONE meme that is:
    • trending right now (high engagement)
    • has 1-2 clear, front-facing faces (ideal for face-swap)
    • SFW, not text-only, not a crowd

    Return ONLY JSON: {"index":0,"reason":"short reason"}

    Memes:
    """
    for i, m in enumerate(memes[:6]):
        eng = m['score'] + m['comments']*1.5
        prompt += f"{i}: \"{m['title']}\" (engagement≈{eng:.0f})\n"

    try:
        resp = xai_client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.2
        )
        sel_text = resp.choices[0].message.content.strip()
        sel = json.loads(sel_text)
        idx = sel['index']
        if 0 <= idx < len(memes):
            memes[idx]['selection_reason'] = sel['reason']
            return memes[idx]
    except Exception as e:
        print("LLM error → fallback:", e)

    # Fallback: highest engagement
    best = max(memes, key=lambda x: x['score'] + x['comments']*1.5)
    best['selection_reason'] = "Fallback: highest engagement"
    return best

# Find meme with face
def find_meme_with_face():
    app_inst = get_face_app()

    for post in reddit.subreddit('memes+dankmemes').hot(limit=50):
        if not post.url.lower().endswith(('.jpg', '.png')):
            continue
        if post.over_18 or post.score < 500:
            continue

        try:
            resp = requests.get(post.url, timeout=10)
            img = np.array(Image.open(BytesIO(resp.content)))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            faces = app_inst.get(img)

            if len(faces) >= 1:
                face = faces[0]
                w = face.bbox[2] - face.bbox[0]
                h = face.bbox[3] - face.bbox[1]
                area = w * h
                if area > 10000:  # Large enough face
                    return img, post
        except Exception as e:
            continue

    return None, None

# Perform face swap
def swap_face(meme_img):
    app_inst = get_face_app()
    swap_model = get_swapper()

    # Load Drew's face
    drew_img = cv2.imread(DREW_FACE_PATH)
    if drew_img is None:
        raise FileNotFoundError(f"{DREW_FACE_PATH} not found!")

    drew_faces = app_inst.get(drew_img)
    if len(drew_faces) == 0:
        raise ValueError("No face detected in Drew's photo")
    drew_face = drew_faces[0]

    # Detect faces in meme
    meme_faces = app_inst.get(meme_img)
    if len(meme_faces) == 0:
        raise ValueError("No face in meme")

    # Pick largest face
    target_face = max(meme_faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))

    # Swap
    result = swap_model.get(meme_img, target_face, drew_face, paste_back=True)
    return result

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_meme():
    try:
        # Step 1: Find a meme with a face
        meme_img, post = find_meme_with_face()
        if meme_img is None:
            return jsonify({'error': 'No suitable meme with face found'}), 404

        # Step 2: Swap the face
        result = swap_face(meme_img)

        # Step 3: Save the result
        output_filename = f'drew_meme_{int(time.time())}.png'
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        cv2.imwrite(output_path, result)

        return jsonify({
            'success': True,
            'image_url': f'/static/output/{output_filename}',
            'meme_title': post.title,
            'meme_score': post.score
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
