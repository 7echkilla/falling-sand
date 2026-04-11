import io
from PIL import Image, ImageDraw

def generate_gif_bytes(days):
    frames = []

    width = 53 * 12
    height = 7 * 12

    levels = [0, 1, 3, 6, 10]
    colors = [
        (235, 237, 240),
        (198, 228, 139),
        (123, 201, 111),
        (35, 154, 59),
        (25, 97, 39),
    ]

    for i in range(len(days)):
        img = Image.new("RGB", (width, height), "#ebedf0")
        draw = ImageDraw.Draw(img)

        for j in range(i + 1):
            x = (j // 7) * 12
            y = (j % 7) * 12
            count = days[j]["count"]

            color = colors[0]
            for k in range(1, len(levels)):
                if count >= levels[k]:
                    color = colors[k]

            draw.rectangle([x, y, x + 12, y + 12], fill=color)

        frames.append(img)

    gif_io = io.BytesIO()

    frames[0].save(
        gif_io,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0
    )

    return gif_io.getvalue()