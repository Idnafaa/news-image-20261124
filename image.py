# image.py — a tiny raster canvas and PNG writer in pure stdlib.
#
# render.py draws the whole poster with this one class: an RGB
# bytearray, filled shapes, straight lines, circles, polygons and
# bitmap text, then a scanline PNG encoded with zlib. Nothing here
# needs any package beyond the Python standard library.
import base64
import struct
import zlib

from font_data import FONTS


def _hex_to_rgb(spec):
    """Convert '#RRGGBB' into a triple of integers."""
    body = spec.lstrip("#")
    red = int(body[0:2], 16)
    green = int(body[2:4], 16)
    blue = int(body[4:6], 16)
    return (red, green, blue)


def _to_rgb(value):
    """Normalise a colour: a hex string becomes a triple, a triple stays."""
    if isinstance(value, str):
        return _hex_to_rgb(value)
    return value


class Canvas:
    """A fixed-size RGB drawing surface."""

    def __init__(self, width, height, bg="#F6F1E6"):
        self.w = width
        self.h = height
        self.px = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, bg)

    # -- single pixels ------------------------------------------------------

    def _put_pixel(self, x, y, color, alpha=255):
        """Paint one pixel, alpha-blending over what is already there."""
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        off = (y * self.w + x) * 3
        if alpha >= 255:
            self.px[off] = color[0]
            self.px[off + 1] = color[1]
            self.px[off + 2] = color[2]
            return
        rest = 255 - alpha
        self.px[off] = (color[0] * alpha + self.px[off] * rest) // 255
        self.px[off + 1] = (color[1] * alpha + self.px[off + 1] * rest) // 255
        self.px[off + 2] = (color[2] * alpha + self.px[off + 2] * rest) // 255

    # -- rectangles and lines -------------------------------------------------

    def fill_rect(self, x, y, w, h, color):
        c = _to_rgb(color)
        left = max(0, x)
        top = max(0, y)
        right = min(self.w, x + w)
        bottom = min(self.h, y + h)
        for yy in range(top, bottom):
            start = (yy * self.w + left) * 3
            for xx in range(left, right):
                j = start + (xx - left) * 3
                self.px[j] = c[0]
                self.px[j + 1] = c[1]
                self.px[j + 2] = c[2]

    def rect_outline(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.fill_rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.fill_rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        """Bresenham line, drawn as a trail of t-by-t squares."""
        c = _to_rgb(color)
        adx = abs(x1 - x0)
        ady = -abs(y1 - y0)
        step_x = 1 if x0 < x1 else -1
        step_y = 1 if y0 < y1 else -1
        err = adx + ady
        while True:
            self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            double = 2 * err
            if double >= ady:
                err += ady
                x0 += step_x
            if double <= adx:
                err += adx
                y0 += step_y

    # -- circles and polygons ---------------------------------------------------

    def fill_circle(self, cx, cy, r, color):
        c = _to_rgb(color)
        for yy in range(cy - r, cy + r + 1):
            dist = yy - cy
            if abs(dist) <= r:
                half = int((r * r - dist * dist) ** 0.5)
            else:
                half = 0
            self.fill_rect(cx - half, yy, half * 2 + 1, 1, c)

    def circle_outline(self, cx, cy, r, color, t=2):
        c = _to_rgb(color)
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if abs(d - r) <= t / 2:
                    self._put_pixel(xx, yy, c)

    def fill_poly(self, points, color):
        """Fill a polygon row by row, pairing edge crossings."""
        c = _to_rgb(color)
        heights = [p[1] for p in points]
        lo = max(0, min(heights))
        hi = min(self.h, max(heights) + 1)
        count = len(points)
        for yy in range(lo, hi):
            crossings = []
            for i in range(count):
                ax, ay = points[i]
                bx, by = points[(i + 1) % count]
                if (ay <= yy < by) or (by <= yy < ay):
                    crossings.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            crossings.sort()
            for k in range(0, len(crossings) - 1, 2):
                start_x = int(crossings[k])
                end_x = int(crossings[k + 1])
                self.fill_rect(start_x, yy, max(1, end_x - start_x), 1, c)

    # -- text ---------------------------------------------------------------------

    def text_width(self, text, font):
        glyphs = FONTS[font]
        width = 0
        for ch in text:
            g = glyphs.get(ch)
            if g is None:
                continue
            width += g[3] if len(g) > 3 else g[0]
        return width

    def draw_text(self, x, y, text, font, color):
        """Paint one line of bitmap text; returns the x past the last glyph."""
        c = _to_rgb(color)
        glyphs = FONTS[font]
        cx = x
        for ch in text:
            g = glyphs.get(ch)
            if g is None:
                cx += 6
                continue
            gw, gh, encoded = g[0], g[1], g[2]
            advance = g[3] if len(g) > 3 else gw
            drop = g[4] if len(g) > 4 else 0
            if gw and gh:
                raw = base64.b64decode(encoded)
                for row in range(gh):
                    offset = row * gw
                    for col in range(gw):
                        alpha = raw[offset + col]
                        if alpha:
                            self._put_pixel(cx + col, y + drop + row, c, alpha)
            cx += advance
        return cx

    def wrap_lines(self, text, font, max_w):
        """Split text into lines by greedy word wrap at max_w."""
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            candidate = (current + " " + word).strip()
            if self.text_width(candidate, font) <= max_w or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw_wrapped(self, x, y, max_w, text, font, color, leading=None):
        metrics = FONTS[font + "_metrics"]
        if leading is None:
            leading = metrics["ascent"] + metrics["descent"] + 2
        yy = y
        for line in self.wrap_lines(text, font, max_w):
            self.draw_text(x, yy, line, font, color)
            yy += leading
        return yy

    # -- PNG output -----------------------------------------------------------------

    def save_png(self, path):
        """Encode the buffer as an 8-bit RGB PNG, filter none, zlib level 9."""
        raw = bytearray()
        stride = self.w * 3
        for yy in range(self.h):
            raw.append(0)
            raw += self.px[yy * stride:(yy + 1) * stride]
        packed = zlib.compress(bytes(raw), 9)

        def emit(kind, data):
            piece = struct.pack(">I", len(data)) + kind + data
            piece += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            return piece

        header = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        png = b"\x89PNG\r\n\x1a\n"
        png += emit(b"IHDR", header)
        png += emit(b"IDAT", packed)
        png += emit(b"IEND", b"")
        with open(path, "wb") as handle:
            handle.write(png)
