"""
image_pipeline.py
Converts a portrait photo into a 1-bit Floyd-Steinberg dithered dot field,
with background segmentation for dark-mode masking.

Source of truth for the portrait layer of the banner SVG.
"""
import numpy as np
from PIL import Image, ImageOps, ImageFilter
from scipy import ndimage

GRID_W, GRID_H = 300, 340


def load_and_crop(path, target_w=GRID_W, target_h=GRID_H):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    target_ratio = target_w / target_h
    ratio = w / h
    if ratio > target_ratio:
        # too wide -> crop sides
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        im = im.crop((left, 0, left + new_w, h))
    else:
        # too tall -> crop a bit off the bottom (keep head+shoulders, not feet)
        new_h = int(w / target_ratio)
        top = 0
        im = im.crop((0, top, w, top + new_h))
    return im


def segment_foreground(im_rgb):
    """Separate subject from a roughly-uniform background using color distance
    from the corner-sampled background color, then clean the mask."""
    arr = np.asarray(im_rgb).astype(np.float32)
    h, w, _ = arr.shape
    corner_px = np.concatenate([
        arr[0:15, 0:15].reshape(-1, 3),
        arr[0:15, w - 15:w].reshape(-1, 3),
        arr[h - 15:h, 0:15].reshape(-1, 3),
    ], axis=0)
    bg_color = np.median(corner_px, axis=0)

    dist = np.linalg.norm(arr - bg_color, axis=2)
    thresh = np.percentile(dist, 35)  # adaptive
    thresh = max(thresh, 22)
    mask = dist > thresh

    # binary closing to seal small gaps, then keep largest connected component
    mask = ndimage.binary_closing(mask, structure=np.ones((5, 5)), iterations=2)
    mask = ndimage.binary_fill_holes(mask)
    labeled, n = ndimage.label(mask)
    if n > 0:
        sizes = ndimage.sum(mask, labeled, range(1, n + 1))
        biggest = np.argmax(sizes) + 1
        mask = labeled == biggest
    # slight dilation so hair edges aren't eaten
    mask = ndimage.binary_dilation(mask, iterations=1)
    return mask


def process_portrait(path, mode="dark"):
    """Returns a (GRID_H, GRID_W) boolean array: True = draw a dot."""
    im = load_and_crop(path).resize((GRID_W, GRID_H), Image.LANCZOS)

    mask = segment_foreground(im) if mode == "dark" else None

    gray = ImageOps.grayscale(im)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    enhanced = gray.filter(ImageFilter.UnsharpMask(radius=3, percent=140, threshold=3))

    # manual 1.3x contrast around midpoint
    arr = np.asarray(enhanced).astype(np.float32)
    arr = (arr - 128) * 1.3 + 128
    arr = np.clip(arr, 0, 255)

    if mode == "dark":
        # subject lit on dark panel -> dots = the (lit) subject; background cleared
        arr[~mask] = 255  # push background to white so dithering drops it (white=no dot)
    # light mode: keep full frame, dots = dark parts of the photo (unchanged)

    dots = floyd_steinberg_serpentine(arr)
    if mode == "dark":
        dots[~mask] = False
    return dots


def floyd_steinberg_serpentine(arr):
    """1-bit dithering with serpentine (boustrophedon) scan.
    Returns boolean array where True = dark pixel = draw dot."""
    a = arr.copy().astype(np.float32)
    h, w = a.shape
    out = np.zeros((h, w), dtype=bool)
    for y in range(h):
        left_to_right = (y % 2 == 0)
        xs = range(w) if left_to_right else range(w - 1, -1, -1)
        for x in xs:
            old = a[y, x]
            new = 0.0 if old < 128 else 255.0
            out[y, x] = new == 0.0
            err = old - new
            nxt = x + 1 if left_to_right else x - 1
            prv = x - 1 if left_to_right else x + 1
            if 0 <= nxt < w:
                a[y, nxt] += err * 7 / 16
            if y + 1 < h:
                if 0 <= prv < w:
                    a[y + 1, prv] += err * 3 / 16
                a[y + 1, x] += err * 5 / 16
                if 0 <= nxt < w:
                    a[y + 1, nxt] += err * 1 / 16
    return out


if __name__ == "__main__":
    import sys, json
    src = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/uploads/WhatsApp_Image_2026-07-30_at_11_35_41_AM.jpeg"
    for mode in ("dark", "light"):
        dots = process_portrait(src, mode)
        count = int(dots.sum())
        print(mode, "dot count:", count)
        np.save(f"/home/claude/github-profile/output/dots_{mode}.npy", dots)
