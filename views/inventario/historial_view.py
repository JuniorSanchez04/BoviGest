import tkinter as tk
from tkinter import ttk

from controllers.inventario_controller import historial, obtener_animal
from utils.fecha_helper import formatear

BG    = "#f4f6f9"
HDR   = "#16213e"
TEXT  = "#2c3e50"
MUTED = "#6b7a8d"


class HistorialView(tk.Toplevel):
    """
    Ventana de solo lectura que muestra todos los movimientos
    (ALTA, BAJA, TRASLADO) de un animal específico.
    """

    def __init__(self, parent, id_animal: int):
        super().__init__(parent)
        self.animal = obtener_animal(id_animal)

        self.title(f"Historial — Caravana {self.animal['caravana']}")
        self.geometry("820x420")
        self.configure(bg=BG)
        self.grab_set()

        self._construir_ui()
        self._cargar_movimientos(id_animal)
        self._centrar()

    def _construir_ui(self) -> None:
        # Encabezado con datos del animal
        hdr = tk.Frame(self, bg=HDR, padx=16, pady=12)
        hdr.pack(fill="x")

        a = self.animal
        tk.Label(hdr,
                 text=f"📋  Historial de movimientos  ·  {a['caravana']}  "
                      f"·  {a['categoria']}  ·  {a['raza']}",
                 font=("Arial", 11, "bold"),
                 bg=HDR, fg="#e0e0e0").pack(side="left")

        # Tabla de movimientos
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=12, pady=10)

        columnas = ('tipo', 'fecha', 'lote_origen',
                    'lote_destino', 'motivo', 'registrado_por', 'observaciones')

        self.tree = ttk.Treeview(frame, columns=columnas,
                                  show="headings", selectmode="none")

        config = [
            ('tipo',          'Tipo',          90),
            ('fecha',         'Fecha',         90),
            ('lote_origen',   'Lote origen',  120),
            ('lote_destino',  'Lote destino', 120),
            ('motivo',        'Motivo baja',  120),
            ('registrado_por','Registrado por',140),
            ('observaciones', 'Observaciones',160),
        ]
        for col, titulo, ancho in config:
            self.tree.heading(col, text=titulo)
            self.tree.column(col, width=ancho, anchor="center")

        self.tree.tag_configure('ALTA',     background="#eafaf1")
        self.tree.tag_configure('BAJA',     background="#fdecea")
        self.tree.tag_configure('TRASLADO', background="#fef9e7")

        scroll_y = ttk.Scrollbar(frame, orient="vertical",
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        # Botón cerrar
        tk.Button(self, text="Cerrar", font=("Arial", 10),
                  bg="#7f8c8d", fg="white", relief="flat",
                  cursor="hand2", padx=16, pady=6,
                  command=self.destroy).pack(pady=(0, 10))

    def _cargar_movimientos(self, id_animal: int) -> None:
        movimientos = historial(id_animal)
        for i, m in enumerate(movimientos):
            tipo = m['tipo']
            self.tree.insert(
                '', 'end',
                values=(
                    tipo,
                    formatear(m['fecha']),
                    m['lote_origen']   or '—',
                    m['lote_destino']  or '—',
                    m['motivo_baja']   or '—',
                    m['registrado_por'],
                    m['observaciones'] or '',
                ),
                tags=(tipo,),
            )

    def _centrar(self) -> None:
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")