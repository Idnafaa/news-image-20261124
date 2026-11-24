# image.py — a tiny pure-stdlib raster canvas and PNG writer.
# No third-party code: RGB bytearray buffer, scanline PNG via zlib.
import base64
import struct
import zlib

from font_data import FONTS


def _hex(rgb_hex):
    rgb_hex = rgb_hex.lstrip("#")
    return (int(rgb_hex[0:2], 16), int(rgb_hex[2:4], 16), int(rgb_hex[4:6], 16))


class Canvas:
    def __init__(self, width, height, bg="#F6F1E6"):
        self.w = width
        self.h = height
        self.px = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, bg)

    def _set(self, x, y, color, alpha=255):
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        i = (y * self.w + x) * 3
        if alpha >= 255:
            self.px[i], self.px[i + 1], self.px[i + 2] = color
        else:
            inv = 255 - alpha
            self.px[i] = (color[0] * alpha + self.px[i] * inv) // 255
            self.px[i + 1] = (color[1] * alpha + self.px[i + 1] * inv) // 255
            self.px[i + 2] = (color[2] * alpha + self.px[i + 2] * inv) // 255

    def fill_rect(self, x, y, w, h, color):
        c = _hex(color) if isinstance(color, str) else color
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

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
        c = _hex(color) if isinstance(color, str) else color
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        c = _hex(color) if isinstance(color, str) else color
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.fill_rect(cx - dx, yy, dx * 2 + 1, 1, c)

    def circle_outline(self, cx, cy, r, color, t=2):
        c = _hex(color) if isinstance(color, str) else color
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if abs(d - r) <= t / 2:
                    self._set(xx, yy, c)

    def fill_poly(self, points, color):
        c = _hex(color) if isinstance(color, str) else color
        ys = [p[1] for p in points]
        for yy in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            nodes = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    x = x0 + (yy - y0) * (x1 - x0) / (y1 - y0)
                    nodes.append(x)
            nodes.sort()
            for k in range(0, len(nodes) - 1, 2):
                self.fill_rect(int(nodes[k]), yy, max(1, int(nodes[k + 1]) - int(nodes[k])), 1, c)

    # ---- text ----
    def text_width(self, text, font):
        table = FONTS[font]
        total = 0
        for ch in text:
            g = table.get(ch)
            if g is None:
                continue
            total += g[3] if len(g) > 3 else g[0]
        return total

    def draw_text(self, x, y, text, font, color):
        c = _hex(color) if isinstance(color, str) else color
        table = FONTS[font]
        cx = x
        for ch in text:
            g = table.get(ch)
            if g is None:
                cx += 6
                continue
            w, h, b64 = g[0], g[1], g[2]
            adv = g[3] if len(g) > 3 else w
            dy = g[4] if len(g) > 4 else 0
            if w and h:
                raw = base64.b64decode(b64)
                for yy in range(h):
                    row = yy * w
                    for xx in range(w):
                        a = raw[row + xx]
                        if a:
                            self._set(cx + xx, y + dy + yy, c, a)
            cx += adv
        return cx

    def draw_wrapped(self, x, y, max_w, text, font, color, leading=None):
        table = FONTS[font]
        metrics = FONTS[font + "_metrics"]
        if leading is None:
            leading = metrics["ascent"] + metrics["descent"] + 2
        words = text.split(" ")
        lines = []
        cur = ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if self.text_width(trial, font) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        yy = y
        for ln in lines:
            self.draw_text(x, yy, ln, font, color)
            yy += leading
        return yy

    def save_png(self, path):
        raw = bytearray()
        stride = self.w * 3
        for yy in range(self.h):
            raw.append(0)  # filter: none
            raw += self.px[yy * stride:(yy + 1) * stride]
        comp = zlib.compress(bytes(raw), 9)

        def chunk(kind, data):
            out = struct.pack(">I", len(data)) + kind + data
            out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", ihdr)
        png += chunk(b"IDAT", comp)
        png += chunk(b"IEND", b"")
        with open(path, "wb") as f:
            f.write(png)
