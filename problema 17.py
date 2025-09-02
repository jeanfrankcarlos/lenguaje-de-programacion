# Definir los salarios mensuales en un arreglo en soles
salarios_mensuales_pen = [3000, 3200, 3100, 3300, 3400, 3500]

# Definir el tipo de cambio de soles a dólares
tipo_cambio = 3.54  # 1 dólar = 3.54 soles

# Calcular el salario total en medio año en soles
total_medio_año_pen = sum(salarios_mensuales_pen)

# Calcular el descuento del 10% en soles
descuento_pen = total_medio_año_pen * 0.10

# Calcular el total después del descuento en soles
total_con_descuento_pen = total_medio_año_pen - descuento_pen

# Convertir el total final a dólares
total_con_descuento_usd = total_con_descuento_pen / tipo_cambio

# --- Impresión de resultados ---

print("Cálculo en Soles Peruanos (PEN):")
print(f"Salario total en medio año: S/.{total_medio_año_pen:,.2f}")
print(f"Descuento del 10%: S/.{descuento_pen:,.2f}")
print(f"Total después del descuento: S/.{total_con_descuento_pen:,.2f}")

print("\n--------------------------------")

print("Cálculo en Dólares Estadounidenses (USD):")
print(f"Total después del descuento: ${total_con_descuento_usd:,.2f}")
