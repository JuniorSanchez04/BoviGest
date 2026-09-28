import tkinter as tk
from tkinter import messagebox

from controllers.produccion_controller import buscar_animal, registrar_pesaje
from utils.fecha_helper import hoy

BG      = "#f4f6f9"
HDR     = "#16213e"
TEXT    = "#2c3e50"
MUTED   = "#6b7a8d"
VERDE   = "#27ae60"
ROJO    = "#c0392b"
INFO_BG = "#eaf4fb"


class PesajeView(tk.Toplevel):
    """
    Formulario modal para registrar un pesaje individual.
    Patrón idéntico al de los formularios de sanidad:
    buscar animal → completar datos → guardar.
    """

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback   = callback
        self._id_animal = None

        self.title("Registrar Pesaje")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()

        self._construir_ui()
        self._centrar()

    def _construir_ui(self) -> None:
        tk.Frame(self, bg=HDR, height=6).pack(fill="x")
        tk.Label(self, text="⚖️  Registrar Pesaje",
                 font=("Arial", 13, "bold"),
                 bg=BG, fg=TEXT, pady=10).pack(fill="x", padx=20)

        # Sección animal
        sec_animal = tk.LabelFrame(self, text="Animal",
                                    bg=BG, fg=MUTED, font=("Arial", 9),
                                    padx=12, pady=10)
        sec_animal.pack(fill="x", padx=20, pady=(0, 8))

        fila = tk.Frame(sec_animal, bg=BG)
        fila.pack(fill="x")
        tk.Label(fila, text="Caravana:", bg=BG, fg=TEXT,
                 font=("Arial", 10)).pack(side="left")
        self.var_caravana = tk.StringVar()
        entry = tk.Entry(fila, textvariable=self.var_caravana,
                         font=("Arial", 11), width=18, relief="solid", bd=1)
        entry.pack(side="left", padx=(8, 8), ipady=4)
        entry.bind("<Return>", lambda _e: self._buscar_animal())
        entry.focus()
        tk.Button(fila, text="Buscar", font=("Arial", 10),
                  bg=MUTED, fg="white", relief="flat", cursor="hand2", padx=8,
                  command=self._buscar_animal).pack(side="left")

        self.lbl_info = tk.Label(sec_animal, text="",
                                  font=("Arial", 10, "bold"),
                                  bg=INFO_BG, fg=TEXT,
                                  anchor="w", padx=8, pady=6)
        self.lbl_info.pack(fill="x", pady=(8, 0))

        # Sección datos del pesaje
        sec_datos = tk.LabelFrame(self, text="Datos del pesaje",
                                   bg=BG, fg=MUTED, font=("Arial", 9),
                                   padx=12, pady=10)
        sec_datos.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(sec_datos, text="Fecha *  (DD/MM/AAAA)", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.var_fecha = tk.StringVar(value=hoy())
        tk.Entry(sec_datos, textvariable=self.var_fecha,
                 font=("Arial", 11), width=16,
                 relief="solid", bd=1).grid(row=0, column=1, sticky="w",
                                             padx=(12, 0), pady=(0, 8), ipady=4)

        tk.Label(sec_datos, text="Peso (kg) *", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=(0, 8))
        self.var_peso = tk.StringVar()
        tk.Entry(sec_datos, textvariable=self.var_peso,
                 font=("Arial", 14, "bold"), width=10,
                 relief="solid", bd=1, fg=TEXT).grid(row=1, column=1, sticky="w",
                                                      padx=(12, 0), pady=(0, 8), ipady=6)
        tk.Label(sec_datos, text="kg", bg=BG, fg=MUTED,
                 font=("Arial", 11)).grid(row=1, column=2, padx=(6, 0))

        tk.Label(sec_datos, text="Observaciones", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=(0, 6))
        self.var_obs = tk.StringVar()
        tk.Entry(sec_datos, textvariable=self.var_obs,
                 font=("Arial", 11), width=28,
                 relief="solid", bd=1).grid(row=2, column=1, sticky="ew",
                                             padx=(12, 0), pady=(0, 6), ipady=4)
        sec_datos.columnconfigure(1, weight=1)

        # Error y botones
        self.lbl_error = tk.Label(self, text="", font=("Arial", 9),
                                   bg=BG, fg=ROJO, wraplength=360)
        self.lbl_error.pack(padx=20, pady=(0, 4))

        bframe = tk.Frame(self, bg=BG, pady=12)
        bframe.pack(fill="x", padx=20)
        tk.Button(bframe, text="Cancelar", font=("Arial", 10),
                  bg="#bdc3c7", fg="white", relief="flat",
                  cursor="hand2", width=10,
                  command=self.destroy).pack(side="right", padx=(8, 0))
        tk.Button(bframe, text="Guardar", font=("Arial", 10, "bold"),
                  bg=VERDE, fg="white", relief="flat",
                  cursor="hand2", width=10,
                  command=self._guardar).pack(side="right")

    def _buscar_animal(self) -> None:
        animal, error = buscar_animal(self.var_caravana.get())
        if error:
            self.lbl_info.config(text=f"✗  {error}", fg=ROJO, bg="#fdecea")
            self._id_animal = None
        else:
            self._id_animal = animal['id_animal']
            self.lbl_info.config(
                text=f"✓  {animal['caravana']}  ·  {animal['categoria']}  "
                     f"·  {animal['sexo']}  ·  Lote: {animal['lote']}",
                fg=VERDE, bg=INFO_BG)

    def _guardar(self) -> None:
        self.lbl_error.config(text="")
        datos_form = {
            'id_animal':    self._id_animal,
            'fecha':        self.var_fecha.get(),
            'peso_kg':      self.var_peso.get(),
            'observaciones': self.var_obs.get(),
        }
        exito, error = registrar_pesaje(datos_form)
        if exito:
            messagebox.showinfo("Pesaje registrado",
                                "El pesaje fue guardado correctamente.",
                                parent=self)
            self.callback()
            self.destroy()
        else:
            self.lbl_error.config(text=error)

    def _centrar(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")