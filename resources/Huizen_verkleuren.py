from PIL import Image
import os

def aanpassen_afbeelding(input_image_path, output_image_path):
    afbeelding = Image.open(input_image_path)
    pixels = afbeelding.convert("RGB")
    pixel_array = pixels.load()

    breedte, hoogte = afbeelding.size
    for x in range(breedte):
        for y in range(hoogte):
            rood, groen, blauw = pixels.getpixel((x, y))
            if rood > groen and rood > blauw:
                if groen > 150 and blauw > 5:
                    continue
                elif groen > 80:
                    #lichte vlakken, minder hard delen
                    afbeelding.putpixel((x, y), (int(rood/1.3),int(rood/1.3), int(rood/1.3)))
                else:
                    #kleur huis
                    afbeelding.putpixel((x, y), (int(rood / 1.4), int(rood / 1.4), int(rood / 1.4)))

    afbeelding.save(output_image_path)

if __name__ == "__main__":
    input_afbeelding = "Huis.png"

    #aanpassen
    output_afbeelding = "Grijs_huis.png"

    aanpassen_afbeelding(input_afbeelding, output_afbeelding)