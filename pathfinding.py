import heapq
import time

def pathfinding_gps2(world_map, shared_pad, shared_eindbestemming, shared_spelerpositie):
    time.sleep(1)  # wachten tot game volledig gestart en eindbestemming besloten is
    oud_speler_positie = [0, 0]
    oud_eindbestemming = [0, 0]
    while True:
        spelerpos = tuple(shared_spelerpositie)
        eindbestemming = tuple(shared_eindbestemming)
        if abs(oud_speler_positie[0] - spelerpos[0]) > 1 or abs(oud_speler_positie[1] - spelerpos[1]) > 1 \
                or (eindbestemming[0] != oud_eindbestemming[0] or eindbestemming[1] != oud_eindbestemming[1]):
            # print(f"pad: {pad}, best: {eindbestemming}")
            oud_speler_positie[:] = spelerpos[:]
            eindpositie = eindbestemming
            start = spelerpos
            buren = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # nu definieren, oogt beter bij de for loop
            close_set = set()  # set is ongeorderd, onveranderbaar en niet geïndexeerd
            came_from = {}  # dictionary die "parents" van de node klasse vervangt, aangezien zelfgemaakte klassen niet zo goed meespelen met heaps
            g_score = {start: 0}  # dictionary die g scores bijhoudt van alle posities
            f_score = {start: heuristiek(start, eindpositie)}  # dictionary die onze f scores bijhoudt bij iteratie
            oheap = []  # ~open_list van eerste pathfinding algoritme, bevat alle posities die we behandelen voor het kortste pad te vinden
            heapq.heappush(oheap, (
                f_score[start], start))  # we pushen de startpositie en f score op de oheap (f score later nodig)

            while oheap:  # kijken dat er posities zijn die we kunnen behandelen
                current = heapq.heappop(oheap)[
                    1]  # pop en return kleinste item van de heap: hier bekijken we de kleinste f score, [1] betekent dat we de positie terug willen
                if current == eindpositie:
                    pad = []
                    while current in came_from:
                        pad.append(current)
                        current = came_from[current]
                    if shared_pad[:] == pad[:]:
                        time.sleep(0.5)
                    else:
                        shared_pad[:] = pad[:]
                    break
                close_set.add(
                    current)  # indien we geen pad gevonden hebben, zetten we de huidige positie op de closed set, aangezien we deze behandelen

                for positie in buren:  # door alle buren gaan + hun g score berekenen
                    buur = (current[0] + positie[0], current[1] + positie[1])
                    buur_g_score = g_score[current] + heuristiek(current, buur)
                    if buur[0] > world_map.shape[1] or buur[0] < 0 or buur[1] > world_map.shape[0] or \
                            buur[1] < 0:
                        continue  # gaat naar de volgende buur
                    # kijken of we op deze positie kunnen stappen
                    if world_map[buur[1]][buur[0]] > 0:
                        continue
                    if buur in close_set and buur_g_score >= g_score.get(buur,
                                                                         0):  # dictionary.get(): buur: de positie van waar we de g score van terug willen, 0 indien er geen buur bestaat
                        continue  # kijken of de buur al behandeld is en ofdat de g score van de buur die we nu berekenen groter is als een vorige buur (indien kleiner kan dit wel een beter pad geven)
                    if buur_g_score < g_score.get(buur, 0) or buur not in [i[1] for i in
                                                                           oheap]:  # indien huidige buur g score lager is als een vorige buur of als de buur niet in de heap zit
                        came_from[buur] = current  # buur komt van huidige positie
                        g_score[buur] = buur_g_score
                        f_score[buur] = buur_g_score + heuristiek(buur, eindpositie)
                        heapq.heappush(oheap, (f_score[buur], buur))


def heuristiek(a, b):
    y = abs(a[0] - b[0])
    x = abs(a[1] - b[1])
    return 14 * y + 10 * (x - y) if y < x else 14 * x + 10 * (y - x)




def politie_pathfind(world_map , eindbestemming, spelerpositie):
    eindpositie = tuple(eindbestemming)
    start = tuple(spelerpositie)
    buren = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # nu definieren, oogt beter bij de for loop
    close_set = set()  # set is ongeorderd, onveranderbaar en niet geïndexeerd
    came_from = {}  # dictionary die "parents" van de node klasse vervangt, aangezien zelfgemaakte klassen niet zo goed meespelen met heaps
    g_score = {start: 0}  # dictionary die g scores bijhoudt van alle posities
    f_score = {start: heuristiek(start, eindpositie)}  # dictionary die onze f scores bijhoudt bij iteratie
    oheap = []  # ~open_list van eerste pathfinding algoritme, bevat alle posities die we behandelen voor het kortste pad te vinden
    heapq.heappush(oheap, (
        f_score[start], start))  # we pushen de startpositie en f score op de oheap (f score later nodig)

    while oheap:  # kijken dat er posities zijn die we kunnen behandelen
        current = heapq.heappop(oheap)[
            1]  # pop en return kleinste item van de heap: hier bekijken we de kleinste f score, [1] betekent dat we de positie terug willen
        if current == eindpositie:
            pad = []
            while current in came_from:
                pad.append(current)
                current = came_from[current]
            return pad
        close_set.add(current)  # indien we geen pad gevonden hebben, zetten we de huidige positie op de closed set, aangezien we deze behandelen

        for positie in buren:  # door alle buren gaan + hun g score berekenen
            buur = (current[0] + positie[0], current[1] + positie[1])
            buur_g_score = g_score[current] + heuristiek(current, buur)
            if buur[0] > world_map.shape[1] or buur[0] < 0 or buur[1] > world_map.shape[0] or \
                    buur[1] < 0:
                continue  # gaat naar de volgende buur
            # kijken of we op deze positie kunnen stappen
            if world_map[buur[1]][buur[0]] > 0:
                continue
            if buur in close_set and buur_g_score >= g_score.get(buur,
                                                                 0):  # dictionary.get(): buur: de positie van waar we de g score van terug willen, 0 indien er geen buur bestaat
                continue  # kijken of de buur al behandeld is en ofdat de g score van de buur die we nu berekenen groter is als een vorige buur (indien kleiner kan dit wel een beter pad geven)
            if buur_g_score < g_score.get(buur, 0) or buur not in [i[1] for i in
                                                                   oheap]:  # indien huidige buur g score lager is als een vorige buur of als de buur niet in de heap zit
                came_from[buur] = current  # buur komt van huidige positie
                g_score[buur] = buur_g_score
                f_score[buur] = buur_g_score + heuristiek(buur, eindpositie)
                heapq.heappush(oheap, (f_score[buur], buur))