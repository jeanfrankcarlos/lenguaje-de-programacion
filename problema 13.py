
factor_decimal = float(input("Ingrese un número decimal: "))
print(f"El bucle no ha comenzado. Ahora el factor es {factor_decimal}")

# El bucle se ejecuta un número de veces definido, por ejemplo, 10
for i in range(10):
    # La variable 'i' es un número entero (0, 1, 2, ...), 
    # pero el cálculo usa el factor decimal
    resultado = i * factor_decimal
    print(f"Paso {i}: {i} * {factor_decimal} = {resultado}")

print(f"El bucle ha terminado. El último valor de i es {i}")
