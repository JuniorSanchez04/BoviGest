import tkinter as tk
from tkinter import ttk, messagebox

from controllers.sanidad_controller import (
    cargar_catalogos_sanidad, buscar_animal,
    calcular_proxima_vacunacion, registrar_vacunacion,
)
from utils.fecha_helper import hoy

BG      = "#f4f6f9"
HDR     = "#16213e"
TEXT    = "#2c3e50"
MUTED   = "#6b7a8d"
VERDE   = "#27ae60"
ROJO    = "#c0392b"
INFO_BG = "#eaf4fb"


class VacunacionView(tk.Toplevel):
    """
    Formulario modal para registrar una vacunación.
    Al seleccionar la vacuna o cambiar la fecha de aplicación,
    calcula automáticamente la próxima fecha de revacunación.
    """

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback   = callback
        self._id_animal = None

        catalogos = cargar_catalogos_sanidad()

        # Mapa: nombre → {id, intervalo_revacunacion}
        self._vacunas = {
            v['nombre']: {
                'id':        v['id_vacuna'],
                'intervalo': v['intervalo_revacunacion'],
            }
            for v in catalogos['vacunas']
        }

        self.title("Registrar Vacunación")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()

        self._construir_ui()
        self._centrar()

    # ── UI ─────────────────────────────────────────────────────

    def _construir_ui(self) -> None:
        tk.Frame(self, bg=HDR, height=6).pack(fill="x")
        tk.Label(self, text="💉  Registrar Vacunación",
                 font=("Arial", 13, "bold"),
                 bg=BG, fg=TEXT, pady=10).pack(fill="x", padx=20)

        self._seccion_busqueda_animal()
        self._seccion_datos_vacunacion()
        self._seccion_error_y_botones()

    def _seccion_busqueda_animal(self) -> None:
        sec = tk.LabelFrame(self, text="Animal",
                             bg=BG, fg=MUTED, font=("Arial", 9),
                             padx=12, pady=10)
        sec.pack(fill="x", padx=20, pady=(0, 8))

        fila = tk.Frame(sec, bg=BG)
        fila.pack(fill="x")

        tk.Label(fila, text="Caravana:", bg=BG, fg=TEXT,
                 font=("Arial", 10)).pack(side="left")
        self.var_caravana = tk.StringVar()
        entry = tk.Entry(fila, textvariable=self.var_caravana,
                         font=("Arial", 11), width=18,
                         relief="solid", bd=1)
        entry.pack(side="left", padx=(8, 8), ipady=4)
        entry.bind("<Return>", lambda _e: self._buscar_animal())
        entry.focus()

        tk.Button(fila, text="Buscar", font=("Arial", 10),
                  bg=MUTED, fg="white", relief="flat",
                  cursor="hand2", padx=8,
                  command=self._buscar_animal).pack(side="left")

        self.lbl_animal_info = tk.Label(sec, text="",
                                         font=("Arial", 10, "bold"),
                                         bg=INFO_BG, fg=TEXT,
                                         anchor="w", padx=8, pady=6)
        self.lbl_animal_info.pack(fill="x", pady=(8, 0))

    def _seccion_datos_vacunacion(self) -> None:
        sec = tk.LabelFrame(self, text="Datos de la vacunación",
                             bg=BG, fg=MUTED, font=("Arial", 9),
                             padx=12, pady=10)
        sec.pack(fill="x", padx=20, pady=(0, 8))

        # Vacuna
        tk.Label(sec, text="Vacuna *", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.var_vacuna = tk.StringVar()
        cmb_vacuna = ttk.Combobox(sec, textvariable=self.var_vacuna,
                                   values=list(self._vacunas),
                                   state="readonly", width=28, font=("Arial", 11))
        cmb_vacuna.grid(row=0, column=1, sticky="ew", padx=(12, 0),
                         pady=(0, 6), ipady=4)
        cmb_vacuna.bind("<<ComboboxSelected>>", self._recalcular_proxima)

        # Info del intervalo (informativa)
        self.lbl_intervalo = tk.Label(sec, text="", font=("Arial", 8, "italic"),
                                       bg=BG, fg=MUTED)
        self.lbl_intervalo.grid(row=0, column=2, padx=(8, 0))

        # Fecha aplicación
        tk.Label(sec, text="Fecha aplicación *  (DD/MM/AAAA)", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=(0, 6))
        self.var_fecha_aplicacion = tk.StringVar(value=hoy())
        entry_fecha = tk.Entry(sec, textvariable=self.var_fecha_aplicacion,
                               font=("Arial", 11), width=18,
                               relief="solid", bd=1)
        entry_fecha.grid(row=1, column=1, sticky="w", padx=(12, 0),
                          pady=(0, 6), ipady=4)
        entry_fecha.bind("<FocusOut>", self._recalcular_proxima)

        # Lote de vacuna (número de lote del producto)
        tk.Label(sec, text="Lote de vacuna", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=(0, 6))
        self.var_lote_vacuna = tk.StringVar()
        tk.Entry(sec, textvariable=self.var_lote_vacuna,
                 font=("Arial", 11), width=20,
                 relief="solid", bd=1).grid(row=2, column=1, sticky="w",
                                             padx=(12, 0), pady=(0, 6), ipady=4)

        # Próxima fecha (auto-calculada, editable)
        tk.Label(sec, text="Próxima vacunación  (DD/MM/AAAA)", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=3, column=0, sticky="w", pady=(0, 6))
        self.var_proxima = tk.StringVar()
        tk.Entry(sec, textvariable=self.var_proxima,
                 font=("Arial", 11, "bold"), width=18,
                 relief="solid", bd=1,
                 fg=VERDE).grid(row=3, column=1, sticky="w",
                                 padx=(12, 0), pady=(0, 6), ipady=4)
        tk.Label(sec, text="← calculado automáticamente", font=("Arial", 8, "italic"),
                 bg=BG, fg=MUTED).grid(row=3, column=2, padx=(8, 0))

        # Observaciones
        tk.Label(sec, text="Observaciones", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=4, column=0, sticky="w", pady=(0, 6))
        self.var_obs = tk.StringVar()
        tk.Entry(sec, textvariable=self.var_obs,
                 font=("Arial", 11), width=30,
                 relief="solid", bd=1).grid(row=4, column=1, sticky="ew",
                                             padx=(12, 0), pady=(0, 6), ipady=4)
        sec.columnconfigure(1, weight=1)

    def _seccion_error_y_botones(self) -> None:
        self.lbl_error = tk.Label(self, text="", font=("Arial", 9),
                                   bg=BG, fg=ROJO, wraplength=380)
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

    # ── Lógica ─────────────────────────────────────────────────

    def _buscar_animal(self) -> None:
        animal, error = buscar_animal(self.var_caravana.get())
        if error:
            self.lbl_animal_info.config(
                text=f"✗  {error}", fg=ROJO, bg="#fdecea")
            self._id_animal = None
        else:
            self._id_animal = animal['id_animal']
            self.lbl_animal_info.config(
                text=f"✓  {animal['caravana']}  ·  {animal['categoria']}  "
                     f"·  {animal['sexo']}  ·  Lote: {animal['lote']}",
                fg=VERDE, bg=INFO_BG)

    def _recalcular_proxima(self, *_) -> None:
        """
        Se llama al cambiar la vacuna o la fecha de aplicación.
        Auto-completa la próxima fecha de vacunación.
        """
        nombre = self.var_vacuna.get()
        if nombre not in self._vacunas:
            return

        intervalo = self._vacunas[nombre]['intervalo']

        if intervalo is None:
            # Vacuna de dosis única (ej: Brucelosis)
            self.lbl_intervalo.config(text="Dosis única — sin revacunación")
            self.var_proxima.set("N/A (dosis única)")
            return

        self.lbl_intervalo.config(text=f"Revacunar cada {intervalo} días")

        nueva = calcular_proxima_vacunacion(
            self.var_fecha_aplicacion.get(), intervalo
        )
        if nueva:
            self.var_proxima.set(nueva)

    def _guardar(self) -> None:
        self.lbl_error.config(text="")

        datos_form = {
            'id_animal':       self._id_animal,
            'id_vacuna':       self._vacunas.get(self.var_vacuna.get(), {}).get('id'),
            'fecha_aplicacion': self.var_fecha_aplicacion.get(),
            'lote_vacuna':     self.var_lote_vacuna.get(),
            'proxima_fecha':   self.var_proxima.get(),
            'observaciones':   self.var_obs.get(),
        }

        exito, error = registrar_vacunacion(datos_form)
        if exito:
            messagebox.showinfo("Vacunación registrada",
                                "La vacunación fue guardada correctamente.",
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