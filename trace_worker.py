import sys, re, os, tempfile
import numpy as np
from PIL import Image, ImageFilter
import vtracer

src, out, n, up, speckle, corner = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:7])

im = Image.open(src).convert("RGB")
w, h = im.size
if up > 1:
    im = im.resize((w * up, h * up), Image.LANCZOS)
q = im.quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
arr = np.array(q)
pal = q.getpalette()
idx, counts = np.unique(arr, return_counts=True)
order = idx[np.argsort(-counts)]  # largest area first (bottom layer)

tmp = tempfile.gettempdir()
layers = []
for k, i in enumerate(order):
    col = "#%02x%02x%02x" % tuple(pal[i*3:i*3+3])
    if k == 0:  # background: full rectangle
        body = f'<rect width="{w*up}" height="{h*up}" fill="{col}"/>'
    else:
        mask = Image.fromarray(np.where(arr == i, 0, 255).astype("uint8"))
        mask = mask.filter(ImageFilter.MinFilter(3))  # grow 1px to avoid seams
        mp, sp = os.path.join(tmp, "m.png"), os.path.join(tmp, "m.svg")
        mask.save(mp)
        vtracer.convert_image_to_svg_py(mp, sp, colormode="binary", mode="spline",
                                        filter_speckle=speckle, corner_threshold=corner,
                                        path_precision=3)
        paths = re.findall(r"<path[^>]*/>", open(sp, encoding="utf-8").read())
        body = "".join(p.replace('fill="#000000"', f'fill="{col}"') for p in paths)
    layers.append(f'<g inkscape:groupmode="layer" inkscape:label="{k:02d} {col}">'
                  f'<g transform="scale({1/up})">{body}</g></g>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
       f'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
       f'width="{w}px" height="{h}px" viewBox="0 0 {w} {h}">{"".join(layers)}</svg>')
open(out, "w", encoding="utf-8").write(svg)
