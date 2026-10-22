"""Reproducibly draw the app's original, transparent geometric PNG icons.

Only writes the fourteen named assets below. Never modifies pages or data.
Pillow renders at 8x size, then Lanczos downsamples for smooth fine outlines.
"""

from math import cos, sin, pi
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'miniprogram' / 'assets'
SIZE, SCALE, STROKE = 64, 8, 2.25


class Icon:
    def __init__(self, color):
        self.color = color
        self.image = Image.new('RGBA', (SIZE * SCALE, SIZE * SCALE), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def box(self, values):
        return tuple(round(v * SCALE) for v in values)

    def line(self, points, width=STROKE):
        pts = [(round(x * SCALE), round(y * SCALE)) for x, y in points]
        self.draw.line(pts, fill=self.color, width=round(width * SCALE), joint='curve')
        # Rounded end caps keep all outline icons visually consistent.
        radius = width * SCALE / 2
        for x, y in (pts[0], pts[-1]):
            self.draw.ellipse((round(x-radius), round(y-radius), round(x+radius), round(y+radius)), fill=self.color)

    def ellipse(self, box, width=STROKE):
        self.draw.ellipse(self.box(box), outline=self.color, width=round(width * SCALE))

    def rect(self, box, radius=3, width=STROKE):
        self.draw.rounded_rectangle(self.box(box), radius=round(radius * SCALE), outline=self.color, width=round(width * SCALE))

    def curve(self, points):
        """Draw connected cubic Beziers: start, then control/control/end triples."""
        start, samples = points[0], [points[0]]
        for index in range(1, len(points), 3):
            a, b, end = points[index:index+3]
            for step in range(1, 41):
                t, u = step / 40, 1 - step / 40
                samples.append((u**3*start[0]+3*u*u*t*a[0]+3*u*t*t*b[0]+t**3*end[0], u**3*start[1]+3*u*u*t*a[1]+3*u*t*t*b[1]+t**3*end[1]))
            start = end
        self.line(samples)

    def save(self, name):
        target = OUT / (name + '.png')
        self.image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(target, optimize=True)
        return target


def navigation(name, color):
    icon = Icon(color)
    if name == 'home':
        icon.line([(13, 29), (32, 13), (51, 29)])
        icon.line([(18, 27), (18, 51), (28, 51), (28, 37), (37, 37), (37, 51), (46, 51), (46, 27)])
    elif name == 'library':
        for x, y in [(14, 14), (36, 14), (14, 36), (36, 36)]:
            icon.rect((x, y, x+14, y+14), radius=3)
    else:
        icon.line([(19, 13), (45, 13), (45, 52), (32, 43), (19, 52), (19, 13)])
        icon.line([(26, 23), (38, 23)])
    return icon


def theme(name, color):
    icon = Icon(color)
    if name == 'health':
        icon.curve([(32, 20), (21, 6), (4, 20), (16, 34), (21, 40), (28, 46), (32, 49), (36, 46), (43, 40), (48, 34), (60, 20), (43, 6), (32, 20)])
        icon.line([(13, 30), (23, 30), (27, 23), (32, 38), (37, 28), (40, 30), (51, 30)])
    elif name == 'safety':
        icon.curve([(32, 12), (26, 16), (19, 18), (13, 19), (13, 36), (17, 45), (32, 52), (47, 45), (51, 36), (51, 19), (45, 18), (38, 16), (32, 12)])
        icon.line([(23, 32), (29, 38), (42, 25)])
    elif name == 'money':
        icon.ellipse((12, 12, 52, 52))
        icon.line([(24, 21), (32, 30), (40, 21)])
        icon.line([(32, 30), (32, 44)])
        icon.line([(24, 31), (40, 31)])
        icon.line([(24, 37), (40, 37)])
    elif name == 'rights':
        icon.line([(32, 13), (32, 49)])
        icon.line([(14, 22), (32, 18), (50, 22)])
        icon.line([(17, 22), (11, 36), (23, 36), (17, 22)])
        icon.curve([(11, 36), (13, 42), (21, 42), (23, 36)])
        icon.line([(47, 22), (41, 36), (53, 36), (47, 22)])
        icon.curve([(41, 36), (43, 42), (51, 42), (53, 36)])
        icon.line([(23, 50), (41, 50)])
    elif name == 'growth':
        icon.line([(12, 27), (12, 49), (23, 47), (32, 50), (41, 47), (52, 49), (52, 27), (41, 25)])
        icon.line([(12, 27), (22, 25), (32, 29), (32, 50)])
        icon.line([(32, 28), (32, 18)])
        icon.curve([(32, 22), (23, 22), (21, 15), (23, 12), (31, 11), (34, 17), (32, 22)])
        icon.curve([(32, 20), (32, 13), (40, 11), (45, 13), (44, 20), (38, 23), (32, 20)])
    elif name == 'family':
        icon.line([(11, 29), (32, 12), (53, 29)])
        icon.line([(17, 27), (17, 51), (47, 51), (47, 27)])
        icon.ellipse((27, 27, 37, 37))
        icon.curve([(24, 48), (24, 37), (40, 37), (40, 48)])
    elif name == 'wellbeing':
        icon.ellipse((22, 22, 42, 42))
        for index in range(8):
            angle = index * pi / 4
            icon.line([(32 + cos(angle)*17, 32 + sin(angle)*17), (32 + cos(angle)*23, 32 + sin(angle)*23)])
    elif name == 'digital':
        icon.rect((11, 14, 53, 44), radius=4)
        icon.line([(12, 37), (52, 37)])
        icon.line([(32, 44), (32, 51)])
        icon.line([(23, 52), (41, 52)])
        icon.line([(24, 22), (20, 26), (24, 30)])
        icon.line([(40, 22), (44, 26), (40, 30)])
        icon.line([(34, 21), (30, 31)])
    return icon


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    paths = []
    for active, color in [(False, '#94816E'), (True, '#C2530C')]:
        for name in ('home', 'library', 'saved'):
            paths.append(navigation(name, color).save(name + ('-active' if active else '')))
    for name, color in [
        ('health', '#BB623E'), ('safety', '#5E7FAD'), ('money', '#B18431'),
        ('rights', '#8770AC'), ('growth', '#7A905A'), ('family', '#B97879'),
        ('wellbeing', '#BD883A'), ('digital', '#5C918A'),
    ]:
        paths.append(theme(name, color).save('theme-' + name))
    print('Prepared 6 navigation icons + 8 theme icons, RGBA 64 x 64.')
    for path in paths:
        print(f'{path.name}: {path.stat().st_size} bytes')
    print(f'Total: {sum(path.stat().st_size for path in paths)} bytes')


if __name__ == '__main__':
    main()
