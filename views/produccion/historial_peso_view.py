import tkinter as tk
from tkinter import ttk

from controllers.produccion_controller import historial_animal
from models.animal_model import obtener_animal
from utils.fecha_helper import formatear

BG     = "#f4f6f9"
HDR    = "#16213e"
TEXT   = "#2c3e50"
MUTED  = "#6b7a8d"
ACCENT = "#1b6ca8"

# Colores del gráfico
COLOR_LINEA  = "#1b6ca8"
COLOR_PUNTO  = "#1b6ca8"
COLOR_GRILLA = "#e8e8e8"
COLOR_EJE    = "#555555"


class HistorialPesoView(tk.Toplevel):
    """
    Ventana que muestra el historial completo de pesajes de un animal:
    - Tabla con fecha, peso y GMD de cada período.
    - Gráfico de línea dibujado con tkinter.Canvas.
    """

    def __init__(self, parent, id_animal: int):
        super().__init__(parent)
        self.animal  = obtener_animal(id_animal)
        self.pesajes = historial_animal(id_animal)

        self.title(
            f"Historial de peso — {self.animal['caravana']}  "
            f"·  {self.animal['categoria']}"
        )
        self.geometry("740x580")
        self.configure(bg=BG)
        self.grab_set()

        self._construir_ui()
        self._centrar()

    # ── UI ─────────────────────────────────────────────────────

    def _construir_ui(self) -> None:
        # Encabezado
        hdr = tk.Frame(self, bg=HDR, padx=16, pady=12)
        hdr.pack(fill="x")
        a = self.animal
        tk.Label(hdr,
                 text=f"📈  {a['caravana']}  ·  {a['categoria']}  ·  "
                      f"{a['raza']}  ·  Lote: {a['lote']}",
                 font=("Arial", 11, "bold"),
                 bg=HDR, fg="#e0e0e0").pack(side="left")

        # Tabla de pesajes
        self._construir_tabla()

        # Gráfico de línea
        self._construir_grafico()

        # Botón cerrar
        tk.Button(self, text="Cerrar", font=("Arial", 10),
                  bg=MUTED, fg="white", relief="flat",
                  cursor="hand2", padx=16, pady=6,
                  command=self.destroy).pack(pady=(6, 10))

    def _construir_tabla(self) -> None:
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="x", padx=12, pady=(10, 0))

        tree = ttk.Treeview(frame,
                             columns=('fecha', 'peso', 'anterior', 'gmd'),
                             show="headings", height=5, selectmode="none")

        for col, titulo, ancho in [
            ('fecha',    'Fecha',          90),
            ('peso',     'Peso (kg)',       90),
            ('anterior', 'Peso anterior',  100),
            ('gmd',      'GMD período',    100),
        ]:
            tree.heading(col, text=titulo)
            tree.column(col, width=ancho, anchor="center")

        tree.tag_configure('primero', background='#f0f4f8')

        for i, p in enumerate(self.pesajes):
            gmd_str = f"{p['gmd_periodo']:.3f} kg/día" if p['gmd_periodo'] else '— (primer pesaje)'
            ant_str = f"{p['peso_anterior']:.1f}" if p['peso_anterior'] else '—'
            tag     = 'primero' if i == 0 else ''
            tree.insert('', 'end', tags=(tag,), values=(
                formatear(p['fecha']),
                f"{p['peso_kg']:.1f}",
                ant_str,
                gmd_str,
            ))

        sy = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sy.set)
        tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        frame.columnconfigure(0, weight=1)

    def _construir_grafico(self) -> None:
        tk.Label(self, text="Evolución de peso",
                 font=("Arial", 10, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(10, 2))

        self.canvas = tk.Canvas(self, bg="white", width=700, height=220,
                                 highlightthickness=1,
                                 highlightbackground="#d0d0d0")
        self.canvas.pack(padx=20)
        self._dibujar_grafico()

    def _dibujar_grafico(self) -> None:
        C = self.canvas
        C.delete("all")

        if len(self.pesajes) < 2:
            C.create_text(350, 110,
                          text="Necesitás al menos 2 pesajes para mostrar el gráfico.",
                          font=("Arial", 10), fill=MUTED)
            return

        # ── Dimensiones ─────────────────────────────────────
        W, H  = 700, 220
        ML, MR, MT, MB = 60, 20, 20, 45
        pw = W - ML - MR   # ancho del área de ploteo
        ph = H - MT - MB   # alto del área de ploteo

        # ── Rango de pesos ───────────────────────────────────
        pesos   = [float(p['peso_kg']) for p in self.pesajes]
        ymin    = min(pesos)
        ymax    = max(pesos)
        rango   = ymax - ymin or 10
        ymin   -= rango * 0.12
        ymax   += rango * 0.12

        n = len(self.pesajes)

        def xp(i):     return ML + (i / (n - 1)) * pw
        def yp(peso):  return MT + ph - (peso - ymin) / (ymax - ymin) * ph

        # ── Grilla y etiquetas eje Y ─────────────────────────
        for pct in [0, 0.25, 0.5, 0.75, 1.0]:
            y   = MT + ph * (1 - pct)
            val = ymin + (ymax - ymin) * pct
            C.create_line(ML, y, ML + pw, y, fill=COLOR_GRILLA, dash=(3, 4))
            C.create_text(ML - 6, y, text=f"{val:.0f}",
                          font=("Arial", 8), fill=MUTED, anchor="e")

        # ── Ejes ─────────────────────────────────────────────
        C.create_line(ML, MT, ML, MT + ph,    fill=COLOR_EJE, width=2)
        C.create_line(ML, MT + ph, ML + pw, MT + ph, fill=COLOR_EJE, width=2)

        # Label eje Y
        C.create_text(16, MT + ph // 2, text="kg",
                      font=("Arial", 9, "bold"), fill=TEXT)

        # ── Línea de datos ───────────────────────────────────
        coords = []
        for i, p in enumerate(self.pesajes):
            coords.extend([xp(i), yp(float(p['peso_kg']))])
        C.create_line(coords, fill=COLOR_LINEA, width=2, smooth=False)

        # ── Puntos, etiquetas de peso y fechas ───────────────
        max_etiquetas = 12   # no mostrar todas si hay muchos puntos
        paso = max(1, n // max_etiquetas)

        for i, p in enumerate(self.pesajes):
            x = xp(i)
            y = yp(float(p['peso_kg']))

            # Punto (círculo)
            r = 4
            C.create_oval(x - r, y - r, x + r, y + r,
                          fill=COLOR_PUNTO, outline="white", width=2)

            if i % paso == 0 or i == n - 1:
                # Peso encima del punto
                C.create_text(x, y - 14,
                              text=f"{p['peso_kg']:.1f}",
                              font=("Arial", 8, "bold"), fill=TEXT)
                # Fecha debajo del eje X (solo DD/MM)
                fecha_str = formatear(p['fecha'])
                C.create_text(x, MT + ph + 14,
                              text=fecha_str[:5],
                              font=("Arial", 8), fill=MUTED)

        # Nota si hay puntos sin etiqueta
        if paso > 1:
            C.create_text(ML + pw - 4, MT + ph + 30,
                          text=f"({n} pesajes — mostrando cada {paso}°)",
                          font=("Arial", 7), fill=MUTED, anchor="e")

    def _centrar(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")