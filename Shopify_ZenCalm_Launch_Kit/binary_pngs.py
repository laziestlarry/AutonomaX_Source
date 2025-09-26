from PIL import Image, ImageDraw, ImageFilter
import random, os

os.makedirs("images", exist_ok=True)

def make_abstract(path, seed, w=2000, h=2500):
    rnd = random.Random(seed)
    img = Image.new("RGB", (w, h), (rnd.randint(200,255), rnd.randint(220,255), rnd.randint(220,255)))
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(12):
        color = (rnd.randint(120,200), rnd.randint(140,210), rnd.randint(140,210), rnd.randint(60,120))
        y = int(h*(i/12.0)) + rnd.randint(-40,40)
        d.rectangle([(0,y), (w, y + rnd.randint(60,160))], fill=color)
    for i in range(9):
        r = rnd.randint(120, 420)
        x = rnd.randint(-100, w+100)
        y = rnd.randint(-100, h+100)
        c = (rnd.randint(100,180), rnd.randint(110,190), rnd.randint(110,190), rnd.randint(70,140))
        d.ellipse([(x-r, y-r), (x+r, y+r)], fill=c)
    img = img.filter(ImageFilter.GaussianBlur(radius=3))
    img.save(path, "PNG", optimize=True)

for i in range(1,6):
    make_abstract(f"images/ZenCalm_{i:02d}.png", seed=1000+i)