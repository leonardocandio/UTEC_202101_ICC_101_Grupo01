from graphviz import Digraph
from graphviz import Graph

n = int(input("Ingrese cantidad de países: "))
lista_paises = []
lista_vecinos = []
vecinos_locales = []
for i in range(n):
    name = input("Ingrese el nombre de cada país: ")
    lista_paises.append(name)

vecino = "_"

for k in lista_paises:
    print("Ingrese los vecinos de " + "\033[92m" + k + "\033[0m")
    print(
        "\033[93m"
        + "Para pasar al siguente pais introduzca una entrada vacía"
        + "\033[0m"
    )
    while vecino != "":
        vecino = input()
        if len(vecino) > 0:
            vecinos_locales.append(vecino)
        else:
            lista_vecinos.append(vecinos_locales)
            vecinos_locales = []
    vecino = "_"

d = dict(zip(lista_paises, lista_vecinos))

print(d)
