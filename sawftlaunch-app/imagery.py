"""SawftLaunch imagery engine.

Generates brand/atmosphere imagery that feels HUMAN, not AI:
  1. build a photographic prompt from the design DNA,
  2. generate with Flux (via fal.ai),
  3. apply our "house look" treatment (warm grade + film grain + vignette),
  4. (caller) curate / regenerate the best one.

The treatment pass is the moat-y bit — it's what makes output feel analog and
cohesive regardless of the base model. Set FAL_KEY in the env to actually
generate; the treatment works on any image with zero external calls.
"""

import io

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

FLUX_MODEL = "fal-ai/flux/dev"


# ---------------------------------------------------------------------------
# 1. photographic prompting (DNA -> a prompt that reads as a real photo)
# ---------------------------------------------------------------------------
def build_prompt(subject, dna=None, extra=""):
    dna = dna or {}
    mood = ", ".join((dna.get("mood") or [])[:3]) or "warm, crafted, premium"
    prompt = (
        f"{subject}. Shot on Kodak Portra 400, 35mm lens, natural soft window light, "
        f"shallow depth of field, candid and unposed, fine film grain, gentle halation, "
        f"{mood} tones, editorial photography, lived-in and slightly imperfect, "
        f"photorealistic. No text, no watermark, no logo, no illustration."
    )
    return (prompt + " " + extra).strip()


# ---------------------------------------------------------------------------
# 2. generation (Flux via fal.ai) — requires FAL_KEY in env
# ---------------------------------------------------------------------------
def generate_flux(prompt, size="portrait_4_3"):
    import fal_client
    result = fal_client.subscribe(
        FLUX_MODEL,
        arguments={
            "prompt": prompt,
            "image_size": size,
            "num_images": 1,
            "num_inference_steps": 28,
            "enable_safety_checker": True,
        },
    )
    return result["images"][0]["url"]


def _download(url):
    import httpx
    r = httpx.get(url, timeout=60)
    r.raise_for_status()
    return r.content


# ---------------------------------------------------------------------------
# 3. the house-look treatment (the human-feel secret sauce)
# ---------------------------------------------------------------------------
def apply_treatment(img):
    """Subtle warm film grade + grain + vignette. Makes output feel analog."""
    img = img.convert("RGB")
    w, h = img.size

    # grade: gentle contrast, slight desaturation, warm wash
    img = ImageEnhance.Contrast(img).enhance(1.07)
    img = ImageEnhance.Color(img).enhance(0.90)
    warm = Image.new("RGB", (w, h), (255, 236, 205))
    img = Image.blend(img, ImageChops.multiply(img, warm), 0.14)

    # film grain (mid-gray noise, overlaid so midtones stay put)
    noise = Image.effect_noise((w, h), 26).convert("L")
    grain = Image.merge("RGB", (noise, noise, noise))
    img = Image.blend(img, ImageChops.overlay(img, grain), 0.16)

    # vignette: soft darkened edges
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse((-w * 0.25, -h * 0.25, w * 1.25, h * 1.25), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(max(w, h) * 0.18))
    darker = ImageChops.multiply(img, Image.merge("RGB", (mask, mask, mask)))
    img = Image.blend(img, darker, 0.32)
    return img


# ---------------------------------------------------------------------------
# 4. one-shot: prompt -> generate -> treat -> jpeg bytes
# ---------------------------------------------------------------------------
def make_image(subject, dna=None, size="portrait_4_3"):
    url = generate_flux(build_prompt(subject, dna), size)
    raw = Image.open(io.BytesIO(_download(url)))
    treated = apply_treatment(raw)
    out = io.BytesIO()
    treated.save(out, format="JPEG", quality=90)
    return out.getvalue()
