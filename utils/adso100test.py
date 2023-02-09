#!/usr/bin/env python

from bs4 import BeautifulSoup
from sys import argv
from libEscansion import VerseMetre

entrada = argv[1:]
salida = 'errores.log'
isought = 'isought.log'
for f in (salida, isought):
    with open(f, 'w') as fout:
        fout.write('')


def compara(verso):
    a = 1
    metro = verso.get('met')
    texto = verso.contents[0]
    escansion = VerseMetre(texto, [11, 7, 10, 12])
    resultado = escansion.rhythm
    if len(resultado) > len(metro) and len(metro) == 11:
        resultado = resultado[:-1]
    if resultado != metro:
        error = f'"{texto}" | o: "{metro}" | i: "{escansion.rhythm} {escansion.syllables}"\n'
        with open(isought, 'a') as foout:
            foout.write(error)
        print(error)
        error = f'<l n="1" met="{metro}">{texto}</l>\n'
        with open(salida, 'a') as fout:
            fout.write(error)
        a -= 1
    return a


total = 0
acertados = 0
fallados = 0
for fil in entrada:
    with open(fil, 'r') as f:
        print(fil)
        data = f.read()
        soup = BeautifulSoup(data, "xml")
        versos = soup.find_all('l')
        for verso in versos:
            #if 'oh' not in verso.contents[0].lower():
            total += 1
            comparaverso = compara(verso)
            acertados += comparaverso
            fallados += comparaverso - 1
            print(f'V: {total} \t A: {acertados} ({acertados/total*100} %), F: {fallados*-1} ({fallados/total*-100} %)\n')

