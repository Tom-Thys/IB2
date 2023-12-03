from PIL import Image
import os

def aanpassen_afbeeldingen(input_map, output_map):
    # Controleer of de uitvoermap bestaat, anders maak deze aan
    if not os.path.exists(output_map):
        os.makedirs(output_map)


    for bestandsnaam in os.listdir(input_map):
        if bestandsnaam.endswith(('.png', '.jpg', '.jpeg')):
            pad_naar_afbeelding = os.path.join(input_map, bestandsnaam)
            afbeelding = Image.open(pad_naar_afbeelding)


            pixels = afbeelding.convert("RGB")
            pixel_array = pixels.load()

            breedte, hoogte = afbeelding.size
            for x in range(breedte):
                for y in range(hoogte):
                    rood, groen, blauw = pixels.getpixel((x, y))
                    if rood > groen and rood > blauw:
                        #Pas dit aan voor het kleur
                        afbeelding.putpixel((x, y), (int(rood/4), int(rood/3), int(rood/1.5)))

            nieuwe_bestandsnaam = os.path.join(output_map, bestandsnaam)
            afbeelding.save(nieuwe_bestandsnaam)

if __name__ == "__main__":

    invoermap = "Auto"
    #Pas dit aan als je een nieuwe map maakt
    uitvoermap = "Blauwe_auto"

    aanpassen_afbeeldingen(invoermap, uitvoermap)
