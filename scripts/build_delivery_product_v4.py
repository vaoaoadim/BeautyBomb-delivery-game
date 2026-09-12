"""Extract the roof tube only from immutable v8, with one 2x backing export."""
from hashlib import sha256
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / 'visual-references/veh-001-courier-clean-concept-v8-flip-top.png'
OUTPUT = ROOT / 'public/assets/game/products/prd-003-delivery-transfer-v4.png'
EXPECTED = '05cf34de50f85d87b17e0db96a6f79c0ea4890c9702dfa4f1176a5e2955bb531'
# Original contour above the mounting rail. Excludes both straps, rail, van,
# and cast shadows. No texture is invented or painted over the product.
CONTOUR = [(265,164),(281,149),(359,149),(375,161),(379,144),
           (1055,78),(1055,412),(1009,412),(1009,395),(379,354),
           (373,362),(360,375),(280,375),(265,358)]

def main():
    assert sha256(MASTER.read_bytes()).hexdigest() == EXPECTED
    master = Image.open(MASTER).convert('RGBA')
    # The right roof clamp occludes the lower tube edge. Restore that tiny
    # region from the directly adjacent clean product column before masking.
    for x in range(819, 870):
        for y in range(360, 397):
            master.putpixel((x,y), master.getpixel((818,y)))
    matte = Image.new('L', master.size)
    ImageDraw.Draw(matte).polygon(CONTOUR, fill=255)
    master.putalpha(ImageChops.multiply(master.getchannel('A'), matte))
    # Crop only alpha padding; 90 degrees is an exact transpose, no resampling.
    tube = master.crop(master.getbbox()).transpose(Image.Transpose.ROTATE_90)
    content_height = 108
    content_width = round(tube.width * content_height / tube.height)
    tube = tube.resize((content_width, content_height), Image.Resampling.NEAREST)
    runtime = Image.new('RGBA', (64,128))
    runtime.alpha_composite(tube, ((64-content_width)//2,10))
    runtime.save(OUTPUT)
    meta = {
        'assetId':'PRD-003', 'version':'v4', 'status':'integrated',
        'canvas':{'width':64,'height':128}, 'runtimeScale':0.5,
        'orientation':'vertical; identical roof tube rotated counterclockwise, cap down',
        'production':{'designMaster':str(MASTER.relative_to(ROOT)).replace('\\','/'),
            'designMasterSha256':EXPECTED, 'sourceContour':CONTOUR,
            'occlusionRepair':'x819:870 y360:397 copied from adjacent tube column x818 before mask',
            'buildScript':'scripts/build_delivery_product_v4.py',
            'assetMode':'high-detail-pixel-style-raster',
            'offlineResizeCount':1, 'resizeFilter':'nearest-neighbor',
            'phaserTextureFilter':'nearest', 'paletteQuantization':False,
            'runtimeSource':'versioned master; not screenshot or runtime sprite',
            'runtimeSha256':sha256(OUTPUT.read_bytes()).hexdigest()},
    }
    OUTPUT.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    review = Image.new('RGBA',(560,400),(76,76,108,255))
    original = Image.open(MASTER).convert('RGBA')
    review.alpha_composite(original.crop((255,70,1065,440)).resize((405,185)),(10,10))
    old = Image.open(ROOT/'public/assets/game/products/prd-003-delivery-transfer-v3.png')
    review.alpha_composite(old.resize((64,128),Image.Resampling.NEAREST),(60,240))
    review.alpha_composite(runtime,(210,240))
    review.alpha_composite(runtime.resize((96,192),Image.Resampling.NEAREST),(395,200))
    review.convert('RGB').save(ROOT/'visual-references/prd-003-transfer-v4-review.png')
    print(json.dumps({'canvas':runtime.size,'content':tube.size,'singleResize':True}))

if __name__ == '__main__':
    main()
