from datetime import datetime
import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
import urllib.request

# CONFIGURACIÓN DEL SERVIDOR EN LA NUBE
# (Aquí colocarás la URL de un archivo JSON en la nube o tu API que controle las suscripciones)
# Ejemplo de estructura que debe tener tu archivo en la nube:
# {"barberia_carlos": {"activo": True, "expiracion": "2026-12-31"}, "barberia_luis": {"activo": False, "expiracion": "2026-05-01"}}
URL_LICENCIAS_NUBE = "https://gist.githubusercontent.com/Jeyson-RD/9e112ec754f66de38103d5121edc6366/raw/3e097efa4f41d3c333a4c2b956d18596851e7b90/licencias.json"
CONFIG_FILE = "config.json"


class ValidadorSuscripcion:

  def __init__(self, root):
    self.root = root
    self.root.title("🔐 Verificando Suscripción...")
    self.root.geometry("400x220")
    self.root.config(bg="#1e1e2f")
    self.centrar_ventana(400, 220)

    # Label de estado
    self.lbl_estado = tk.Label(
        root,
        text="Verificando licencia con el servidor...",
        bg="#1e1e2f",
        fg="#ffc107",
        font=("Segoe UI", 11, "bold"),
    )
    self.lbl_estado.pack(pady=40)

    self.barra_carga = ttk.Progressbar(
        root, orient="horizontal", length=300, mode="indeterminate"
    )
    self.barra_carga.pack(pady=10)
    self.barra_carga.start(10)

    # Ejecutar verificación de inmediato
    self.root.after(1000, self.verificar_en_linea)

  def centrar_ventana(self, ancho, alto):
    pantalla_ancho = self.root.winfo_screenwidth()
    pantalla_alto = self.root.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

  def verificar_en_linea(self):
    # 1. Obtener ID de la barbería local
    id_barberia = self.obtener_id_local()

    try:
      # 2. Consultar base de datos en la nube
      req = urllib.request.Request(
          URL_LICENCIAS_NUBE, headers={"User-Agent": "Mozilla/5.0"}
      )
      with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode())

        if id_barberia in data:
          info_cliente = data[id_barberia]
          activo = info_cliente.get("activo", False)
          fecha_exp = datetime.strptime(
              info_cliente.get("expiracion", "2000-01-01"), "%Y-%m-%d"
          )

          # 3. Validar si está activo y la fecha no ha expirado
          if activo and datetime.now() <= fecha_exp:
            self.root.destroy()
            lanzar_app_principal()
            return
          else:
            self.mostrar_error_suscripcion(
                "⚠️ Su suscripción mensual ha expirado.\nPor favor contacte al"
                " Administrador\npara realizar el pago (WhatsApp: +1 (809)"
                " 000-0000)."
            )
        else:
          self.mostrar_error_suscripcion(
              "❌ ID de Barbería no registrado en el sistema."
          )

    except Exception as e:
      # Modo de gracia por si no hay internet (puedes decidir si permitirlo temporalmente o bloquearlo)
      messagebox.showerror(
          "Error de Conexión",
          "No se pudo conectar con el servidor de licencias.\nVerifique su"
          " conexión a internet.",
      )
      self.root.destroy()

  def obtener_id_local(self):
    if os.path.exists(CONFIG_FILE):
      try:
        with open(CONFIG_FILE, "r") as f:
          return json.load(f).get("id_barberia", "desconocido")
      except:
        pass

    # Si no existe, crear un archivo de configuración por defecto
    default_config = {"id_barberia": "barberia_carlos"}
    with open(CONFIG_FILE, "w") as f:
      json.dump(default_config, f)
    return "barberia_carlos"

  def mostrar_error_suscripcion(self, mensaje):
    self.root.destroy()
    root_error = tk.Tk()
    root_error.title("Suscripción Vencida")
    root_error.geometry("450x250")
    root_error.config(bg="#1e1e2f")

    tk.Label(
        root_error,
        text=mensaje,
        bg="#1e1e2f",
        fg="#ff4d4d",
        font=("Segoe UI", 11, "bold"),
        justify="center",
    ).pack(pady=40)

    tk.Button(
        root_error,
        text="Salir",
        bg="#dc3545",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=15,
        command=root_error.destroy,
    ).pack(pady=10)
    root_error.mainloop()


