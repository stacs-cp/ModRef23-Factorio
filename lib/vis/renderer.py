from PIL import Image, ImageDraw, ImageFont
from matplotlib import font_manager
import os

ASSET_FOLDER = "assets"
FONT_SIZE = 26

TILE_SIZE = 64
ROTATIONS = [0, 0, 180, 270, 90]

LAYOUT    = ["conveyors", "inserters", "assemblers"]
LOGISTICS = ["routes", "carrying"]


# Load .png files in the given asset folder
def load_assets(folder):
    assets = dict()

    for file in os.scandir(folder):
        if file.is_dir() or not file.name.endswith(".png"):
            continue

        img = Image.open(file.path)
        assets[os.path.splitext(file.name)[0]] = img

    return assets


# Try to load a monospace font, or the PIL default if none are found
def load_fonts():
    # Try to load Consolas font
    try:
        file = font_manager.findfont('Consolas')
        return ImageFont.truetype(file, FONT_SIZE)
    except:
        # Consolas not available, look for any monospace font
        try:
            font_search = font_manager.FontProperties(family='monospace', weight='normal')
            file = font_manager.findfont(font_search)
            return ImageFont.truetype(file, FONT_SIZE)
        except:
            # No monospace fonts available, use default font
            return ImageFont.load_default()


# Draw an image representing the described layout
def render_layout(dvars):
    (width, height) = validate_dvars(dvars)
    res = Image.new("RGBA", (TILE_SIZE * width, TILE_SIZE * height))

    for row in range(height):
        for col in range(width):
            # Paste the tile using itself as a mask so empty tiles do not overwrite populated tiles
            tile = generate_tile(dvars, row, col)
            res.paste(tile, (TILE_SIZE * col, TILE_SIZE * row), tile)

            overlay = generate_tile_logistics(dvars, row, col)
            res.paste(overlay, (TILE_SIZE * col, TILE_SIZE * row), overlay)

    return res


# Ensure all variables are present and dimensions are consistent in the given solution
def validate_dvars(dvars):
    xs = set()
    ys = set()
    
    # Ensure all required decision variables are present
    for v in (LAYOUT + LOGISTICS):
        if v not in dvars:
            raise ValueError(f"Decision variable {v} not present in solution file")

    # Ensure all layout matrices have the same dimensions
    for v in LAYOUT:
        ys.add(len(dvars[v]))
        xs.add(len(dvars[v][0]))

    if len(xs) > 1 or len(ys) > 1:
        raise ValueError("Solution contains inconsistent blueprint dimensions")

    (width, )  = xs
    (height, ) = ys

    return width, height
    

# For a given tile, place a conveyor, inserter, or assembler if one is present
def generate_tile(dvars, row, col):
    if dvars["assemblers"][row][col] > 0:
        return assets["assembler"]

    elif dvars["inserters"][row][col] > 0:
        tile = assets["inserter"]
        return tile.rotate(ROTATIONS[dvars["inserters"][row][col]])

    elif dvars["conveyors"][row][col] > 0:
        tile = assets["conveyor"]
        return tile.rotate(ROTATIONS[dvars["conveyors"][row][col]])

    else:
        return Image.new("RGBA", (TILE_SIZE, TILE_SIZE))


# If the given tile is an assembler or the start of a route, display which items are carried by it
def generate_tile_logistics(dvars, row, col):
    tile = Image.new("RGBA", (TILE_SIZE, TILE_SIZE))
    canvas = ImageDraw.Draw(tile)
    
    if dvars["assemblers"][row][col] > 0 or dvars["routes"][row][col] == 1:
        carrying = dvars["carrying"][row][col] if dvars["carrying"][row][col] > 0 else ""

        # Generate a graphic to show the item(s)
        canvas.text((TILE_SIZE / 2, TILE_SIZE / 2), str(carrying), font=font, anchor="mm", fill="white", stroke_width=5, stroke_fill="black")

    return tile


# Load assets and fonts on script import
assets = load_assets(ASSET_FOLDER)
font = load_fonts()