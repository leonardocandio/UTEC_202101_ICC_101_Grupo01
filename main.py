n = int(input("Ingrese cantidad de países: "))
p = []
v = []
for i in range(n):
    name = input("Ingrese el nombre de cada país: ")
    p.append(name)

vecino = ""

while vecino != "Siguiente":
    for k in p:
        vecino = input(
            f"Ingrese los vecinos de {k}\nPara pasar el siguiente país escriba Siguiente "
        )
