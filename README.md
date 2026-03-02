
# Wallsize

**Wallsize** is a streamlined, interactive tool designed to take the guesswork out of cropping images for wallpapers. Instead of relying on static gravity flags (like "center" or "north"), it provides a live GUI canvas where you can position images before saving.

It consists of a bash wrapper `wallsize` for dependency management and a python backend `wallsize_gui.py` powered by **[tkinter](https://docs.python.org/3/library/tkinter.html)** and **[ImageMagick](https://imagemagick.org/)**.


## Features
+ **Live Preview:** See exactly how your image will fit the target resolution.
+ **Dual Motion Modes:**
	+ **Default Mode:** Quickly snap images to the North, South, East, or West edges.
	+ **Manual Mode:** Nudge images 1 pixel at a time for high-precision alignment.
+ **Batch Processing:** Automatically cycles through all images in the current directory.
+ **Visual Guides:** Includes a center-point crosshair and "toast" notifications for actions.
+ **High Quality:** Uses ImageMagick's `LANCZOS` filtering for final exports.


## Requirements
Before running the scripts, ensure you have the following installed:
1. **ImageMagick 7+**: Used for the final image processing (`magick` command).
2. **Python 3**: The core logic engine.
3. **Pillow (PIL)**: For GUI image rendering.
4. **Tkinter**: Python’s standard GUI framework.


## Installation
+ Save both files to the `~/.local/bin/` as:
	+ `~/.local/bin/wallsize`
	+ `~/.local/bin/wallsize_gui.py`
+ Make them both executable:
	+ `chmod +x ~/.local/bin/wallsize`
	+ `chmod +x ~/.local/bin/wallsize_gui.py`

> Make sure that `~/.local/bin/` is in your path !!


## Usage
Navigate to the folder containing images & run:

```bash
# Provide a resolution as an argument at run..
wallsize 1920x1200

# Run it without an argument & it will automatically prompt you for one..
wallsize
```

The script will create a subfolder named `resized/` where all saves images are placed `{filename}_resized.jpg`.


## Controls

| Key | Action |
| --- | --- |
| **Arrow Keys** | Move image (Snap-to-edge in Default / 1px nudge in Manual) |
| **`m`** | Toggle Mode between Default and Manual |
| **`c`** | Center image on both axes |
| **`[`** | Center image horizontally |
| **`]`** | Center image vertically |
| **`s`** | Save and advance to next image |
| **`p`** | Skip current image (no save) |
| **`q`** | Quit application |


## How it Works

1. **Scaling:** The script automatically scales your image to the "Minimum Fill"—it ensures the image is at least as large as your target resolution while maintaining the aspect ratio.
2. **Positioning:** You move the "view" of the image within the canvas.
3. **Final Export:** When you press **`s`**, the script passes your exact coordinates to ImageMagick to perform a lossless crop and resize, ensuring the output is exactly the resolution you requested.

---

> **Note:** If you find the GUI window is too large for your monitor (e.g., trying to crop a 4K wallpaper on a 1080p screen), you may need to adjust your OS display scaling or the resolution input. 
>
> This tool is more handcrafted than anything so expect a few charming bugs and character-building quirks along the way.