# --- APLICACIÓN PRINCIPAL DE LA BARBERÍA ---
class BarberiaApp:

  def __init__(self, root):
    self.root = root
    self.root.title(
        "💈 BarberShop Manager | Sistema de Citas y Ganancias (RD$)"
    )
    self.root.geometry("900x600")
    self.root.config(bg="#1e1e2f")

    self.barberos = ["Carlos", "Luis", "Miguel"]
    self.servicios = {
        "Corte Clásico": 400.0,
        "Corte y Barba": 700.0,
        "Barba Completa": 300.0,
        "Fade / Degradado": 500.0,
    }
    self.citas = []

    self.style = ttk.Style()
    self.style.theme_use("clam")
    self.style.configure(
        "Treeview",
        background="#2b2b3c",
        foreground="white",
        fieldbackground="#2b2b3c",
        font=("Segoe UI", 10),
        rowheight=25,
    )
    self.style.configure(
        "Treeview.Heading",
        background="#3a3a52",
        foreground="white",
        font=("Segoe UI", 10, "bold"),
    )

    self.crear_interfaz()

  def crear_interfaz(self):
    # Encabezado
    header_frame = tk.Frame(self.root, bg="#252538", height=70)
    header_frame.pack(fill=tk.X, side=tk.TOP)
    header_frame.pack_propagate(False)

    tk.Label(
        header_frame,
        text="✂️ BARBERSHOP MANAGER (RD$)",
        bg="#252538",
        fg="#ffc107",
        font=("Segoe UI", 16, "bold"),
    ).pack(side=tk.LEFT, padx=20, pady=15)
    tk.Label(
        header_frame,
        text="Control de Citas y Ganancias",
        bg="#252538",
        fg="#a0a0b0",
        font=("Segoe UI", 10),
    ).pack(side=tk.RIGHT, padx=20, pady=15)

    main_frame = tk.Frame(self.root, bg="#1e1e2f")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    # Panel Izquierdo (Formulario)
    left_frame = tk.LabelFrame(
        main_frame,
        text=" 📝 Nueva Cita ",
        font=("Segoe UI", 11, "bold"),
        bg="#2b2b3c",
        fg="white",
        bd=2,
        relief="groove",
    )
    left_frame.place(relx=0, rely=0, relwidth=0.40, relheight=1.0)

    tk.Label(
        left_frame,
        text="Nombre del Cliente:",
        bg="#2b2b3c",
        fg="white",
        font=("Segoe UI", 10),
    ).pack(anchor="w", padx=15, pady=(15, 5))
    self.entry_cliente = tk.Entry(
        left_frame,
        font=("Segoe UI", 10),
        bg="#3a3a52",
        fg="white",
        insertbackground="white",
        relief="flat",
    )
    self.entry_cliente.pack(fill=tk.X, padx=15, pady=(0, 10), ipady=3)

    tk.Label(
        left_frame,
        text="Barbero:",
        bg="#2b2b3c",
        fg="white",
        font=("Segoe UI", 10),
    ).pack(anchor="w", padx=15, pady=(5, 5))
    self.combo_barbero = ttk.Combobox(
        left_frame, values=self.barberos, state="readonly", font=("Segoe UI", 10)
    )
    self.combo_barbero.pack(fill=tk.X, padx=15, pady=(0, 10))
    self.combo_barbero.current(0)

    tk.Label(
        left_frame,
        text="Servicio y Precio:",
        bg="#2b2b3c",
        fg="white",
        font=("Segoe UI", 10),
    ).pack(anchor="w", padx=15, pady=(5, 5))
    servicios_con_precio = [
        f"{serv} (RD$ {prec:,.2f})" for serv, prec in self.servicios.items()
    ]
    self.combo_servicio = ttk.Combobox(
        left_frame,
        values=servicios_con_precio,
        state="readonly",
        font=("Segoe UI", 10),
    )
    self.combo_servicio.pack(fill=tk.X, padx=15, pady=(0, 10))
    self.combo_servicio.current(0)

    tk.Label(
        left_frame,
        text="Fecha y Hora (DD/MM/YYYY HH:MM):",
        bg="#2b2b3c",
        fg="white",
        font=("Segoe UI", 10),
    ).pack(anchor="w", padx=15, pady=(5, 5))
    self.entry_fecha = tk.Entry(
        left_frame,
        font=("Segoe UI", 10),
        bg="#3a3a52",
        fg="white",
        insertbackground="white",
        relief="flat",
    )
    self.entry_fecha.pack(fill=tk.X, padx=15, pady=(0, 20), ipady=3)
    self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y 10:00"))

    tk.Button(
        left_frame,
        text="✨ Confirmar y Reservar Cita",
        bg="#28a745",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        cursor="hand2",
        relief="flat",
        command=self.agendar_cita,
    ).pack(fill=tk.X, padx=15, pady=10, ipady=5)

    # Panel Derecho (Tabla y Finanzas)
    right_frame = tk.LabelFrame(
        main_frame,
        text=" 📊 Agenda y Finanzas ",
        font=("Segoe UI", 11, "bold"),
        bg="#2b2b3c",
        fg="white",
        bd=2,
        relief="groove",
    )
    right_frame.place(relx=0.43, rely=0, relwidth=0.57, relheight=1.0)

    stats_frame = tk.Frame(right_frame, bg="#252538", bd=1, relief="solid")
    stats_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    self.lbl_ganancias = tk.Label(
        stats_frame,
        text="💰 Ganancias Totales Estimadas: RD$ 0.00",
        bg="#252538",
        fg="#28a745",
        font=("Segoe UI", 11, "bold"),
    )
    self.lbl_ganancias.pack(pady=10)

    tk.Button(
        right_frame,
        text="🗑️ Cancelar Cita Seleccionada",
        bg="#dc3545",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        cursor="hand2",
        relief="flat",
        command=self.cancelar_cita,
    ).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 5), ipady=4)

    columns = ("Cliente", "Barbero", "Servicio", "Precio", "Fecha/Hora")
    self.tabla = ttk.Treeview(right_frame, columns=columns, show="headings", height=11)
    for col in columns:
      self.tabla.heading(col, text=col)

    self.tabla.column("Cliente", width=90, anchor="w")
    self.tabla.column("Barbero", width=75, anchor="center")
    self.tabla.column("Servicio", width=105, anchor="w")
    self.tabla.column("Precio", width=75, anchor="center")
    self.tabla.column("Fecha/Hora", width=110, anchor="center")

    scrollbar = ttk.Scrollbar(
        right_frame, orient="vertical", command=self.tabla.yview
    )
    self.tabla.configure(yscrollcommand=scrollbar.set)
    self.tabla.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

  def agendar_cita(self):
    cliente = self.entry_cliente.get().strip()
    barbero = self.combo_barbero.get()
    seleccion_servicio = self.combo_servicio.get()
    fecha_hora = self.entry_fecha.get().strip()

    if not cliente:
      messagebox.showerror("Error", "El nombre del cliente no puede estar vacío.")
      return
    try:
      datetime.strptime(fecha_hora, "%d/%m/%Y %H:%M")
    except ValueError:
      messagebox.showerror(
          "Error", "Formato de fecha u hora incorrecto (DD/MM/YYYY HH:MM)."
      )
      return

    nombre_servicio = seleccion_servicio.split(" (RD$")[0]
    precio_servicio = self.servicios[nombre_servicio]

    cita = {
        "cliente": cliente,
        "barbero": barbero,
        "servicio": nombre_servicio,
        "precio_num": precio_servicio,
        "precio": f"RD$ {precio_servicio:,.2f}",
        "fecha_hora": fecha_hora,
    }
    self.citas.append(cita)
    self.actualizar_tabla()
    self.entry_cliente.delete(0, tk.END)
    messagebox.showinfo("Éxito", f"¡Cita reservada para {cliente}!")

  def actualizar_tabla(self):
    for item in self.tabla.get_children():
      self.tabla.delete(item)
    total = 0.0
    for c in self.citas:
      self.tabla.insert(
          "",
          tk.END,
          values=(
              c["cliente"],
              c["barbero"],
              c["servicio"],
              c["precio"],
              c["fecha_hora"],
          ),
      )
      total += c["precio_num"]
    self.lbl_ganancias.config(
        text=f"💰 Ganancias Totales Estimadas: RD$ {total:,.2f}"
    )

  def cancelar_cita(self):
    seleccion = self.tabla.selection()
    if not seleccion:
      messagebox.showwarning("Aviso", "Selecciona una cita para cancelar.")
      return
    if messagebox.askyesno("Confirmar", "¿Deseas eliminar esta cita?"):
      index = self.tabla.index(seleccion[0])
      self.citas.pop(index)
      self.actualizar_tabla()


def lanzar_app_principal():
  root_app = tk.Tk()
  BarberiaApp(root_app)
  root_app.mainloop()


if __name__ == "__main__":
  # Inicia primero la ventana de validación de suscripción
  root_val = tk.Tk()
  ValidadorSuscripcion(root_val)
  root_val.mainloop()