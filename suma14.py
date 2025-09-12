def info_personal(nombre, edad, *pasatiempos, **redes_sociales):
    print(f"Nombre: {nombre}")
    print(f"Edad: {edad}")

    if pasatiempos:
        print("Pasatiempos:")
        for hobby in pasatiempos:
            print(f"* {pasatiempos}")

    if redes_sociales:
        print("Redes Sociales:")
        for red, usuario in redes_sociales.items():
            print(f"* {red}: {usuario}")

info_personal("Jean", 28, "leer", "viajar", tiktok="@JeanF", instagram="Jean.explora")
