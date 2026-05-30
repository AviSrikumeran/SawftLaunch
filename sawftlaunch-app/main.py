"""SawftLaunch — dynamic, generative design API (v1).

Run locally:
    .venv/bin/uvicorn main:app --reload
Then open http://127.0.0.1:8000
"""

import base64
import json
import re
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool

import aesthetics
import brain

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env", override=True)  # .env wins, even over an empty shell var

app = FastAPI(title="SawftLaunch")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

MAX_PHOTOS = 4
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


# ---------------------------------------------------------------------------
# Identity assembly + storage
# ---------------------------------------------------------------------------
def build_identity(aesthetic_id, name, tagline, palette=None, eyebrow="soft launch"):
    """Assemble a render-ready identity from an aesthetic + personalization."""
    a = aesthetics.get_aesthetic(aesthetic_id)
    if a is None:
        raise HTTPException(status_code=404, detail=f"Unknown aesthetic: {aesthetic_id}")
    return {
        "aesthetic_id": aesthetic_id,
        "name": name,
        "tagline": tagline,
        "eyebrow": eyebrow,
        "effect": a["effect"],
        "fonts": a["fonts"],
        "palette": palette or a["base_palette"],
    }


def _slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:40] or "launch"


def save_identity(render_identity):
    """Persist a render-ready identity to disk and return its unique slug."""
    slug = f"{_slugify(render_identity['name'])}-{secrets.token_hex(3)}"
    (DATA_DIR / f"{slug}.json").write_text(json.dumps(render_identity))
    return slug


def load_identity(slug):
    path = DATA_DIR / f"{slug}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "onboard.html", {})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
async def generate(
    request: Request,
    what: str = Form(...),
    feeling: str = Form(...),
    name: str = Form(""),
    aesthetic: str = Form(""),
    world: str = Form("either"),
    photos: list[UploadFile] = [],  # noqa: B006 (FastAPI handles default)
):
    # Collect uploaded photos as base64 (skip empties / non-images).
    images = []
    for upload in photos[:MAX_PHOTOS]:
        if not upload or not upload.filename:
            continue
        media_type = upload.content_type or "image/jpeg"
        if media_type not in ALLOWED_IMAGE_TYPES:
            continue
        data = await upload.read()
        if data:
            images.append((media_type, base64.standard_b64encode(data).decode("utf-8")))

    answers = {
        "name they gave": name,
        "who they are / what they're launching": what,
        "the feeling they want in 3 seconds": feeling,
        "an aesthetic they like": aesthetic,
        "light or dark world": world,
    }

    # The brain call is blocking network IO — run it off the event loop.
    try:
        result = await run_in_threadpool(brain.generate_identity, images, answers)
    except Exception as e:  # surface a friendly message instead of a 500 page
        return templates.TemplateResponse(
            request, "error.html", {"message": str(e)}, status_code=502
        )

    render_identity = build_identity(
        result["aesthetic_id"],
        name=result["brand_name"],
        tagline=result["tagline"],
        palette=result["palette"],
        eyebrow=result["eyebrow"],
    )
    slug = save_identity(render_identity)
    return RedirectResponse(url=f"/u/{slug}", status_code=303)


@app.get("/u/{slug}", response_class=HTMLResponse)
def show_identity(request: Request, slug: str):
    identity = load_identity(slug)
    if identity is None:
        raise HTTPException(status_code=404, detail="That identity doesn't exist.")
    return templates.TemplateResponse(request, "page.html", {"identity": identity})


# Preview routes for the curated crayon box (no AI — handy for browsing styles).
_PREVIEW_SAMPLES = {
    "cybersigilism": ("NOVA", "Underground sound, future rituals. New drop incoming."),
    "pasifika": ("Moana Made", "Hand-woven goods, ocean-rooted stories."),
    "vaporwave": ("After Hours", "Late-night synth dreams and neon afterglow."),
    "editorial-luxe": ("Atelier Sève", "Quiet luxury, considered objects, made to last."),
}


@app.get("/preview/{aesthetic_id}", response_class=HTMLResponse)
def preview(request: Request, aesthetic_id: str):
    sample = _PREVIEW_SAMPLES.get(aesthetic_id)
    if sample is None:
        raise HTTPException(status_code=404, detail=f"Unknown aesthetic: {aesthetic_id}")
    name, tagline = sample
    identity = build_identity(aesthetic_id, name=name, tagline=tagline)
    return templates.TemplateResponse(request, "page.html", {"identity": identity})
