nombre = input("Dame un nombre completo: ")

print("Vamos a imprimir cada letra:")
for letra in nombre:
    print(f"Dame una {letra}")

print(f"¡El nombre completo es {nombre.upper()}!")
