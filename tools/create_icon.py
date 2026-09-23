"""Original ChatHelp artwork, generated from basic shapes; no upstream branding."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
painter = ImageDraw.Draw(canvas)
painter.rounded_rectangle((8, 8, 504, 504), 112, fill="#0F766E")
painter.rounded_rectangle((95, 112, 417, 352), 64, fill="white")
painter.polygon(((132, 318), (132, 419), (225, 345)), fill="white")
painter.line(((174, 188), (174, 278)), fill="#0F766E", width=24)
painter.line(((338, 188), (338, 278)), fill="#0F766E", width=24)
painter.line(((174, 233), (338, 233)), fill="#0F766E", width=24)
canvas.save(root / "docs/icon.ico", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
