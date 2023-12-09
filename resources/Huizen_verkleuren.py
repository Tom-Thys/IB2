from PIL import Image
#import os


def aanpassen_afbeelding(input_image_path, output_image_path, kleur):
    verlichte_kleur = (min(255, kleur[0] + 10), min(255, kleur[1] + 10), min(255, kleur[2] + 10))

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
                    # lichte vlakken, minder hard delen
                    afbeelding.putpixel((x, y), verlichte_kleur)
                else:
                    # kleur huis
                    afbeelding.putpixel((x, y), kleur)

    afbeelding.save(output_image_path)

# Kleuren
Geen_texture_kleur = (0, 0, 0)
Groen = (141, 170, 127)
Grijs = (205, 201, 201)
Blauw = (102, 127, 171)
Paars = (180, 162, 200)
Geel =  (218, 165, 32)
Rood = (170, 85, 85)
Oranje = (204, 119, 102)
Haag = (0, 255, 0)
Einde_map_kleur = (255, 0, 20)
Post = (255,255,255)

#Volgorde van import in renderer (Geen_texture_kleur altijd eerst, gevolgd door 1x Rood(bakstenen) Eindemapkleur laatst)
volgorde = [Geen_texture_kleur, Rood, Rood, Groen, Blauw, Grijs, Paars, Geel, Oranje, Haag, Einde_map_kleur, Post]
"""Als er aanpassingen gebeuren aan deze lijst en de import van textures moeten deze worden doorgetrokken
Naar de worlds.py file op lijn 60"""



if __name__ == "__main__":
    input_afbeelding = "Huis.png"

    # aanpassen
    output_afbeelding = "Oranje_huis.png"

    aanpassen_afbeelding(input_afbeelding, output_afbeelding, Oranje)

    kleuren_dict = {}
    for i, kleur in enumerate(volgorde):
        kleuren_dict[i] = kleur#(max(0, kleur[0] - 20), max(0, kleur[1] - 20), max(0, kleur[2] - 20))
    print(kleuren_dict)