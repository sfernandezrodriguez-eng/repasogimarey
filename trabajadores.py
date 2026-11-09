trabajadores = 0
entre_1000_y_1750 = 0
menos_de_1000 = 0

while True:
    dinero = float(input("Introduce el sueldo que gana marito en el only (0 para que muestre los datos): "))

    if dinero == 0:
        break
    if dinero < 0:
        print("El sueldo no puede ser negativo, gil.")
        continue

    trabajadores += 1
    if 1000 <= dinero <= 1750:
        entre_1000_y_1750 += 1
    elif dinero < 1000:
        menos_de_1000 += 1

porcentaje = menos_de_1000 * 100 / trabajadores if trabajadores else 0

print(f"Gorditos que ganan entre 1000 y 1750 €: {entre_1000_y_1750}")
print(f"Porcentaje de los tetones que ganan menos de 1000 €: {porcentaje:.2f}%")