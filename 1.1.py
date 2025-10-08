import tkinter as tk 
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import datetime

# ====== COLORES ======
BG_COLOR = "#f4f9f9"
FRAME_COLOR = "#dff6f0"
TEXT_COLOR = "#333"
BUTTON_COLORS = {
    "calcular": "#00a86b",   # verde
    "guardar": "#007bff",    # azul
    "finalizar": "#f0ad4e",  # dorado
    "historial": "#6f42c1",  # morado
    "borrar": "#dc3545",     # rojo
    "regresar": "#6c757d"    # gris
}

# ====== BASE DE DATOS ======
def crear_base():
    conn = sqlite3.connect("ahorros.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS planes_ahorro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            meta REAL,
            plazo INTEGER,
            ingreso REAL,
            comida REAL,
            transporte REAL,
            otros REAL,
            ahorrado REAL,
            mes_actual INTEGER DEFAULT 1,
            fecha_inicio TEXT,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ahorros_mensuales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER,
            mes INTEGER,
            monto REAL,
            fecha TEXT,
            FOREIGN KEY(plan_id) REFERENCES planes_ahorro(id)
        )
    """)
    conn.commit()
    conn.close()

crear_base()

# ====== LOGIN ======
def login_usuario():
    nombre = nombre_entry.get().strip()
    if not nombre:
        messagebox.showerror("Error", "Por favor ingresa un nombre.")
        return

    conn = sqlite3.connect("ahorros.db")
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE nombre=?", (nombre,))
    row = cur.fetchone()

    if row:
        usuario_id = row[0]
    else:
        cur.execute("INSERT INTO usuarios (nombre) VALUES (?)", (nombre,))
        conn.commit()
        usuario_id = cur.lastrowid

    conn.close()
    login_window.destroy()
    abrir_ventana_principal(nombre, usuario_id)

# ====== VENTANA PRINCIPAL ======
def abrir_ventana_principal(nombre_usuario, usuario_id):
    ventana = tk.Tk()
    ventana.title(f"Planificador de Ahorros - {nombre_usuario}")
    ventana.geometry("700x750")
    ventana.configure(bg=BG_COLOR)

    tk.Label(ventana, text=f"🌟 Planificador de Ahorros - {nombre_usuario}",
             font=("Helvetica", 16, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)

    # === FRAMES DE SECCIONES ===
    frames = {}
    for key in ("meta", "gastos", "aporte"):
        frames[key] = tk.Frame(ventana, bg=FRAME_COLOR, padx=15, pady=10)
        frames[key].pack(pady=8, fill="x", padx=20)

    # === META Y PLAZO ===
    tk.Label(frames["meta"], text="🎯 Meta de ahorro ($):", bg=FRAME_COLOR).grid(row=0, column=0, sticky="w")
    meta_entry = tk.Entry(frames["meta"]); meta_entry.grid(row=0, column=1)
    tk.Label(frames["meta"], text="⏳ Plazo (meses):", bg=FRAME_COLOR).grid(row=1, column=0, sticky="w", pady=5)
    plazo_entry = tk.Entry(frames["meta"]); plazo_entry.grid(row=1, column=1)

    # === GASTOS ===
    labels = ["💰 Ingreso mensual ($):", "🍽️ Comida ($):", "🚌 Transporte ($):", "📱 Otros gastos ($):"]
    entries = []
    for i, text in enumerate(labels):
        tk.Label(frames["gastos"], text=text, bg=FRAME_COLOR).grid(row=i, column=0, sticky="w")
        e = tk.Entry(frames["gastos"]); e.grid(row=i, column=1); entries.append(e)
    ingreso_entry, comida_entry, transporte_entry, otros_entry = entries

    # === APORTE Y AHORRO ===
    tk.Label(frames["aporte"], text="💵 Ahorro actual ($):", bg=FRAME_COLOR).grid(row=0, column=0, sticky="w")
    ahorrado_entry = tk.Entry(frames["aporte"]); ahorrado_entry.grid(row=0, column=1)
    tk.Label(frames["aporte"], text="📆 Aporte sugerido mensual ($):", bg=FRAME_COLOR).grid(row=1, column=0, sticky="w", pady=5)
    aporte_sugerido_label = tk.Label(frames["aporte"], text="--", bg=FRAME_COLOR, fg="blue")
    aporte_sugerido_label.grid(row=1, column=1, sticky="w")

    # === RESULTADOS ===
    resultado_label = tk.Label(ventana, text="", font=("Helvetica", 12), bg=BG_COLOR, fg=TEXT_COLOR)
    resultado_label.pack(pady=8)
    progress = ttk.Progressbar(ventana, orient="horizontal", length=400, mode="determinate")
    progress.pack(pady=5)
    alerta_label = tk.Label(ventana, text="", font=("Helvetica", 11, "bold"), bg=BG_COLOR)
    alerta_label.pack()
    faltante_label = tk.Label(ventana, text="", font=("Helvetica", 11), bg=BG_COLOR, fg=TEXT_COLOR)
    faltante_label.pack()
    mes_label = tk.Label(ventana, text="", font=("Helvetica", 11), bg=BG_COLOR, fg="blue")
    mes_label.pack()

    # === CANVAS PARA GRÁFICO ===
    canvas = tk.Canvas(ventana, width=450, height=200, bg="white", relief="ridge", bd=2)
    canvas.pack(pady=10)

    current_plan_id = None

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
                progress["value"] = 0; alerta_label.config(text="", fg="red"); faltante_label.config(text=""); return

            aporte_necesario = (meta - ahorrado) / plazo
            aporte_sugerido_label.config(text=f"${aporte_necesario:.2f}/mes")
            resultado_label.config(text=f"✅ Puedes alcanzar tu meta en {plazo} meses.")
            progress["value"] = (ahorrado / meta) * 100
            faltante = meta - ahorrado
            faltante_label.config(text=f"💸 Te faltan ${faltante:.2f}" if faltante > 0 else "✅ Meta alcanzada.")

        except ValueError:
            messagebox.showerror("Error", "Completa todos los campos con valores válidos.")

    def guardar_datos():
        nonlocal current_plan_id
        try:
            datos = (
                float(meta_entry.get()), int(plazo_entry.get()), float(ingreso_entry.get()),
                float(comida_entry.get()), float(transporte_entry.get()), float(otros_entry.get()),
                float(ahorrado_entry.get()), usuario_id, datetime.date.today().isoformat()
            )
            conn = sqlite3.connect("ahorros.db")
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO planes_ahorro (meta, plazo, ingreso, comida, transporte, otros, ahorrado, usuario_id, fecha_inicio, mes_actual)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, datos)
            conn.commit()
            current_plan_id = cur.lastrowid
            conn.close()
            messagebox.showinfo("Éxito", "Datos guardados correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los datos.\n{e}")

    def finalizar_mes():
        if not current_plan_id:
            messagebox.showwarning("Atención", "Primero guarda un plan antes de finalizar un mes.")
            return

        monto = simpledialog.askfloat("Finalizar mes", "¿Cuánto ahorraste este mes?")
        if monto is None: return

        conn = sqlite3.connect("ahorros.db")
        cur = conn.cursor()
        cur.execute("SELECT mes_actual, plazo, ahorrado, meta FROM planes_ahorro WHERE id=?", (current_plan_id,))
        row = cur.fetchone()

        if not row:
            conn.close()
            messagebox.showerror("Error", "No se encontró el plan de ahorro.")
            return

        mes_actual, plazo, ahorrado, meta = row

        # 🔧 Validaciones
        if mes_actual is None:
            mes_actual = 1
        if plazo is None:
            messagebox.showerror("Error", "El plazo no está definido en este plan.")
            conn.close()
            return
        if mes_actual > plazo:
            messagebox.showinfo("Plan completado", "🎉 Ya has finalizado todos los meses de tu plan.")
            conn.close()
            return

        nuevo_ahorrado = ahorrado + monto
        cur.execute("""
            UPDATE planes_ahorro SET ahorrado=?, mes_actual=? WHERE id=?
        """, (nuevo_ahorrado, mes_actual + 1, current_plan_id))
        cur.execute("""
            INSERT INTO ahorros_mensuales (plan_id, mes, monto, fecha)
            VALUES (?, ?, ?, ?)
        """, (current_plan_id, mes_actual, monto, datetime.date.today().isoformat()))
        conn.commit()
        conn.close()

        ahorrado_entry.delete(0, tk.END)
        ahorrado_entry.insert(0, nuevo_ahorrado)
        actualizar_grafico()
        mes_label.config(text=f"📅 Mes {mes_actual} finalizado.")

        if mes_actual >= plazo:
            messagebox.showinfo("Plan completado", "🎉 Has cumplido el plazo del plan de ahorro.")
            actualizar_grafico()

    def actualizar_grafico():
        if not current_plan_id: return
        conn = sqlite3.connect("ahorros.db")
        cur = conn.cursor()
        cur.execute("SELECT mes, monto FROM ahorros_mensuales WHERE plan_id=? ORDER BY mes", (current_plan_id,))
        datos = cur.fetchall()
        conn.close()
        canvas.delete("all")
        if not datos: return
        max_monto = max([d[1] for d in datos]) if datos else 1
        for i, (mes, monto) in enumerate(datos):
            x1 = 40 + i * 50; y1 = 180 - (monto / max_monto * 150)
            canvas.create_oval(x1 - 3, y1 - 3, x1 + 3, y1 + 3, fill="blue")
            if i > 0:
                x0 = 40 + (i - 1) * 50; y0 = 180 - (datos[i - 1][1] / max_monto * 150)
                canvas.create_line(x0, y0, x1, y1, fill="green", width=2)
        for i, (mes, _) in enumerate(datos):
            canvas.create_text(40 + i * 50, 190, text=f"M{mes}", font=("Helvetica", 8))

    def ver_historial():
        ventana_historial = tk.Toplevel(ventana)
        ventana_historial.title(f"📋 Historial de {nombre_usuario}")
        ventana_historial.geometry("500x400")
        ventana_historial.configure(bg=BG_COLOR)
        tree = ttk.Treeview(ventana_historial, columns=("Mes", "Monto", "Fecha"), show="headings")
        tree.heading("Mes", text="Mes"); tree.heading("Monto", text="Monto Ahorrado ($)"); tree.heading("Fecha", text="Fecha")
        tree.pack(fill="both", expand=True, pady=10, padx=10)
        conn = sqlite3.connect("ahorros.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT mes, monto, fecha FROM ahorros_mensuales
            WHERE plan_id=? ORDER BY mes
        """, (current_plan_id,))
        for row in cur.fetchall(): tree.insert("", "end", values=row)
        conn.close()

    def borrar_datos():
        if messagebox.askyesno("Confirmar", "¿Deseas borrar todos los datos de este usuario?"):
            conn = sqlite3.connect("ahorros.db")
            cur = conn.cursor()
            cur.execute("DELETE FROM planes_ahorro WHERE usuario_id=?", (usuario_id,))
            cur.execute("DELETE FROM ahorros_mensuales WHERE plan_id NOT NULL")
            conn.commit(); conn.close()
            messagebox.showinfo("Éxito", "Datos borrados correctamente.")
            ventana.destroy(); mostrar_login()

    def regresar_login():
        if messagebox.askyesno("Cerrar sesión", "¿Deseas salir de la cuenta actual?"):
            ventana.destroy(); mostrar_login()

    # === BOTONES EN CUADRÍCULA ===
    botones_frame = tk.Frame(ventana, bg=BG_COLOR)
    botones_frame.pack(pady=15)

    botones = [
        ("Calcular Plan", calcular_plan, BUTTON_COLORS["calcular"]),
        ("Guardar Datos", guardar_datos, BUTTON_COLORS["guardar"]),
        ("Finalizar Mes", finalizar_mes, BUTTON_COLORS["finalizar"]),
        ("Ver Historial", ver_historial, BUTTON_COLORS["historial"]),
        ("Borrar Datos", borrar_datos, BUTTON_COLORS["borrar"]),
        ("Regresar al Inicio", regresar_login, BUTTON_COLORS["regresar"]),
    ]

    for i, (texto, cmd, color) in enumerate(botones):
        tk.Button(
            botones_frame, text=texto, bg=color, fg="white",
            font=("Helvetica", 11, "bold"), width=18, command=cmd
        ).grid(row=i//2, column=i%2, padx=10, pady=8)

    ventana.mainloop()

# ====== LOGIN WINDOW ======
def mostrar_login():
    global login_window, nombre_entry
    login_window = tk.Tk()
    login_window.title("Ingreso de Usuario")
    login_window.geometry("400x200")
    login_window.configure(bg=BG_COLOR)

    tk.Label(login_window, text="👤 Ingresa tu nombre de usuario", bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 13)).pack(pady=20)
    nombre_entry = tk.Entry(login_window, font=("Helvetica", 12)); nombre_entry.pack(pady=10)
    tk.Button(login_window, text="Entrar", bg=BUTTON_COLORS["calcular"], fg="white",
              font=("Helvetica", 12), command=login_usuario).pack(pady=10)

    login_window.mainloop()

# ====== EJECUTAR APP ======
mostrar_login()
