import tkinter as tk
from tkinter import ttk

from controllers.produccion_controller import (
    listar_gmd, gmd_por_lote, animales_sin_pesar,
)
from core.session import tiene_permiso
from utils.fecha_helper import formatear

# ── Colores ────────────────────────────────────────────────────
BG       = "#f4f6f9"
HDR      = "#16213e"
HDR_TEXT = "#e0e0e0"
TEXT     = "#2c3e50"
MUTED    = "#6b7a8d"
ACCENT   = "#1b6ca8"
VERDE    = "#27ae60"
NARANJA  = "#e67e22"
ROJO     = "#c0392b"
BTN_GREEN = "#27ae60"
BTN_BLUE  = "#1b6ca8"
BTN_GRAY  = "#7f8c8d"

# Umbrales de GMD para colorear filas (kg/día)
GMD_EXCELENTE = 0.900
GMD_BUENA     = 0.600


class ProduccionView(tk.Frame):
    """
    Vista principal del Módulo 4.
    Tres tabs: GMD por Animal, GMD por Lote, Sin Pesar.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)
        self._construir_ui()
        self._cargar_todo()

    # ── Construcción ───────────────────────────────────────────

    def _construir_ui(self) -> None:
        self._construir_encabezado()
        self._construir_notebook()

    def _construir_encabezado(self) -> None:
        frame = tk.Frame(self, bg=HDR, padx=20, pady=14)
        frame.pack(fill="x")
        tk.Label(frame, text="⚖️  Producción, Rendimiento y GMD",
                 font=("Arial", 15, "bold"),
                 bg=HDR, fg=HDR_TEXT).pack(side="left")
        self.lbl_resumen = tk.Label(frame, text="",
                                     font=("Arial", 10),
                                     bg=HDR, fg=MUTED)
        self.lbl_resumen.pack(side="right")

    def _construir_notebook(self) -> None:
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[12, 6], font=("Arial", 10))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: GMD por animal
        self.tab_gmd = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(self.tab_gmd, text="  ⚖️ GMD por Animal  ")
        self._construir_tab_gmd()

        # Tab 2: GMD por lote
        self.tab_lote = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(self.tab_lote, text="  📊 Por Lote  ")
        self._construir_tab_lote()

        # Tab 3: Sin pesar
        self.tab_sin_pesar = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(self.tab_sin_pesar, text="  ⚠ Sin Pesar  ")
        self._construir_tab_sin_pesar()

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    # ── Tab 1: GMD por animal ──────────────────────────────────

    def _construir_tab_gmd(self) -> None:
        # Leyenda de colores
        leyenda = tk.Frame(self.tab_gmd, bg=BG, pady=6, padx=12)
        leyenda.pack(fill="x")
        for color, texto in [
            ("#eafaf1", f"▪ Excelente (≥ {GMD_EXCELENTE} kg/día)"),
            ("#fef9e7", f"▪ Buena ({GMD_BUENA}–{GMD_EXCELENTE} kg/día)"),
            ("#fdecea", f"▪ Deficiente (< {GMD_BUENA} kg/día)"),
        ]:
            tk.Label(leyenda, text=texto, font=("Arial", 9),
                     bg=color, fg=TEXT, padx=8, pady=3,
                     relief="flat").pack(side="left", padx=(0, 8))

        # Tabla GMD
        self.tree_gmd = self._crear_treeview(self.tab_gmd, [
            ('caravana',          'Caravana',       80),
            ('categoria',         'Categoría',       90),
            ('lote',              'Lote',           120),
            ('peso_actual',       'Peso actual',     90),
            ('ultimo_pesaje',     'Último pesaje',   90),
            ('peso_anterior',     'Peso anterior',   90),
            ('dias_entre_pesajes','Días período',    80),
            ('gmd_kg_dia',        'GMD (kg/día)',    90),
        ])
        self.tree_gmd.tag_configure('excelente', background='#eafaf1')
        self.tree_gmd.tag_configure('buena',     background='#fef9e7')
        self.tree_gmd.tag_configure('deficiente',background='#fdecea')

        # Doble click → historial de pesajes
        self.tree_gmd.bind("<Double-1>", self._abrir_historial)

        # Botones
        bframe = tk.Frame(self.tab_gmd, bg=BG, pady=8, padx=12)
        bframe.pack(fill="x")
        if tiene_permiso('produccion.crear'):
            tk.Button(bframe, text="＋ Pesaje individual",
                      font=("Arial", 10, "bold"), bg=BTN_GREEN, fg="white",
                      relief="flat", cursor="hand2", padx=12, pady=6,
                      command=self._abrir_pesaje_individual).pack(side="left", padx=(0, 8))
            tk.Button(bframe, text="＋ Pesaje masivo",
                      font=("Arial", 10, "bold"), bg=BTN_BLUE, fg="white",
                      relief="flat", cursor="hand2", padx=12, pady=6,
                      command=self._abrir_pesaje_masivo).pack(side="left", padx=(0, 8))
        tk.Button(bframe, text="📋 Ver historial",
                  font=("Arial", 10), bg=BTN_GRAY, fg="white",
                  relief="flat", cursor="hand2", padx=12, pady=6,
                  command=self._abrir_historial).pack(side="left")
        tk.Button(bframe, text="↻ Actualizar",
                  font=("Arial", 10), bg=BTN_GRAY, fg="white",
                  relief="flat", cursor="hand2", padx=12, pady=6,
                  command=self._cargar_gmd).pack(side="right")

    # ── Tab 2: GMD por lote ────────────────────────────────────

    def _construir_tab_lote(self) -> None:
        self.tree_lote = self._crear_treeview(self.tab_lote, [
            ('lote',            'Lote',              160),
            ('animales_con_gmd','Animales con GMD',  130),
            ('gmd_promedio',    'GMD Promedio',      120),
            ('gmd_minima',      'GMD Mínima',        110),
            ('gmd_maxima',      'GMD Máxima',        110),
        ])
        self.tree_lote.tag_configure('fila_par',   background='#f9f9f9')
        self.tree_lote.tag_configure('fila_impar', background='white')

        bframe = tk.Frame(self.tab_lote, bg=BG, pady=8, padx=12)
        bframe.pack(fill="x")
        tk.Button(bframe, text="↻ Actualizar",
                  font=("Arial", 10), bg=BTN_GRAY, fg="white",
                  relief="flat", cursor="hand2", padx=12, pady=6,
                  command=self._cargar_lote).pack(side="right")

    # ── Tab 3: Sin pesar ───────────────────────────────────────

    def _construir_tab_sin_pesar(self) -> None:
        # Selector de umbral de días
        ctrl = tk.Frame(self.tab_sin_pesar, bg=BG, pady=8, padx=12)
        ctrl.pack(fill="x")
        tk.Label(ctrl, text="Mostrar animales sin pesar en más de:",
                 bg=BG, fg=TEXT, font=("Arial", 10)).pack(side="left")
        self.var_dias = tk.StringVar(value="30")
        tk.Entry(ctrl, textvariable=self.var_dias,
                 font=("Arial", 10), width=5).pack(side="left", padx=(8, 4))
        tk.Label(ctrl, text="días", bg=BG, fg=TEXT,
                 font=("Arial", 10)).pack(side="left")
        tk.Button(ctrl, text="🔍 Filtrar", font=("Arial", 10),
                  bg=ACCENT, fg="white", relief="flat", cursor="hand2", padx=8,
                  command=self._cargar_sin_pesar).pack(side="left", padx=(10, 0))

        self.tree_sin_pesar = self._crear_treeview(self.tab_sin_pesar, [
            ('caravana',     'Caravana',      90),
            ('categoria',    'Categoría',     90),
            ('lote',         'Lote',         130),
            ('ultimo_pesaje','Último pesaje', 110),
            ('dias_sin_pesar','Días sin pesar',100),
        ])
        self.tree_sin_pesar.tag_configure('nunca', background='#fdecea')
        self.tree_sin_pesar.tag_configure('atrasado', background='#fef9e7')

        bframe = tk.Frame(self.tab_sin_pesar, bg=BG, pady=8, padx=12)
        bframe.pack(fill="x")
        tk.Button(bframe, text="↻ Actualizar",
                  font=("Arial", 10), bg=BTN_GRAY, fg="white",
                  relief="flat", cursor="hand2", padx=12, pady=6,
                  command=self._cargar_sin_pesar).pack(side="right")

    # ── Widget helper ──────────────────────────────────────────

    def _crear_treeview(self, parent, columnas_config: list) -> ttk.Treeview:
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="both", expand=True, padx=8, pady=(0, 0))
        ids  = [c[0] for c in columnas_config]
        tree = ttk.Treeview(frame, columns=ids,
                             show="headings", selectmode="browse")
        for col_id, titulo, ancho in columnas_config:
            tree.heading(col_id, text=titulo)
            tree.column(col_id, width=ancho, anchor="center", minwidth=50)
        sy = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
        sx = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return tree

    # ── Carga de datos ─────────────────────────────────────────

    def _cargar_todo(self) -> None:
        self._cargar_gmd()
        self._cargar_lote()
        self._cargar_sin_pesar()

    def _cargar_gmd(self) -> None:
        datos = listar_gmd()
        for item in self.tree_gmd.get_children():
            self.tree_gmd.delete(item)

        for a in datos:
            gmd = float(a['gmd_kg_dia']) if a['gmd_kg_dia'] else 0
            if gmd >= GMD_EXCELENTE:
                tag = 'excelente'
            elif gmd >= GMD_BUENA:
                tag = 'buena'
            else:
                tag = 'deficiente'

            self.tree_gmd.insert('', 'end',
                iid=str(a['id_animal']),
                tags=(tag,),
                values=(
                    a['caravana'],
                    a['categoria'],
                    a['lote'],
                    f"{a['peso_actual']:.1f} kg",
                    formatear(a['ultimo_pesaje']),
                    f"{a['peso_anterior']:.1f} kg",
                    f"{a['dias_entre_pesajes']}d",
                    f"{a['gmd_kg_dia']:.3f}",
                ),
            )

        n = len(datos)
        if n > 0:
            gmd_vals = [float(a['gmd_kg_dia']) for a in datos if a['gmd_kg_dia']]
            prom = sum(gmd_vals) / len(gmd_vals) if gmd_vals else 0
            self.lbl_resumen.config(
                text=f"{n} animales  ·  GMD promedio: {prom:.3f} kg/día"
            )

    def _cargar_lote(self) -> None:
        datos = gmd_por_lote()
        for item in self.tree_lote.get_children():
            self.tree_lote.delete(item)
        for i, fila in enumerate(datos):
            tag = 'fila_par' if i % 2 == 0 else 'fila_impar'
            self.tree_lote.insert('', 'end', tags=(tag,), values=(
                fila['lote'],
                fila['animales_con_gmd'],
                f"{fila['gmd_promedio']:.3f}",
                f"{fila['gmd_minima']:.3f}",
                f"{fila['gmd_maxima']:.3f}",
            ))

    def _cargar_sin_pesar(self) -> None:
        try:
            dias = int(self.var_dias.get())
        except ValueError:
            dias = 30
        datos = animales_sin_pesar(dias)
        for item in self.tree_sin_pesar.get_children():
            self.tree_sin_pesar.delete(item)
        for a in datos:
            nunca = a['ultimo_pesaje'] is None
            tag   = 'nunca' if nunca else 'atrasado'
            self.tree_sin_pesar.insert('', 'end',
                iid=str(a['id_animal']),
                tags=(tag,),
                values=(
                    a['caravana'],
                    a['categoria'],
                    a['lote'],
                    formatear(a['ultimo_pesaje']) if a['ultimo_pesaje'] else '— Nunca pesado',
                    f"{a['dias_sin_pesar']}d" if a['dias_sin_pesar'] is not None else '—',
                ),
            )

    def _on_tab_changed(self, _event) -> None:
        tab = self.notebook.index(self.notebook.select())
        if tab == 0:   self._cargar_gmd()
        elif tab == 1: self._cargar_lote()
        elif tab == 2: self._cargar_sin_pesar()

    # ── Navegación ─────────────────────────────────────────────

    def _id_seleccionado(self) -> int | None:
        sel = self.tree_gmd.selection()
        return int(sel[0]) if sel else None

    def _abrir_pesaje_individual(self) -> None:
        from views.produccion.pesaje_view import PesajeView
        PesajeView(self, callback=self._cargar_todo)

    def _abrir_pesaje_masivo(self) -> None:
        from views.produccion.pesaje_masivo_view import PesajeMasivoView
        PesajeMasivoView(self, callback=self._cargar_todo)

    def _abrir_historial(self, _event=None) -> None:
        id_animal = self._id_seleccionado()
        if not id_animal:
            return
        from views.produccion.historial_peso_view import HistorialPesoView
        HistorialPesoView(self, id_animal=id_animal)