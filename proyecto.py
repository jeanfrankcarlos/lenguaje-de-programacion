#!/usr/bin/env python3
# planificador_ahorros_pyqt6.py
import sys
import sqlite3
import datetime
import csv 
import shutil # Importación añadida para copiar archivos (backup)

from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QMessageBox, QLineEdit, QLabel, QPushButton,
    QGridLayout, QVBoxLayout, QHBoxLayout, QFrame, QProgressBar, QTableWidget,
    QTableWidgetItem, QInputDialog, QDialog, QFormLayout, QFileDialog 
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap 

# matplotlib for embedding the simple line chart
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ====== COLORES ======
BG_COLOR = "#f4f9f9" 
FRAME_COLOR = "#dff6f0" 
TEXT_COLOR = "#333"
BUTTON_COLORS = {
    "calcular": "#00a86b",
    "guardar": "#007bff",
    "finalizar": "#f0ad4e",
    "historial": "#6f42c1",
    "limpiar": "#f4a261",
    "borrar": "#dc3545",
    "regresar": "#6c757d",
    "exportar": "#17a2b8", 
    "backup": "#ff8c00" # Color para el botón de Backup
}

DB_FILE = "ahorros.db" # Nombre del archivo de la base de datos

# ====== BASE DE DATOS ======
def crear_base():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            contrasena TEXT
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

