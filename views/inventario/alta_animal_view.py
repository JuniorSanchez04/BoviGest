import tkinter as tk
from tkinter import ttk, messagebox

from controllers.inventario_controller import dar_alta, cargar_catalogos
from utils.fecha_helper import hoy

# ── Colores ────────────────────────────────────────────────────
BG      = "#f4f6f9"
HDR     = "#16213e"
TEXT    = "#2c3e50"
MUTED   = "#6b7a8d"
ACCENT  = "#1b6ca8"
BTN_OK  = "#27ae60"


class AltaAnimalView(tk.Toplevel):
    """
    Formulario modal para registrar un nuevo animal en el inventario.
    Se abre como ventana secundaria (Toplevel) bloqueando el padre.
    """

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback   # función a llamar al guardar exitosamente

        self.title("Alta de Animal")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()            # bloquea la interacción con la ventana padre

        # Catálogos y mapas nombre → id
        catalogos = cargar_catalogos()
        self._razas      = {r['nombre']: r['id_raza']      for r in catalogos['razas']}
        self._categorias = {c['nombre']: c['id_categoria']  for c in catalogos['categorias']}
        self._sexos      = {s['nombre']: s['id_sexo']       for s in catalogos['sexos']}
        self._lotes      = {l['nombre']: l['id_lote']       for l in catalogos['lotes']}

        self._construir_ui()
        self._centrar()

    # ── UI ─────────────────────────────────────────────────────

    def _construir_ui(self) -> None:
        # Encabezado
        tk.Frame(self, bg=HDR, height=6).pack(fill="x")
        tk.Label(
            self, text="Alta de Animal",
            font=("Arial", 13, "bold"),
            bg=BG, fg=TEXT, pady=12,
        ).pack(fill="x", padx=20)

        # Formulario
        form = tk.Frame(self, bg=BG, padx=24, pady=8)
        form.pack(fill="x")

        self.e_caravana  = self._campo(form, 0, "Caravana *")
        self.cmb_raza    = self._combo(form, 1, "Raza",
                                        [''] + list(self._razas))
        self.cmb_cat     = self._combo(form, 2, "Categoría *",
                                        list(self._categorias))
        self.cmb_sexo    = self._combo(form, 3, "Sexo *",
                                        list(self._sexos))
        self.e_fecha_nac = self._campo(form, 4, "Fecha nacimiento  (DD/MM/AAAA)")
        self.e_fecha_alta = self._campo(form, 5, "Fecha alta *  (DD/MM/AAAA)",
                                         valor_default=hoy())
        self.cmb_lote    = self._combo(form, 6, "Lote",
                                        [''] + list(self._lotes))
        self.e_obs       = self._campo(form, 7, "Observaciones")

        # Error
        self.lbl_error = tk.Label(
            self, text="", font=("Arial", 9),
            bg=BG, fg="#c0392b", wraplength=340,
        )
        self.lbl_error.pack(padx=24)

        # Botones
        bframe = tk.Frame(self, bg=BG, pady=14)
        bframe.pack(fill="x", padx=24)

        tk.Button(
            bframe, text="Cancelar",
            font=("Arial", 10), bg="#bdc3c7", fg="white",
            relief="flat", cursor="hand2", width=10, padx=6,
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            bframe, text="Guardar",
            font=("Arial", 10, "bold"), bg=BTN_OK, fg="white",
            relief="flat", cursor="hand2", width=10, padx=6,
            command=self._guardar,
        ).pack(side="right")

    def _campo(self, parent, fila, etiqueta, valor_default=''):
        tk.Label(parent, text=etiqueta, bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(
            row=fila, column=0, sticky="w", pady=(6, 2))
        var = tk.StringVar(value=valor_default)
        entry = tk.Entry(parent, textvariable=var,
                         font=("Arial", 11), width=30, relief="solid", bd=1)
        entry.grid(row=fila, column=1, sticky="ew", padx=(12, 0), pady=(6, 2), ipady=4)
        parent.columnconfigure(1, weight=1)
        return var   # retornamos la StringVar para leer el valor luego

    def _combo(self, parent, fila, etiqueta, opciones):
        tk.Label(parent, text=etiqueta, bg=BG, fg=MUTED,
                 font=("Arial", 9)).grid(
            row=fila, column=0, sticky="w", pady=(6, 2))
        var = tk.StringVar()
        cmb = ttk.Combobox(parent, textvariable=var,
                            values=opciones, state="readonly", width=28,
                            font=("Arial", 11))
        cmb.grid(row=fila, column=1, sticky="ew", padx=(12, 0), pady=(6, 2), ipady=4)
        return var   # retornamos la StringVar

    # ── Guardar ────────────────────────────────────────────────

    def _guardar(self) -> None:
        self.lbl_error.config(text="")

        datos_form = {
            'caravana':        self.e_caravana.get(),
            'id_raza':         self._razas.get(self.cmb_raza.get()),
            'id_categoria':    self._categorias.get(self.cmb_cat.get()),
            'id_sexo':         self._sexos.get(self.cmb_sexo.get()),
            'fecha_nacimiento': self.e_fecha_nac.get(),
            'fecha_alta':       self.e_fecha_alta.get(),
            'id_lote':         self._lotes.get(self.cmb_lote.get()),
            'observaciones':   self.e_obs.get(),
        }

        exito, error = dar_alta(datos_form)

        if exito:
            messagebox.showinfo("Éxito", "Animal registrado correctamente.",
                                parent=self)
            self.callback()   # recarga la tabla en inventario_view
            self.destroy()
        else:
            self.lbl_error.config(text=error)

    # ── Centrar ventana ────────────────────────────────────────

    def _centrar(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")