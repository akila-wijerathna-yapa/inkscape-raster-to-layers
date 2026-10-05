import os, subprocess, tempfile, base64, re
from urllib.parse import unquote
import inkex
from inkex import Transform


class RasterToLayers(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--src", type=str, default="")
        pars.add_argument("--python", type=str, default="python")
        pars.add_argument("--colors", type=int, default=8)
        pars.add_argument("--upscale", type=int, default=2)
        pars.add_argument("--speckle", type=int, default=4)
        pars.add_argument("--corner", type=int, default=60)

    def _image_from_node(self, img):
        href = img.get("xlink:href") or img.get("href") or ""
        if href.startswith("data:"):
            m = re.match(r"data:image/(\w+);base64,(.*)", href, re.S)
            if not m:
                raise inkex.AbortExtension("Unsupported embedded image.")
            path = os.path.join(tempfile.gettempdir(), "rtl_input." + m.group(1))
            with open(path, "wb") as f:
                f.write(base64.b64decode(m.group(2)))
            return path
        p = unquote(href.replace("file:///", "").replace("file://", ""))
        if not os.path.isabs(p):
            p = os.path.join(os.path.dirname(self.document_path() or ""), p)
        return p

    def effect(self):
        o = self.options
        sel = self.svg.selection.filter(inkex.Image).first()
        if sel is not None:
            src = self._image_from_node(sel)
        else:
            src = o.src
        if not src or not os.path.isfile(src):
            raise inkex.AbortExtension(
                "Select an image on the canvas, or choose a file in the dialog.")

        worker = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trace_worker.py")
        out = os.path.join(tempfile.gettempdir(), "raster_to_layers_out.svg")
        cmd = [o.python, worker, src, out, str(o.colors), str(o.upscale),
               str(o.speckle), str(o.corner)]
        r = subprocess.run(cmd, capture_output=True, text=True,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if r.returncode != 0:
            raise inkex.AbortExtension("Worker failed:\n" + r.stderr[-1500:])

        doc = inkex.load_svg(out).getroot()
        pw = float(doc.get("width").replace("px", ""))
        ph = float(doc.get("height").replace("px", ""))

        wrapper = inkex.Group()
        wrapper.set("inkscape:groupmode", "layer")
        wrapper.set("inkscape:label", "Traced vector")
        if sel is not None:
            x = float(sel.get("x", 0)); y = float(sel.get("y", 0))
            w = float(sel.get("width", pw)); h = float(sel.get("height", ph))
            wrapper.transform = sel.transform @ Transform(
                f"translate({x},{y}) scale({w/pw},{h/ph})")
            sel.getparent().append(wrapper)
        else:
            s = self.svg.unittouu("1px")
            wrapper.transform = Transform(f"scale({s})")
            self.svg.append(wrapper)
        for g in list(doc):
            wrapper.append(g)


if __name__ == "__main__":
    RasterToLayers().run()
