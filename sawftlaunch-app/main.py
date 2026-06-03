"""SawftLaunch — dynamic, generative design API (v1).

Run locally:
    .venv/bin/uvicorn main:app --reload
Then open http://127.0.0.1:8000
"""

import base64
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool

import brain
import design
import storage

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env", override=True)  # .env wins, even over an empty shell var

app = FastAPI(title="SawftLaunch")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

MAX_PHOTOS = 4
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


# ---------------------------------------------------------------------------
# Identity assembly + storage
# ---------------------------------------------------------------------------
def build_identity(layout, name, tagline, palette=None, font_pairing="modern-grotesk",
                   shape="rounded", eyebrow="", bio="", specialties=None, booking="",
                   photos=None, dna=None):
    """Assemble a render-ready barber portfolio from the composed design spec."""
    if layout not in design.LAYOUTS:
        layout = "editorial"
    return {
        "layout": layout,
        "name": name,
        "tagline": tagline,
        "eyebrow": eyebrow,
        "bio": bio,
        "specialties": specialties or [],
        "booking": booking,
        "photos": photos or [],
        "dna": dna or {},
        "fonts": design.get_fonts(font_pairing),   # {display, body, url}
        "radius": design.get_radius(shape),
        "palette": palette or design.DEFAULT_PALETTE,
    }


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
    name: str = Form(""),
    booking: str = Form(""),
    photos: list[UploadFile] = [],  # noqa: B006 — these are INSPIRATION images
):
    # Collect inspiration images as base64 (skip empties / non-images).
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
        "what they do": what,
    }

    # The brain call is blocking network IO — run it off the event loop.
    try:
        result = await run_in_threadpool(brain.generate_identity, images, answers)
    except Exception as e:  # surface a friendly message instead of a 500 page
        return templates.TemplateResponse(
            request, "error.html", {"message": str(e)}, status_code=502
        )

    render_identity = build_identity(
        result["layout"],
        name=result["brand_name"],
        tagline=result["tagline"],
        palette=result["palette"],
        font_pairing=result["font_pairing"],
        shape=result["shape"],
        eyebrow=result["eyebrow"],
        bio=result.get("bio", ""),
        specialties=result.get("specialties", []),
        booking=booking.strip(),
        dna=result.get("dna"),
    )
    slug = storage.save_identity(render_identity)
    return RedirectResponse(url=f"/u/{slug}", status_code=303)


@app.get("/u/{slug}", response_class=HTMLResponse)
def show_identity(request: Request, slug: str):
    identity = storage.load_identity(slug)
    if identity is None:
        raise HTTPException(status_code=404, detail="That identity doesn't exist.")
    return templates.TemplateResponse(request, "page.html", {"identity": identity})


# Preview routes — sample barber in each layout (no AI; handy for QA).
_PREVIEW_SAMPLES = {
    "editorial": {
        "font": "editorial-serif", "shape": "sharp",
        "palette": {"bg": "#f6f1e7", "ink": "#1d1b18", "accent": "#b5482e", "accent2": "#7d8466", "soft": "#cdbfa6"},
        "name": "Atelier Fade", "eyebrow": "Master Barber · NYC",
        "tagline": "Precision cuts with a quiet, considered hand.",
        "bio": "Atelier Fade is the chair where patience meets a straight razor. Every line is measured, every fade earned — work that holds up in daylight and in photos.",
        "specialties": ["Skin fades", "Scissor work", "Beard sculpting", "Hot towel shave"],
    },
    "bold": {
        "font": "heavy-impact", "shape": "rounded",
        "palette": {"bg": "#fff7e8", "ink": "#161310", "accent": "#ff4d2e", "accent2": "#1fb6a6", "soft": "#ffc233"},
        "name": "FRESH CUTS CO", "eyebrow": "Barbershop · Open 7 days",
        "tagline": "Sharp cuts, good energy, zero waiting around.",
        "bio": "Walk in, walk out a new person. We move fast, cut clean, and keep the music loud. The crew's chair of choice.",
        "specialties": ["Tapers", "Designs", "Kids cuts", "Line-ups", "Color"],
    },
    "moody": {
        "font": "quiet-luxe", "shape": "soft",
        "palette": {"bg": "#13110e", "ink": "#f3efe6", "accent": "#c7a45a", "accent2": "#6b6256", "soft": "#262219"},
        "name": "Midnight Barber", "eyebrow": "By appointment · Private studio",
        "tagline": "Late chairs, low light, immaculate cuts.",
        "bio": "A private studio for those who'd rather not wait in a crowd. One chair, full attention, and a cut finished to the millimeter.",
        "specialties": ["Executive cuts", "Beard design", "Grey blending", "Straight razor"],
    },
}


@app.get("/preview/{layout}", response_class=HTMLResponse)
def preview(request: Request, layout: str):
    s = _PREVIEW_SAMPLES.get(layout)
    if s is None:
        raise HTTPException(status_code=404, detail=f"Unknown layout: {layout}")
    identity = build_identity(
        layout, name=s["name"], tagline=s["tagline"], palette=s["palette"],
        font_pairing=s["font"], shape=s["shape"], eyebrow=s["eyebrow"],
        bio=s["bio"], specialties=s["specialties"],
    )
    return templates.TemplateResponse(request, "page.html", {"identity": identity})
