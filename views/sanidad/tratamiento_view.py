import tkinter as tk
from tkinter import ttk, messagebox

from controllers.sanidad_controller import (
    cargar_catalogos_sanidad, buscar_animal,
    calcular_fin_carencia, registrar_tratamiento,
)
from utils.fecha_helper import hoy

BG      = "#f4f6f9"
HDR     = "#16213e"
TEXT    = "#2c3e50"
MUTED   = "#6b7a8d"
VERDE   = "#27ae60"
ROJO    = "#c0392b"
INFO_BG = "#eaf4fb"


class TratamientoView(tk.Toplevel):
    """
    Formulario modal para registrar un tratamiento médico.
    Funcionalidad clave: al seleccionar el fármaco o cambiar la fecha
    de inicio, calcula automáticamente la fecha de fin de carencia.
    """

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback       = callback
        self._id_animal     = None   # se llena al buscar el animal

        catalogos = cargar_catalogos_sanidad()

        # Mapa: nombre → {id, dias_carencia, unidad}
        self._farmacos = {
            f['nombre']: {
                'id':           f['id_farmaco'],
                'dias_carencia': f['dias_carencia'],
                'unidad':       f['unidad_medida'] or '',
            }
            for f in catalogos['farmacos']
        }
        self._diagnosticos = {
            d['nombre']: d['id_diagnostico']
            for d in catalogos['diagnosticos']
        }

        self.title("Registrar Tratamiento")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()

        self._construir_ui()
        self._centrar()

    # ── UI ─────────────────────────────────────────────────────

    def _construir_ui(self) -> None:
        tk.Frame(self, bg=HDR, height=6).pack(fill="x")
        tk.Label(self, text="💊  Registrar Tratamiento",
                 font=("Arial", 13, "bold"),
                 bg=BG, fg=TEXT, pady=10).pack(fill="x", padx=20)

        self._seccion_busqueda_animal()
        self._seccion_datos_tratamiento()
        self._seccion_error_y_botones()

    def _seccion_busqueda_animal(self) -> None:
        """Sección superior: buscar animal por caravana."""
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

        # Label que muestra los datos del animal encontrado
        self.lbl_animal_info = tk.Label(sec, text="",
                                         font=("Arial", 10, "bold"),
                                         bg=INFO_BG, fg=TEXT,
                                         anchor="w", padx=8, pady=6,
                                         relief="flat")
        self.lbl_animal_info.pack(fill="x", pady=(8, 0))

    def _seccion_datos_tratamiento(self) -> None:
        """Sección central: campos del tratamiento."""
        sec = tk.LabelFrame(self, text="Datos del tratamiento",
                             bg=BG, fg=MUTED, font=("Arial", 9),
                             padx=12, pady=10)
        sec.pack(fill="x", padx=20, pady=(0, 8))

        # Fármaco
        tk.Label(sec, text="Fármaco *", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.var_farmaco = tk.StringVar()
        cmb_farmaco = ttk.Combobox(sec, textvariable=self.var_farmaco,
                                    values=list(self._farmacos),
                                    state="readonly", width=28, font=("Arial", 11))
        cmb_farmaco.grid(row=0, column=1, sticky="ew", padx=(12, 0),
                          pady=(0, 6), ipady=4)
        # Al seleccionar fármaco → recalcular carencia
        cmb_farmaco.bind("<<ComboboxSelected>>", self._recalcular_carencia)

        # Label de días de carencia (informativo)
        self.lbl_dias = tk.Label(sec, text="", font=("Arial", 8, "italic"),
                                  bg=BG, fg=MUTED)
        self.lbl_dias.grid(row=0, column=2, padx=(8, 0))

        # Diagnóstico (opcional)
        tk.Label(sec, text="Diagnóstico", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=(0, 6))
        self.var_diagnostico = tk.StringVar()
        ttk.Combobox(sec, textvariable=self.var_diagnostico,
                     values=[''] + list(self._diagnosticos),
                     state="readonly", width=28, font=("Arial", 11)
                     ).grid(row=1, column=1, sticky="ew", padx=(12, 0),
                             pady=(0, 6), ipady=4)

        # Fecha inicio
        tk.Label(sec, text="Fecha inicio *  (DD/MM/AAAA)", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=(0, 6))
        self.var_fecha_inicio = tk.StringVar(value=hoy())
        entry_inicio = tk.Entry(sec, textvariable=self.var_fecha_inicio,
                                font=("Arial", 11), width=18,
                                relief="solid", bd=1)
        entry_inicio.grid(row=2, column=1, sticky="w", padx=(12, 0),
                           pady=(0, 6), ipady=4)
        # Al salir del campo de fecha → recalcular carencia
        entry_inicio.bind("<FocusOut>", self._recalcular_carencia)

        # Dosis
        tk.Label(sec, text="Dosis", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=3, column=0, sticky="w", pady=(0, 6))
        self.var_dosis = tk.StringVar()
        tk.Entry(sec, textvariable=self.var_dosis,
                 font=("Arial", 11), width=12,
                 relief="solid", bd=1).grid(row=3, column=1, sticky="w",
                                             padx=(12, 0), pady=(0, 6), ipady=4)
        self.lbl_unidad = tk.Label(sec, text="", font=("Arial", 9),
                                    bg=BG, fg=MUTED)
        self.lbl_unidad.grid(row=3, column=2, padx=(8, 0))

        # Fecha fin de carencia (auto-calculada, editable)
        tk.Label(sec, text="Fin de carencia *  (DD/MM/AAAA)", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=4, column=0, sticky="w", pady=(0, 6))
        self.var_fecha_carencia = tk.StringVar()
        tk.Entry(sec, textvariable=self.var_fecha_carencia,
                 font=("Arial", 11, "bold"), width=18,
                 relief="solid", bd=1,
                 fg=ROJO).grid(row=4, column=1, sticky="w",
                                padx=(12, 0), pady=(0, 6), ipady=4)
        tk.Label(sec, text="← calculado automáticamente", font=("Arial", 8, "italic"),
                 bg=BG, fg=MUTED).grid(row=4, column=2, padx=(8, 0))

        # Observaciones
        tk.Label(sec, text="Observaciones", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=5, column=0, sticky="w", pady=(0, 6))
        self.var_obs = tk.StringVar()
        tk.Entry(sec, textvariable=self.var_obs,
                 font=("Arial", 11), width=30,
                 relief="solid", bd=1).grid(row=5, column=1, sticky="ew",
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

    def _recalcular_carencia(self, *_) -> None:
        """
        Se llama al cambiar el fármaco o la fecha de inicio.
        Auto-completa la fecha de fin de carencia.
        """
        nombre = self.var_farmaco.get()
        if nombre not in self._farmacos:
            return

        info = self._farmacos[nombre]
        dias = info['dias_carencia']

        # Actualizar label informativo de días y unidad
        self.lbl_dias.config(text=f"{dias} días de carencia")
        self.lbl_unidad.config(text=info['unidad'])

        # Calcular fecha fin de carencia
        nueva = calcular_fin_carencia(self.var_fecha_inicio.get(), dias)
        if nueva:
            self.var_fecha_carencia.set(nueva)

    def _guardar(self) -> None:
        self.lbl_error.config(text="")

        datos_form = {
            'id_animal':        self._id_animal,
            'id_farmaco':       self._farmacos.get(self.var_farmaco.get(), {}).get('id'),
            'id_diagnostico':   self._diagnosticos.get(self.var_diagnostico.get()),
            'fecha_inicio':     self.var_fecha_inicio.get(),
            'dosis':            self.var_dosis.get(),
            'fecha_fin_carencia': self.var_fecha_carencia.get(),
            'observaciones':    self.var_obs.get(),
        }

        exito, error = registrar_tratamiento(datos_form)
        if exito:
            messagebox.showinfo("Tratamiento registrado",
                                "El tratamiento fue guardado correctamente.",
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