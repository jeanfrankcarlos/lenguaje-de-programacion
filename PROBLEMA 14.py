
# Crea una cadena de texto vacía para guardar las letras
nombre_completo = ""


# Bucle principal para pedir las letras
while True:
    letra = input("Dame una letra: ")

    # Si el usuario escribe ".", sal del bucle
    if letra.lower() == ".":
        break
    
    # Añade la letra a la cadena
    nombre_completo += letra

print(f"\nDame una {nombre_completo}")
print(f"¡{nombre_completo.upper()} FRANK!")
for letra
