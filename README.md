# Raster to Layered Vector (Inkscape extension)

Convert PNG/JPG images (e.g. scientific illustrations) into **editable, layered SVG** inside Inkscape. The image is reduced to *N* colors and each color is traced into its own named layer, so shapes can be recolored, moved or deleted independently.

Tracing is done by [vtracer](https://github.com/visioncortex/vtracer), run through a system Python install (Inkscape's bundled Python cannot easily install packages).

## Requirements

| Component | Version |
|---|---|
| Inkscape | 1.x (tested on Windows 64-bit) |
| Python | **3.12 recommended** (see note below) |
| Python packages | `vtracer`, `pillow`, `numpy` |

> **Do not use Python 3.14.** In testing, `vtracer` crashed silently (exit code `-1073741819`) under Python 3.14, which showed up in Inkscape as an empty "Worker failed" box. Python 3.12 works.

## Installation (Windows)

### 1. Install Python 3.12
Download the 64-bit Windows installer from <https://www.python.org/downloads/release/python-3129/> or run:

```
winget install Python.Python.3.12
```

Open a **new** PowerShell window and check:

```
py -0p
```

Note the full path on the `3.12` line, e.g.
`C:\Users\<you>\AppData\Local\Programs\Python\Python312\python.exe`

### 2. Install the packages
```
py -3.12 -m pip install -r requirements.txt
```
(or `py -3.12 -m pip install vtracer pillow numpy`)

### 3. Copy the extension files
Download this repository (**Code → Download ZIP**, or `git clone`) and copy these three files into Inkscape's user extensions folder:

- `raster_to_layers.inx`
- `raster_to_layers.py`
- `trace_worker.py`

To find the folder: Inkscape → **Edit → Preferences → System → User extensions → Open**.
On Windows it is normally `%APPDATA%\inkscape\extensions\`.

### 4. Restart Inkscape
The extension appears at **Extensions → Tracing → Raster to Layered Vector**.

### 5. Test the setup (optional but useful)
In PowerShell:
```
cd $env:APPDATA\inkscape\extensions
py -3.12 -c "from PIL import Image, ImageDraw; im=Image.new('RGB',(200,200),'white'); ImageDraw.Draw(im).ellipse((40,40,160,160),fill='green'); im.save('test.png')"
py -3.12 .\trace_worker.py test.png out.svg 4 2 4 60
$LASTEXITCODE
```
`0` means the tracer works.

## Usage

1. Import or paste a PNG/JPG into Inkscape (File → Import, or Ctrl+V).
2. **Click the image to select it.**
3. Open **Extensions → Tracing → Raster to Layered Vector**.
4. In **Python executable**, paste the full path to the Python 3.12 `python.exe` from step 1.
5. Set the options (below). Leave **Image file** empty to trace the selected image.
6. Click **Apply**. Wait 10-30 seconds; there is no progress bar.
7. A **"Traced vector"** layer appears on top, with one sub-layer per color named `NN #hexcolor`. Hide or delete the original image to view the result.

If no image is selected, the extension traces the file chosen in the **Image file** box instead.

### Options

| Option | Default | Effect |
|---|---|---|
| Number of colors | 8 | Palette size. Use about 8-16 for most figures; more for gradients, fewer for flat diagrams. |
| Upscale before tracing | 2 | Enlarges the image before tracing for smoother curves. Higher is slower. |
| Speckle filter (px) | 4 | Removes specks smaller than this. Raise it to clean up noise. |
| Corner threshold | 60 | Lower gives smoother curves, higher keeps sharper corners. |

## Limitations

- Text, arrows and labels become shapes, not live text. Retype them with Inkscape's Text tool.
- Gradients and photographic regions become banded color areas.
- Anti-aliased edges can produce thin stray layers. Increase the speckle filter or lower the color count.
- Vectorizing cannot add detail the raster does not contain. Use the largest source image available.
- Check the license of any image before reusing or modifying it.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `No module named 'vtracer'` | Inkscape ran the wrong Python. Put the full path to the Python where you installed the packages in **Python executable**. |
| "Worker failed:" with an empty message | Python crashed without output. Run the step 5 test. If `$LASTEXITCODE` is not `0`, switch to Python 3.12. |
| "Select an image on the canvas, or choose a file" | No image selected. Click the image first. |
| "Select a valid image file." | An older version of the extension is installed. Overwrite all three files and restart Inkscape. |
| Extension missing from the menu | Files are in the wrong folder, or Inkscape was not restarted. |
| Python path not recognized in PowerShell | Run `py -0p` and copy the exact path it lists. |

## macOS / Linux

Not tested. The same approach should work: install Python 3.12 and the packages, copy the three files to the Inkscape user extensions folder (see Edit → Preferences → System), and enter the full path to that Python (for example `/usr/bin/python3`) in **Python executable**.

## Files

| File | Purpose |
|---|---|
| `raster_to_layers.inx` | Inkscape dialog definition |
| `raster_to_layers.py` | Extension: reads the selected image, calls the worker, inserts the layers |
| `trace_worker.py` | Quantizes the image and traces each color with vtracer |
| `requirements.txt` | Python dependencies |

## License

Add a license file (for example MIT) before publishing.
