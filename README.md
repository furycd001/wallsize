# Batch Image Resizer

![alt text](wallsize.png "wallsize")

This bash script allows you to batch resize all images in a directory to a user-specified resolution. It supports `JPEG`, `PNG`, and `WebP` formats and saves all resized images to a separate folder.

## Installation

1. Ensure you have [ImageMagick](https://imagemagick.org/) installed, as the script uses the `magick` command for resizing.

2. **Clone the Repository**:
    ```bash
    git clone https://github.com/furycd001/wallsize.git
    cd hue
    ```

3. **Make the Script Executable**:
    ```bash
    chmod +x hue
    ```

4. **Move the Script to a Directory in Your PATH**:
    ```bash
    mv hue.sh ~/.local/bin/hue
    ```

    **Please ensure `~/.local/bin` is in your `PATH`. If not, add the following line to your `~/.bashrc` or `~/.zshrc` and reload the shell:**
    ```bash
    export PATH=$PATH:~/.local/bin
    ```

## Usage

Open a terminal in the directory containing your images & simply run `wallsize`.