# ====== DIALOGO DE LOGIN ======
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ingreso de Usuario")
        self.setMinimumSize(QSize(380, 220))
        self.setWindowIcon(QIcon("logo.png")) 
        self.init_ui()
        self.usuario_id = None
        self.nombre = None

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("👤 Ingresa tu nombre de usuario")
        title.setFont(QFont("Helvetica", 12))
        layout.addWidget(title)

        self.nombre_edit = QLineEdit()
        self.nombre_edit.setPlaceholderText("Usuario")
        layout.addWidget(self.nombre_edit)

        pw_label = QLabel("🔒 Contraseña")
        pw_label.setFont(QFont("Helvetica", 12))
        layout.addWidget(pw_label)

        self.pw_edit = QLineEdit()
        self.pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pw_edit)

        btn_layout = QHBoxLayout()
        entrar_btn = QPushButton("Entrar")
        entrar_btn.clicked.connect(self.intentar_login)
        btn_layout.addStretch()
        btn_layout.addWidget(entrar_btn)
        layout.addLayout(btn_layout)

    def intentar_login(self):
        nombre = self.nombre_edit.text().strip()
        contrasena = self.pw_edit.text().strip()

        if not nombre or not contrasena:
            QMessageBox.critical(self, "Error", "Por favor ingresa usuario y contraseña.")
            return

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()

        # Compatibilidad: asegurar columna contrasena
        cur.execute("PRAGMA table_info(usuarios)")
        columnas = [col[1] for col in cur.fetchall()] 
        if "contrasena" not in columnas:
            cur.execute("ALTER TABLE usuarios ADD COLUMN contrasena TEXT")
            conn.commit()

        cur.execute("SELECT id, contrasena FROM usuarios WHERE nombre=?", (nombre,))
        row = cur.fetchone()

        if row:
            usuario_id, contrasena_guardada = row
            if contrasena == contrasena_guardada:
                conn.close()
                self.usuario_id = usuario_id
                self.nombre = nombre
                self.accept()
            else:
                conn.close()
                QMessageBox.critical(self, "Error", "Contraseña incorrecta.")
        else:
            resp = QMessageBox.question(self, "Nuevo usuario",
                                         f"El usuario '{nombre}' no existe. ¿Deseas crear una cuenta nueva?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if resp == QMessageBox.StandardButton.Yes:
                cur.execute("INSERT INTO usuarios (nombre, contrasena) VALUES (?, ?)", (nombre, contrasena))
                conn.commit()
                usuario_id = cur.lastrowid
                conn.close()
                QMessageBox.information(self, "Éxito", f"Cuenta creada para {nombre}.")
                self.usuario_id = usuario_id
                self.nombre = nombre
                self.accept()
            else:
                conn.close()
                return

# ====== VENTANA PRINCIPAL ======
class MainWindow(QMainWindow):
    def __init__(self, nombre_usuario, usuario_id):
        super().__init__()
        self.nombre_usuario = nombre_usuario
        self.usuario_id = usuario_id
        self.current_plan_id = None

        self.setWindowTitle(f"Planificador de Ahorros - {self.nombre_usuario}")
        self.setMinimumSize(QSize(900, 650))
        self.setWindowIcon(QIcon("logo.png"))
        
        self.init_ui()
        self.cargar_ultimo_plan()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)
        
        # Fondo de la ventana principal: color sólido base
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BG_COLOR}; 
                color: {TEXT_COLOR};
            }}
        """)
        
        # El widget central se hace transparente para que muestre el color de la QMainWindow
        central.setStyleSheet(f"background-color: transparent;")


        # Left frame: formulario
        left_frame = QFrame()
        left_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {FRAME_COLOR}; /* Color verde claro sólido */
                padding: 12px; 
                border-radius: 8px;
            }}
        """)
        left_frame.setMinimumWidth(420)
        main_layout.addWidget(left_frame)

        lf_layout = QGridLayout()
        left_frame.setLayout(lf_layout)

        # Escalar la imagen a 96x96 píxeles
        user_info_layout = QHBoxLayout()
        
        # Cargar la imagen del usuario
        # ¡IMPORTANTE! Reemplaza "user_icon.png" con el nombre real de tu archivo de imagen.
        user_pixmap = QPixmap("user_icon.png") 
        if not user_pixmap.isNull():
            user_pixmap = user_pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation) 
            user_icon_label = QLabel()
            user_icon_label.setPixmap(user_pixmap)
            user_info_layout.addWidget(user_icon_label)
        
        user_label = QLabel(f"🌟 Planificador de Ahorros - {self.nombre_usuario}")
        user_info_layout.addWidget(user_label)
        user_info_layout.addStretch() # Empuja el contenido hacia la izquierda

        lf_layout.addLayout(user_info_layout, 0, 0, 1, 2) # Agregar el layout con imagen y texto

        # Campos
        lf_layout.addWidget(QLabel("🎯 Meta de ahorro ($):"), 1, 0)
        self.meta_edit = QLineEdit(); self.meta_edit.setText("0.00"); lf_layout.addWidget(self.meta_edit, 1, 1)
        self.meta_edit.textChanged.connect(self.calcular_plan)

        lf_layout.addWidget(QLabel("⏳ Plazo (meses):"), 2, 0)
        self.plazo_edit = QLineEdit(); self.plazo_edit.setText("1"); lf_layout.addWidget(self.plazo_edit, 2, 1)
        self.plazo_edit.textChanged.connect(self.calcular_plan)

        lf_layout.addWidget(QLabel("💰 Ingreso mensual ($):"), 3, 0)
        self.ingreso_edit = QLineEdit(); self.ingreso_edit.setText("0.00"); lf_layout.addWidget(self.ingreso_edit, 3, 1)
        self.ingreso_edit.textChanged.connect(self.calcular_plan)

        lf_layout.addWidget(QLabel("🍽️ Comida ($):"), 4, 0)
        self.comida_edit = QLineEdit(); self.comida_edit.setText("0.00"); lf_layout.addWidget(self.comida_edit, 4, 1)
        self.comida_edit.textChanged.connect(self.calcular_plan)

        lf_layout.addWidget(QLabel("🚌 Transporte ($):"), 5, 0)
        self.transporte_edit = QLineEdit(); self.transporte_edit.setText("0.00"); lf_layout.addWidget(self.transporte_edit, 5, 1)
        self.transporte_edit.textChanged.connect(self.calcular_plan)

        lf_layout.addWidget(QLabel("📱 Otros gastos ($):"), 6, 0)
        self.otros_edit = QLineEdit(); self.otros_edit.setText("0.00"); lf_layout.addWidget(self.otros_edit, 6, 1)
        self.otros_edit.textChanged.connect(self.calcular_plan)

        lf_layout.addWidget(QLabel("💵 Ahorro actual ($):"), 7, 0)
        self.ahorrado_edit = QLineEdit(); self.ahorrado_edit.setText("0.00"); lf_layout.addWidget(self.ahorrado_edit, 7, 1)
        self.ahorrado_edit.textChanged.connect(self.calcular_plan)

        lf_layout.addWidget(QLabel("📆 Aporte sugerido mensual ($):"), 8, 0)
        self.aporte_label = QLabel("--"); lf_layout.addWidget(self.aporte_label, 8, 1)

        # Resultado / progreso / alerta (Contenedor derecho)
        right_vbox = QVBoxLayout()
        main_layout.addLayout(right_vbox)
        
        right_vbox_widget = QWidget()
        right_vbox_widget.setLayout(right_vbox)
        right_vbox_widget.setStyleSheet("background-color: transparent;")
        main_layout.addWidget(right_vbox_widget)


        self.resultado_label = QLabel("")
        self.resultado_label.setFont(QFont("Helvetica", 11))
        right_vbox.addWidget(self.resultado_label)

        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        right_vbox.addWidget(self.progress)

        self.alerta_label = QLabel("")
        right_vbox.addWidget(self.alerta_label)

        self.faltante_label = QLabel("")
        right_vbox.addWidget(self.faltante_label)

        self.mes_label = QLabel("")
        self.mes_label.setFont(QFont("Helvetica", 10, QFont.Weight.Bold))
        right_vbox.addWidget(self.mes_label)

        # Gráfico embebido (matplotlib)
        self.figure = Figure(figsize=(6, 2.5), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: white; border-radius: 6px;") # Fondo blanco sólido para el gráfico
        right_vbox.addWidget(self.canvas)

        # Botones panel derecho (organizados en grid)
        btn_frame = QFrame()
        btn_frame.setStyleSheet("background-color: transparent;") # Marco de botones transparente
        
        btn_layout = QGridLayout() 
        
        btn_frame.setLayout(btn_layout)
        right_vbox.addWidget(btn_frame)

        # Lista de botones con Exportar Datos y Backup DB
        botones = [
            ("Calcular Plan", self.calcular_plan, BUTTON_COLORS["calcular"]),
            ("Guardar Datos", self.guardar_datos, BUTTON_COLORS["guardar"]),
            ("Finalizar Mes", self.finalizar_mes, BUTTON_COLORS["finalizar"]),
            ("Ver Historial", self.ver_historial, BUTTON_COLORS["historial"]),
            ("Limpiar Datos", self.limpiar_datos, BUTTON_COLORS["limpiar"]),
            ("Borrar Todo", self.borrar_datos_usuario, BUTTON_COLORS["borrar"]),
            ("Exportar Datos", self.exportar_datos, BUTTON_COLORS["exportar"]), 
            ("Extraer Backup DB", self.extraer_backup_db, BUTTON_COLORS["backup"]), 
            ("Regresar", self.regresar_login, BUTTON_COLORS["regresar"]),
        ]

        for i, (texto, cmd, color) in enumerate(botones):
            btn = QPushButton(texto)
            btn.setMinimumWidth(180)
            btn.clicked.connect(cmd)
            btn.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
            r = i // 2
            c = i % 2
            btn_layout.addWidget(btn, r, c)

        self.plot_sin_datos()

    # ====== FUNCIONES DE LÓGICA ======
    
    def calcular_plan(self):
        try:
            meta = float(self.meta_edit.text())
            plazo = int(self.plazo_edit.text())
            ingreso = float(self.ingreso_edit.text())
            comida = float(self.comida_edit.text())
            transporte = float(self.transporte_edit.text())
            otros = float(self.otros_edit.text())
            ahorrado = float(self.ahorrado_edit.text())

            if plazo <= 0:
                 self.resultado_label.setText("⚠️ El plazo debe ser mayor que 0.")
                 self.progress.setValue(0)
                 self.alerta_label.setText("")
                 self.faltante_label.setText("")
                 return

            gastos_totales = comida + transporte + otros
            disponible = ingreso - gastos_totales
            
            if disponible < 0:
                 self.resultado_label.setText("⚠️ Gastos superan ingresos. No puedes ahorrar.")
                 self.alerta_label.setText(f"💸 Te faltan ${abs(disponible):.2f} para cubrir gastos.")
                 self.progress.setValue(0)
                 self.aporte_label.setText("$0.00/mes")
                 self.faltante_label.setText("")
                 return
            else:
                 self.alerta_label.setText(f"✅ Disponible para ahorro: ${disponible:.2f}/mes")

            faltante = meta - ahorrado
            
            if faltante <= 0:
                aporte_necesario = 0
                self.faltante_label.setText("🎉 Meta alcanzada.")
                self.resultado_label.setText("✅ ¡Felicidades! Meta ya cumplida.")
            else:
                aporte_necesario = faltante / plazo
                self.faltante_label.setText(f"💸 Te faltan ${faltante:.2f}")
                self.resultado_label.setText(f"✅ Ahorrando ${aporte_necesario:.2f} por mes, alcanzarás la meta.")
            
            self.aporte_label.setText(f"${aporte_necesario:.2f}/mes")

            progreso = int((ahorrado / meta) * 100) if meta > 0 else 0
            self.progress.setValue(max(0, min(progreso, 100)))

        except ValueError:
             self.resultado_label.setText("⚠️ Introduce valores numéricos válidos en todos los campos.")
             self.progress.setValue(0)
             self.aporte_label.setText("--")
             self.alerta_label.setText("")
             self.faltante_label.setText("")
        except Exception as e:
            QMessageBox.critical(self, "Error de Cálculo", f"Error desconocido: {e}")


    def guardar_datos(self):
        try:
            meta = float(self.meta_edit.text())
            plazo = int(self.plazo_edit.text())
            ingreso = float(self.ingreso_edit.text())
            comida = float(self.comida_edit.text())
            transporte = float(self.transporte_edit.text())
            otros = float(self.otros_edit.text())
            ahorrado = float(self.ahorrado_edit.text())
        except ValueError:
            QMessageBox.critical(self, "Error", "Completa todos los campos con valores numéricos válidos antes de guardar.")
            return

        if meta <= 0 or plazo <= 0:
             QMessageBox.critical(self, "Error", "Meta y Plazo deben ser mayores a cero.")
             return

        datos = (
            meta, plazo, ingreso, comida, transporte, otros,
            ahorrado, self.usuario_id, datetime.date.today().isoformat()
        )
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO planes_ahorro (meta, plazo, ingreso, comida, transporte, otros, ahorrado, usuario_id, fecha_inicio, mes_actual)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, datos)
            conn.commit()
            self.current_plan_id = cur.lastrowid
            conn.close()
            QMessageBox.information(self, "Éxito", "Nuevo plan de ahorro guardado correctamente.")
            self.actualizar_grafico()
            self.calcular_plan() 
            self.mes_label.setText("📅 Plan iniciado en Mes 1.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron guardar los datos.\n{e}")

    def finalizar_mes(self):
        if not self.current_plan_id:
            QMessageBox.warning(self, "Atención", "Primero guarda un plan antes de finalizar un mes.")
            return

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT mes_actual, plazo, ahorrado, meta FROM planes_ahorro WHERE id=?", (self.current_plan_id,))
        row = cur.fetchone()
        
        if not row:
            conn.close()
            QMessageBox.critical(self, "Error", "No se encontró el plan de ahorro activo.")
            return

        mes_actual, plazo, ahorrado, meta = row
        
        if mes_actual > plazo:
            conn.close()
            QMessageBox.information(self, "Plan completado", "🎉 Ya has finalizado todos los meses de tu plan.")
            return

        monto_sugerido = 0
        try:
            faltante = meta - ahorrado
            if faltante > 0 and (plazo - mes_actual + 1) > 0:
                monto_sugerido = faltante / (plazo - mes_actual + 1)
        except Exception:
            monto_sugerido = 0
            
        monto, ok = QInputDialog.getDouble(self, "Finalizar mes", 
                                          f"¿Cuánto ahorraste en el **Mes {mes_actual}**?\n(Aporte sugerido: ${monto_sugerido:.2f})", 
                                          value=monto_sugerido, decimals=2, min=-1000000)
        
        if not ok:
            conn.close()
            return
            
        if monto < 0:
             QMessageBox.warning(self, "Advertencia", "El monto ahorrado no puede ser negativo, por favor ajusta tus gastos o meta.")
             conn.close()
             return

        nuevo_ahorrado = ahorrado + monto
        
        cur.execute("UPDATE planes_ahorro SET ahorrado=?, mes_actual=? WHERE id=?", 
                    (nuevo_ahorrado, mes_actual + 1, self.current_plan_id))
        
        cur.execute("INSERT INTO ahorros_mensuales (plan_id, mes, monto, fecha) VALUES (?, ?, ?, ?)",
                      (self.current_plan_id, mes_actual, monto, datetime.date.today().isoformat()))
        conn.commit()
        conn.close()

        self.ahorrado_edit.setText(f"{nuevo_ahorrado:.2f}")
        self.actualizar_grafico()
        self.calcular_plan()
        
        self.mes_label.setText(f"📅 Mes {mes_actual} finalizado. Nuevo mes: {mes_actual + 1}")

        if mes_actual == plazo:
            QMessageBox.information(self, "Plan completado", "🎉 Has cumplido el plazo del plan de ahorro.")
            self.mes_label.setText("🎉 Plan finalizado.")
        
        if nuevo_ahorrado >= meta and mes_actual <= plazo:
             QMessageBox.information(self, "¡Meta cumplida!", "🌟 ¡Has alcanzado la meta antes de tiempo!")
             self.resultado_label.setText("✅ Meta alcanzada.")


    def actualizar_grafico(self):
        if not self.current_plan_id:
            self.plot_sin_datos()
            return
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT mes, monto, fecha FROM ahorros_mensuales WHERE plan_id=? ORDER BY mes", (self.current_plan_id,))
        datos = cur.fetchall()
        conn.close()
        
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT meta, plazo FROM planes_ahorro WHERE id=?", (self.current_plan_id,))
        plan_data = cur.fetchone()
        meta_total = plan_data[0] if plan_data else 0.0
        plazo_total = plan_data[1] if plan_data else 0
        conn.close()

        if not datos:
            self.plot_sin_datos()
            return

        meses = [d[0] for d in datos]
        montos_mensuales = [d[1] for d in datos]
        montos_acumulados = [sum(montos_mensuales[:i+1]) for i in range(len(montos_mensuales))]
        
        try:
            fecha_inicio = datetime.datetime.fromisoformat(datos[0][2])
            mes_inicio = fecha_inicio.month
        except Exception:
            mes_inicio = datetime.date.today().month

        nombres_meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        etiquetas = [nombres_meses[(mes_inicio + i - 1) % 12] for i in range(len(meses))]

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.plot(range(len(montos_acumulados)), montos_acumulados, marker='o', linewidth=2, label="Ahorro Acumulado")
        
        if meta_total > 0:
            ax.axhline(meta_total, color='r', linestyle='--', label="Meta")
            
        ruta_ideal = [(meta_total / plazo_total) * (i + 1) for i in range(len(montos_acumulados))]
        if ruta_ideal and plazo_total > 0:
             ax.plot(range(len(ruta_ideal)), ruta_ideal, color='g', linestyle=':', label="Ruta Ideal")
             
        ax.set_xticks(range(len(montos_acumulados)))
        ax.set_xticklabels(etiquetas, rotation=45, fontsize=8)
        ax.set_ylabel("Monto Acumulado ($)")
        ax.set_title("Progreso del Ahorro")
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.legend(loc='upper left', fontsize='small')
        self.canvas.draw()

    def plot_sin_datos(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, "Sin datos de ahorro aún", horizontalalignment='center', verticalalignment='center', fontsize=12, color='gray')
        ax.set_xticks([]); ax.set_yticks([])
        self.canvas.draw()

    def ver_historial(self):
        if not self.current_plan_id:
            QMessageBox.information(self, "Historial", "No hay plan cargado para mostrar historial.")
            return

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT mes, monto, fecha FROM ahorros_mensuales WHERE plan_id=? ORDER BY mes", (self.current_plan_id,))
        datos = cur.fetchall()
        conn.close()

        tabla = QDialog(self)
        tabla.setWindowTitle(f"📋 Historial de {self.nombre_usuario}")
        tabla.setMinimumSize(QSize(500, 350))
        tabla.setWindowIcon(QIcon("logo.png"))
        v = QVBoxLayout()
        tabla.setLayout(v)

        table_widget = QTableWidget()
        table_widget.setColumnCount(3)
        table_widget.setHorizontalHeaderLabels(["Mes", "Monto Ahorrado ($)", "Fecha"])
        table_widget.setRowCount(len(datos))
        for i, row in enumerate(datos):
            table_widget.setItem(i, 0, QTableWidgetItem(str(row[0])))
            table_widget.setItem(i, 1, QTableWidgetItem(f"{row[1]:.2f}"))
            table_widget.setItem(i, 2, QTableWidgetItem(str(row[2])))
        v.addWidget(table_widget)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(tabla.close)
        v.addWidget(close_btn)
        
        tabla.exec()

    def limpiar_datos(self):
        if not self.current_plan_id:
            QMessageBox.warning(self, "Atención", "Primero guarda un plan antes de limpiar.")
            return
            
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT ahorrado, mes_actual FROM planes_ahorro WHERE id=?", (self.current_plan_id,))
        plan = cur.fetchone()
        conn.close()
        
        if not plan:
             QMessageBox.warning(self, "Atención", "Plan no encontrado. No se puede limpiar.")
             return

        resp = QMessageBox.question(self, "Confirmar", 
                                    "¿Seguro que quieres **borrar todos los registros mensuales** de este plan?\n(El total ahorrado y el mes actual se resetearán)",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp != QMessageBox.StandardButton.Yes:
            return
        
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("DELETE FROM ahorros_mensuales WHERE plan_id=?", (self.current_plan_id,))
        cur.execute("UPDATE planes_ahorro SET ahorrado=0.0, mes_actual=1 WHERE id=?", (self.current_plan_id,))
        conn.commit()
        conn.close()
        
        self.ahorrado_edit.setText("0.00")
        self.mes_label.setText("📅 Plan iniciado en Mes 1.")
        self.plot_sin_datos()
        self.calcular_plan() 
        
        QMessageBox.information(self, "Limpieza completada", "Se han borrado los registros del plan actual y se ha reseteado el progreso.")

    def borrar_datos_usuario(self):
        resp = QMessageBox.question(self, "Confirmar", 
                                    "⚠️ **Advertencia:** ¿Deseas borrar **TODOS** los planes y registros de ahorro de este usuario? Esta acción es irreversible.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp != QMessageBox.StandardButton.Yes:
            return
            
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM planes_ahorro WHERE usuario_id=?", (self.usuario_id,))
        plan_ids = [row[0] for row in cur.fetchall()]

        for plan_id in plan_ids:
            cur.execute("DELETE FROM ahorros_mensuales WHERE plan_id=?", (plan_id,))

        cur.execute("DELETE FROM planes_ahorro WHERE usuario_id=?", (self.usuario_id,))
        cur.execute("DELETE FROM usuarios WHERE id=?", (self.usuario_id,))
        
        conn.commit()
        conn.close()
        
        QMessageBox.information(self, "Éxito", "Todos los datos y planes del usuario han sido borrados.")
        self.close()
        main()

    # Método para extraer backup de la DB
    def extraer_backup_db(self):
        # Generar nombre sugerido con fecha
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_sugerido = f"backup_{DB_FILE.replace('.db', '')}_{fecha_actual}.db"
        
        # Abrir diálogo para seleccionar dónde guardar
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar Copia de Seguridad de la Base de Datos", 
                                                  nombre_sugerido,
                                                  "Archivos de Base de Datos SQLite (*.db)")

        if not filename:
            return

        try:
            # Copiar el archivo de la DB al destino seleccionado
            shutil.copyfile(DB_FILE, filename)
            QMessageBox.information(self, "Éxito", f"Copia de seguridad guardada correctamente en:\n{filename}")
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"No se encontró el archivo de la base de datos: {DB_FILE}")
        except Exception as e:
            QMessageBox.critical(self, "Error de Backup", f"No se pudo guardar la copia de seguridad: {e}")

    def exportar_datos(self):
        if not self.current_plan_id:
            QMessageBox.warning(self, "Atención", "No hay plan de ahorro cargado para exportar.")
            return

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        
        # Obtener datos del plan y de los ahorros mensuales
        cur.execute("SELECT meta, plazo, ingreso, comida, transporte, otros, ahorrado, mes_actual FROM planes_ahorro WHERE id=?", (self.current_plan_id,))
        plan_data = cur.fetchone()
        
        cur.execute("SELECT mes, monto, fecha FROM ahorros_mensuales WHERE plan_id=? ORDER BY mes", (self.current_plan_id,))
        ahorro_mensual_data = cur.fetchall()
        
        conn.close()

        if not plan_data and not ahorro_mensual_data:
             QMessageBox.information(self, "Exportar", "No hay datos para exportar en el plan actual.")
             return

        # Abrir diálogo para guardar archivo
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar Historial de Ahorros", 
                                                  f"historial_ahorros_{self.nombre_usuario}.csv",
                                                  "Archivos CSV (*.csv)")

        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Encabezado del Plan
                writer.writerow(["Plan de Ahorro", self.nombre_usuario])
                writer.writerow(["Métrica", "Valor"])
                
                # Datos del Plan
                writer.writerow(["Meta", f"{plan_data[0]:.2f}"])
                writer.writerow(["Plazo (meses)", plan_data[1]])
                writer.writerow(["Ingreso Mensual", f"{plan_data[2]:.2f}"])
                writer.writerow(["Comida", f"{plan_data[3]:.2f}"])
                writer.writerow(["Transporte", f"{plan_data[4]:.2f}"])
                writer.writerow(["Otros Gastos", f"{plan_data[5]:.2f}"])
                writer.writerow(["Ahorrado Total", f"{plan_data[6]:.2f}"])
                writer.writerow(["Mes Actual", plan_data[7]])
                writer.writerow([]) # Fila vacía para separación
                
                # Datos Mensuales
                writer.writerow(["Historial Mensual"])
                writer.writerow(["Mes", "Monto Ahorrado ($)", "Fecha"])
                
                # Escribir registros mensuales
                for row in ahorro_mensual_data:
                    writer.writerow(row)
            
            QMessageBox.information(self, "Éxito", f"Datos exportados correctamente a:\n{filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error de Exportación", f"No se pudieron exportar los datos: {e}")

    def regresar_login(self):
        resp = QMessageBox.question(self, "Cerrar sesión", "¿Deseas salir de la cuenta actual?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp == QMessageBox.StandardButton.Yes:
            self.close()
            main()

    def cargar_ultimo_plan(self):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT id FROM planes_ahorro WHERE usuario_id=? ORDER BY id DESC LIMIT 1", (self.usuario_id,))
        row = cur.fetchone()
        
        if row:
            self.current_plan_id = row[0]
            cur.execute("SELECT meta, plazo, ingreso, comida, transporte, otros, ahorrado, mes_actual FROM planes_ahorro WHERE id=?", (self.current_plan_id,))
            p = cur.fetchone()
            
            if p:
                try:
                    meta, plazo, ingreso, comida, transporte, otros, ahorrado, mes_actual = p
                    
                    self.meta_edit.setText(f"{meta:.2f}")
                    self.plazo_edit.setText(str(plazo))
                    self.ingreso_edit.setText(f"{ingreso:.2f}")
                    self.comida_edit.setText(f"{comida:.2f}")
                    self.transporte_edit.setText(f"{transporte:.2f}")
                    self.otros_edit.setText(f"{otros:.2f}")
                    self.ahorrado_edit.setText(f"{ahorrado:.2f}")
                    self.mes_label.setText(f"📅 Plan cargado. Mes actual: {mes_actual}")
                except Exception:
                    QMessageBox.warning(self, "Carga incompleta", "El último plan no pudo cargarse por completo. Por favor, revisa o crea uno nuevo.")
            
            self.actualizar_grafico()
            self.calcular_plan() 
            
        else:
            self.mes_label.setText("📅 No hay planes guardados. Crea uno nuevo.")
            
        conn.close()

# ====== EJECUTAR APLICACIÓN ======
def main():
    app = QApplication(sys.argv)
    dlg = LoginDialog()
    if dlg.exec() == QDialog.DialogCode.Accepted:
        nombre = dlg.nombre
        usuario_id = dlg.usuario_id
        ventana = MainWindow(nombre, usuario_id)
        ventana.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()