import tkinter as tk
from tkinter import ttk, messagebox

# Colores
BG_COLOR = "#f4f9f9"
FRAME_COLOR = "#dff6f0"
BUTTON_COLOR = "#00a86b"
TEXT_COLOR = "#333"

# Ventana principal
ventana = tk.Tk()
ventana.title("Planificador de Ahorros")
ventana.geometry("550x730")
ventana.configure(bg=BG_COLOR)

# Título
tk.Label(ventana, text="🌟 Planificador de Ahorros Personales", font=("Helvetica", 16, "bold"),
         bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)

# ====== SECCIÓN: META Y PLAZO ======
meta_frame = tk.Frame(ventana, bg=FRAME_COLOR, padx=15, pady=10)
meta_frame.pack(pady=10, fill="x", padx=20)

tk.Label(meta_frame, text="🎯 Meta de ahorro ($):", bg=FRAME_COLOR).grid(row=0, column=0, sticky="w")
meta_entry = tk.Entry(meta_frame)
meta_entry.grid(row=0, column=1)

tk.Label(meta_frame, text="⏳ Plazo (meses):", bg=FRAME_COLOR).grid(row=1, column=0, sticky="w", pady=5)
plazo_entry = tk.Entry(meta_frame)
plazo_entry.grid(row=1, column=1)

# ====== SECCIÓN: GASTOS MENSUALES ======
gastos_frame = tk.Frame(ventana, bg=FRAME_COLOR, padx=15, pady=10)
gastos_frame.pack(pady=10, fill="x", padx=20)

tk.Label(gastos_frame, text="💰 Ingreso mensual ($):", bg=FRAME_COLOR).grid(row=0, column=0, sticky="w")
ingreso_entry = tk.Entry(gastos_frame)
ingreso_entry.grid(row=0, column=1)

tk.Label(gastos_frame, text="🍽️ Comida ($):", bg=FRAME_COLOR).grid(row=1, column=0, sticky="w")
comida_entry = tk.Entry(gastos_frame)
comida_entry.grid(row=1, column=1)

tk.Label(gastos_frame, text="🚌 Transporte ($):", bg=FRAME_COLOR).grid(row=2, column=0, sticky="w")
transporte_entry = tk.Entry(gastos_frame)
transporte_entry.grid(row=2, column=1)

tk.Label(gastos_frame, text="📱 Otros gastos ($):", bg=FRAME_COLOR).grid(row=3, column=0, sticky="w")
otros_entry = tk.Entry(gastos_frame)
otros_entry.grid(row=3, column=1)

# ====== SECCIÓN: APORTES Y PROGRESO ======
aporte_frame = tk.Frame(ventana, bg=FRAME_COLOR, padx=15, pady=10)
aporte_frame.pack(pady=10, fill="x", padx=20)

tk.Label(aporte_frame, text="💵 Ahorro actual ($):", bg=FRAME_COLOR).grid(row=0, column=0, sticky="w")
ahorrado_entry = tk.Entry(aporte_frame)
ahorrado_entry.grid(row=0, column=1)

tk.Label(aporte_frame, text="📆 Aporte sugerido mensual ($):", bg=FRAME_COLOR).grid(row=1, column=0, sticky="w", pady=5)
aporte_sugerido_label = tk.Label(aporte_frame, text="--", bg=FRAME_COLOR, fg="blue")
aporte_sugerido_label.grid(row=1, column=1, sticky="w")

# ====== RESULTADOS Y ALERTAS ======
resultado_label = tk.Label(ventana, text="", font=("Helvetica", 12), bg=BG_COLOR, fg=TEXT_COLOR)
resultado_label.pack(pady=10)

# Barra de progreso
progress = ttk.Progressbar(ventana, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=10)

# Alertas y cuánto falta
alerta_label = tk.Label(ventana, text="", font=("Helvetica", 11, "bold"), bg=BG_COLOR)
alerta_label.pack()

faltante_label = tk.Label(ventana, text="", font=("Helvetica", 11), bg=BG_COLOR, fg=TEXT_COLOR)
faltante_label.pack()

# ====== FUNCIÓN PRINCIPAL ======
def calcular_plan():
    try:
        meta = float(meta_entry.get())
        plazo = int(plazo_entry.get())
        ingreso = float(ingreso_entry.get())
        comida = float(comida_entry.get())
        transporte = float(transporte_entry.get())
        otros = float(otros_entry.get())
        ahorrado = float(ahorrado_entry.get())

        gastos_totales = comida + transporte + otros
        disponible = ingreso - gastos_totales

        if disponible <= 0:
            resultado_label.config(text="⚠️ No puedes ahorrar: tus gastos superan tus ingresos.")
            progress["value"] = 0
            alerta_label.config(text="", fg="red")
            faltante_label.config(text="")
            return

        aporte_necesario = (meta - ahorrado) / plazo

        if aporte_necesario > disponible:
            resultado_label.config(
                text=f"❌ No es posible alcanzar la meta con tus gastos actuales.\n"
                     f"Necesitas ahorrar ${aporte_necesario:.2f}/mes."
            )
            alerta_label.config(text="Revisa tus gastos o extiende el plazo.", fg="red")
            progress["value"] = (ahorrado / meta) * 100
            faltante = meta - ahorrado
            if faltante > 0:
                faltante_label.config(text=f"💸 Te faltan ${faltante:.2f} para alcanzar tu meta.")
            else:
                faltante_label.config(text="✅ Ya alcanzaste tu meta o la superaste.")
            return

        # Todo OK
        aporte_sugerido_label.config(text=f"${aporte_necesario:.2f}/mes")
        resultado_label.config(text=f"✅ Puedes alcanzar tu meta en {plazo} meses.")

        porcentaje = (ahorrado / meta) * 100
        progress["value"] = porcentaje

        # Alertas visuales
        if porcentaje >= 100:
            alerta_label.config(text="🎉 ¡Meta alcanzada!", fg="green")
        elif porcentaje >= 80:
            alerta_label.config(text="🟢 Estás muy cerca de lograr tu meta.", fg="green")
        elif porcentaje >= 50:
            alerta_label.config(text="🟡 Vas por la mitad. ¡Sigue así!", fg="orange")
        else:
            alerta_label.config(text="🔴 Aún te falta bastante. Mantente constante.", fg="red")

        # Mostrar cuánto falta
        faltante = meta - ahorrado
        if faltante > 0:
            faltante_label.config(text=f"💸 Te faltan ${faltante:.2f} para alcanzar tu meta.")
        else:
            faltante_label.config(text="✅ Ya alcanzaste tu meta o la superaste.")

    except ValueError:
        messagebox.showerror("Error", "Completa todos los campos con valores válidos.")

# ====== BOTÓN ======
tk.Button(ventana, text="Calcular Plan de Ahorro", bg=BUTTON_COLOR, fg="white",
          font=("Helvetica", 12), command=calcular_plan).pack(pady=20)

# ====== AYUDA ======
tk.Label(ventana,
         text="ℹ️ Ingresa tu meta y plazo. El sistema calcula cuánto debes ahorrar\n"
              "mensualmente según tus ingresos y gastos.\n"
              "Puedes registrar tu ahorro actual y recibirás alertas del progreso.",
         bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 10), justify="center").pack(pady=10)

# Ejecutar app
ventana.mainloop()
