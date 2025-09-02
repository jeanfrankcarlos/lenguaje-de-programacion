# Definir los salarios mensuales en un arreglo
salarios_mensuales = [3000, 3200, 3100, 3300, 3400, 3500]

# Calcular el salario total en medio año
total_medio_año = sum(salarios_mensuales)

# Calcular el descuento del 10%
descuento = total_medio_año * 0.10

# Calcular el total después del descuento
total_con_descuento = total_medio_año - descuento

# Formatear la salida para evitar los ceros finales en los decimales
# Usamos un f-string con .rstrip('0').rstrip('.') para este propósito
total_formateado = f"{total_con_descuento:f}".rstrip('0').rstrip('.')

# Imprimir los resultados
print(f"Salario total en medio año: ${total_medio_año:,.2f}")
print(f"Descuento del 10%: ${descuento:,.2f}")
print(f"Total después del descuento: ${total_formateado}")
