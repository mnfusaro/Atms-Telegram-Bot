import csv
from itertools import islice
from os import path
from vincenty import vincenty


class Banco:
    """Representacion del objeto Banco, con su nombre, ubicacion y coordenadas"""

    def __init__(self, bank, address, lon, lat):
        self.name = bank
        self.address = address
        self.coordenadas = (lon, lat)

    def coords(self):
        return self.coordenadas

    def ubicacion(self):
        return self.address

    def nombre(self):
        return self.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def buscarCajeros(user_data):
    """Busca los 3 cajeros más cercanos al usuario.
        Devuelve una lista de Bancos."""

    with open(path.join("app","cajeros-automaticos.csv"), "r") as dataset:
        if user_data["firma"] == "LINK":
            cajeros = csv.reader(islice(dataset, 694, None), delimiter=";")

        else:
            cajeros = csv.reader(islice(dataset, 1, 694), delimiter=";")
        cajeros_cercanos = []
        for cajero in cajeros:
            if cajero[4] == user_data["firma"]:

                lon = float(cajero[2].replace(",","."))
                lat = float(cajero[1].replace(",","."))
                distancia_a_usuario = calcularDistancia((lon,lat), user_data["coordenadas"])

                if ( distancia_a_usuario <= 500):
                    banco_cercano = (Banco(cajero[3], cajero[5], lon, lat), distancia_a_usuario)
                    cajeros_cercanos.append(banco_cercano)

    cajeros_cercanos.sort(key=lambda banco: banco[1])

    return [cajero[0] for cajero in cajeros_cercanos[:3]]


def calcularDistancia(coordenadas_cajero, coordenadas_usuario):
    """Usa la formula de vincenty para calcular la distancia (en metros) entre el usuario y el cajero"""

    return (vincenty(coordenadas_cajero, coordenadas_usuario))* 1000