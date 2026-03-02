#!/usr/bin/env python3
"""
wallsize_gui.py — Interactive image crop-positioning tool

Keys:
  Arrow keys  — move image
                Default mode : snap to canvas edge (N / S / E / W)
                Manual mode  : nudge 1 pixel at a time
  m           — toggle Default / Manual mode
  c           — centre on both axes
  [           — centre horizontally only
  ]           — centre vertically only
  s           — save and advance to next image
  p           — skip image (no save)
  q           — quit
"""

import math
import os
import sys
import glob
import subprocess
import tkinter as tk
from tkinter import messagebox

try:
    from PIL import Image, ImageTk
except ImportError:
    print("ERROR: Pillow is required.  Run:  pip install Pillow")
    sys.exit(1)

# ── Palette ───────────────────────────────────────────────────────────────────
WARN      = "#ff5f5f"
ACCENT    = "#00e5a0"
SAVED_COL = "#00bfff"
SKIP_COL  = "#ffaa00"
INFO_COL  = "#ffffff"


class WallsizeApp:
    def __init__(self, root: tk.Tk, images: list, resolution: str, out_dir: str):
        self.root       = root
        self.images     = images
        self.out_dir    = out_dir
        self.resolution = resolution
        self.cv_w, self.cv_h = map(int, resolution.split("x"))

        try:
            root.tk.call("tk", "scaling", 1.0)
        except Exception:
            pass

        self.index      = 0
        self.mode       = "default"
        self.img_x      = 0
        self.img_y      = 0
        self.img_w      = 0
        self.img_h      = 0
        self.pil_img    = None
        self._toast_job = None

        self._build_ui()
        self._bind_keys()
        self._load_current()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.root.title("wallsize")
        self.root.configure(bg="black")
        self.root.resizable(False, False)
        self.root.geometry(f"{self.cv_w}x{self.cv_h}")

        self.canvas = tk.Canvas(
            self.root,
            width=self.cv_w,
            height=self.cv_h,
            bg="black",
            bd=0,
            highlightthickness=0,
            relief="flat",
        )
        self.canvas.pack(padx=0, pady=0)
        self.root.focus_set()

    def _bind_keys(self):
        self.root.bind("<KeyPress>", self._on_key)

    # ── Image loading ─────────────────────────────────────────────────────────

    def _load_current(self):
        if self.index >= len(self.images):
            messagebox.showinfo(
                "wallsize — done",
                f"All {len(self.images)} image(s) processed.\nOutput → {self.out_dir}/",
            )
            self.root.quit()
            return

        self.current_path = self.images[self.index]

        try:
            raw = Image.open(self.current_path).convert("RGB")
        except Exception as exc:
            messagebox.showerror("Load error",
                                 f"Cannot open:\n{self.current_path}\n\n{exc}")
            self.index += 1
            self._load_current()
            return

        scale        = max(self.cv_w / raw.width, self.cv_h / raw.height)
        self.img_w   = math.ceil(raw.width  * scale)
        self.img_h   = math.ceil(raw.height * scale)
        self.pil_img = raw.resize((self.img_w, self.img_h), Image.LANCZOS)

        fname = os.path.basename(self.current_path)
        print(f"\n[wallsize] {fname}")
        print(f"  raw={raw.width}x{raw.height}  "
              f"scaled={self.img_w}x{self.img_h}  "
              f"canvas={self.cv_w}x{self.cv_h}")

        self.mode = "default"
        self._centre_both()
        self._toast(
            f"[{self.index + 1}/{len(self.images)}]  {fname}",
            colour=INFO_COL,
            duration=1800,
        )

    # ── Centering ─────────────────────────────────────────────────────────────

    def _centre_h(self):
        self.img_x = (self.cv_w - self.img_w) // 2

    def _centre_v(self):
        self.img_y = (self.cv_h - self.img_h) // 2

    def _centre_both(self):
        self._centre_h()
        self._centre_v()
        self._render()

    # ── Render ────────────────────────────────────────────────────────────────

    def _render(self):
        ox = max(0, min(-self.img_x, self.img_w - self.cv_w))
        oy = max(0, min(-self.img_y, self.img_h - self.cv_h))

        tile = self.pil_img.crop((ox, oy, ox + self.cv_w, oy + self.cv_h))
        self.tk_img = ImageTk.PhotoImage(tile)

        self.canvas.delete("image", "crosshair")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img, tags="image")

        mx, my = self.cv_w // 2, self.cv_h // 2
        self.canvas.create_line(
            mx - 16, my, mx + 16, my,
            fill=WARN, width=1, tags="crosshair")
        self.canvas.create_line(
            mx, my - 16, mx, my + 16,
            fill=WARN, width=1, tags="crosshair")

    # ── Toast ─────────────────────────────────────────────────────────────────

    def _toast(self, message: str, colour: str = INFO_COL, duration: int = 1200):
        if self._toast_job is not None:
            self.root.after_cancel(self._toast_job)
            self._toast_job = None

        self.canvas.delete("toast")

        tx = self.cv_w // 2
        ty = self.cv_h - 40

        self.canvas.create_text(
            tx, ty,
            text=message,
            fill=colour,
            font=("Monospace", 11, "bold"),
            anchor="center",
            tags="toast",
        )
        bbox = self.canvas.bbox("toast")
        if bbox:
            self.canvas.create_rectangle(
                bbox[0] - 14, bbox[1] - 6,
                bbox[2] + 14, bbox[3] + 6,
                fill="#1a1a1a", outline="#333333", width=1,
                tags="toast",
            )
            self.canvas.create_text(
                tx, ty,
                text=message,
                fill=colour,
                font=("Monospace", 11, "bold"),
                anchor="center",
                tags="toast",
            )

        self._toast_job = self.root.after(duration, self._clear_toast)

    def _clear_toast(self):
        self.canvas.delete("toast")
        self._toast_job = None

    # ── Clamp ─────────────────────────────────────────────────────────────────

    def _clamp(self):
        self.img_x = min(0, max(self.cv_w - self.img_w, self.img_x))
        self.img_y = min(0, max(self.cv_h - self.img_h, self.img_y))

    # ── Key handler ───────────────────────────────────────────────────────────

    def _on_key(self, event: tk.Event):
        k = event.keysym.lower()

        if k == "q":
            remaining = len(self.images) - self.index
            if remaining > 0:
                if not messagebox.askyesno(
                        "Quit?",
                        f"Quit now? {remaining} image(s) will not be processed."):
                    return
            self.root.quit()
            return

        if k == "m":
            self.mode = "manual" if self.mode == "default" else "default"
            label = "DEFAULT  (↑↓←→ = snap)" \
                    if self.mode == "default" \
                    else "MANUAL  (↑↓←→ = 1px)"
            self._toast(label, colour=ACCENT if self.mode == "default" else WARN)
            self._render()
            return

        if k == "s":
            self._save()
            return

        if k == "p":
            self._skip()
            return

        if k == "c":
            self._centre_both()
            self._toast("centred", colour=ACCENT, duration=800)
            return

        if k == "bracketleft":
            self._centre_h(); self._clamp(); self._render()
            self._toast("centred horizontally", colour=ACCENT, duration=800)
            return

        if k == "bracketright":
            self._centre_v(); self._clamp(); self._render()
            self._toast("centred vertically", colour=ACCENT, duration=800)
            return

        if k not in ("up", "down", "left", "right"):
            return

        if self.mode == "default":
            if   k == "up":    self.img_y = 0
            elif k == "down":  self.img_y = self.cv_h - self.img_h
            elif k == "left":  self.img_x = 0
            elif k == "right": self.img_x = self.cv_w - self.img_w
        else:
            if   k == "up":    self.img_y += 1
            elif k == "down":  self.img_y -= 1
            elif k == "left":  self.img_x += 1
            elif k == "right": self.img_x -= 1

        self._clamp()
        self._render()

    # ── Skip ──────────────────────────────────────────────────────────────────

    def _skip(self):
        fname = os.path.basename(self.current_path)
        print(f"[wallsize] skipped: {fname}")
        self._toast(f"skipped  {fname}", colour=SKIP_COL, duration=700)
        self.root.after(750, self._advance)

    # ── Save ──────────────────────────────────────────────────────────────────

    def _save(self):
        ox = -self.img_x
        oy = -self.img_y

        stem     = os.path.splitext(os.path.basename(self.current_path))[0]
        out_file = os.path.join(self.out_dir, f"{stem}_resized.jpg")

        cmd = [
            "magick", self.current_path,
            "-resize",  f"{self.resolution}^",
            "-gravity", "NorthWest",
            "-crop",    f"{self.resolution}+{ox}+{oy}",
            "+repage",
            out_file,
        ]
        print(f"[wallsize] save: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            messagebox.showerror("Save failed", result.stderr or "Unknown error")
            return

        self._toast(
            f"saved → {os.path.basename(out_file)}",
            colour=SAVED_COL,
            duration=700,
        )
        self.root.after(750, self._advance)

    def _advance(self):
        self.index += 1
        self._load_current()


# ── Entry point ───────────────────────────────────────────────────────────────

def collect_images() -> list:
    exts = ("*.jpg", "*.jpeg", "*.png", "*.webp",
            "*.JPG", "*.JPEG", "*.PNG", "*.WEBP")
    found: set = set()
    for pat in exts:
        found.update(glob.glob(pat))
    return sorted(found)


def parse_resolution(res: str) -> bool:
    parts = res.lower().split("x")
    return (len(parts) == 2
            and all(p.isdigit() and int(p) > 0 for p in parts))


def main():
    if len(sys.argv) >= 2:
        resolution = sys.argv[1]
    else:
        resolution = input("Resolution (e.g. 1080x1920): ").strip()

    if not parse_resolution(resolution):
        print(f"ERROR: '{resolution}' is not a valid WxH resolution.")
        sys.exit(1)

    resolution = resolution.lower()

    images = collect_images()
    if not images:
        print("No images found in the current directory.")
        sys.exit(1)

    print(f"[wallsize] Found {len(images)} image(s).  Target: {resolution}")

    out_dir = "resized"
    os.makedirs(out_dir, exist_ok=True)

    root = tk.Tk()
    WallsizeApp(root, images, resolution, out_dir)
    root.mainloop()


if __name__ == "__main__":
    main()