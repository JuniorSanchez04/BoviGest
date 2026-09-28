import tkinter as tk
from tkinter import ttk, messagebox

from controllers.inventario_controller import trasladar, obtener_animal, cargar_catalogos
from utils.fecha_helper import hoy

BG      = "#f4f6f9"
HDR     = "#e67e22"
TEXT    = "#2c3e50"
MUTED   = "#6b7a8d"
BTN_OK  = "#e67e22"


class TrasladoView(tk.Toplevel):
    """
    Formulario modal para registrar el traslado de un animal entre lotes.
    """

    def __init__(self, parent, id_animal: int, callback):
        super().__init__(parent)
        self.id_animal = id_animal
        self.callback  = callback
        self.animal    = obtener_animal(id_animal)

        catalogos = cargar_catalogos()
        self._lotes = {l['nombre']: l['id_lote'] for l in catalogos['lotes']}

        self.title("Traslado de Animal")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()

        self._construir_ui()
        self._centrar()

    def _construir_ui(self) -> None:
        tk.Frame(self, bg=HDR, height=6).pack(fill="x")
        tk.Label(self, text="↔  Traslado de Animal",
                 font=("Arial", 13, "bold"),
                 bg=BG, fg=HDR, pady=10).pack(fill="x", padx=20)

        # Datos del animal
        info = tk.LabelFrame(self, text="Animal seleccionado",
                              bg=BG, fg=MUTED, font=("Arial", 9),
                              padx=12, pady=8)
        info.pack(fill="x", padx=20, pady=(0, 10))

        a = self.animal
        for i, (lbl, val) in enumerate([
            ("Caravana",      a['caravana']),
            ("Categoría",     a['categoria']),
            ("Lote actual",   a['lote']),
        ]):
            tk.Label(info, text=f"{lbl}:", bg=BG, fg=MUTED,
                     font=("Arial", 9)).grid(row=i, column=0, sticky="w", pady=2)
            tk.Label(info, text=val, bg=BG, fg=TEXT,
                     font=("Arial", 10, "bold")).grid(
                row=i, column=1, sticky="w", padx=(8, 0), pady=2)

        # Formulario
        form = tk.Frame(self, bg=BG, padx=20)
        form.pack(fill="x")

        tk.Label(form, text="Lote de destino *", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=(6, 2))
        self.var_lote = tk.StringVar()
        ttk.Combobox(
            form, textvariable=self.var_lote,
            values=list(self._lotes), state="readonly", width=26,
        ).grid(row=0, column=1, sticky="ew", padx=(12, 0), pady=(6, 2), ipady=4)

        tk.Label(form, text="Fecha traslado *  (DD/MM/AAAA)", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=(6, 2))
        self.var_fecha = tk.StringVar(value=hoy())
        tk.Entry(form, textvariable=self.var_fecha, font=("Arial", 11),
                 width=18, relief="solid", bd=1).grid(
            row=1, column=1, sticky="w", padx=(12, 0), pady=(6, 2), ipady=4)

        tk.Label(form, text="Observaciones", bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=(6, 2))
        self.var_obs = tk.StringVar()
        tk.Entry(form, textvariable=self.var_obs, font=("Arial", 11),
                 width=28, relief="solid", bd=1).grid(
            row=2, column=1, sticky="ew", padx=(12, 0), pady=(6, 2), ipady=4)
        form.columnconfigure(1, weight=1)

        self.lbl_error = tk.Label(self, text="", font=("Arial", 9),
                                   bg=BG, fg="#c0392b", wraplength=320)
        self.lbl_error.pack(padx=20, pady=(4, 0))

        bframe = tk.Frame(self, bg=BG, pady=14)
        bframe.pack(fill="x", padx=20)
        tk.Button(bframe, text="Cancelar", font=("Arial", 10),
                  bg="#bdc3c7", fg="white", relief="flat",
                  cursor="hand2", width=10, command=self.destroy).pack(side="right", padx=(8, 0))
        tk.Button(bframe, text="Confirmar traslado", font=("Arial", 10, "bold"),
                  bg=BTN_OK, fg="white", relief="flat",
                  cursor="hand2", command=self._confirmar).pack(side="right")

    def _confirmar(self) -> None:
        self.lbl_error.config(text="")
        exito, error = trasladar(
            self.id_animal,
            self._lotes.get(self.var_lote.get()),
            self.animal['id_lote'],
            self.var_fecha.get(),
            self.var_obs.get(),
        )
        if exito:
            messagebox.showinfo("Traslado registrado",
                                "El traslado fue registrado correctamente.",
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