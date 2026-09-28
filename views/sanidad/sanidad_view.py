import tkinter as tk
from tkinter import ttk

from controllers.sanidad_controller import (
    resumen_alertas, alertas_carencia, alertas_proximas, alertas_vencidas,
    listar_tratamientos, listar_vacunaciones,
)
from core.session import tiene_permiso
from utils.fecha_helper import formatear

# ── Colores ────────────────────────────────────────────────────
BG        = "#f4f6f9"
HDR       = "#16213e"
HDR_TEXT  = "#e0e0e0"
TEXT      = "#2c3e50"
MUTED     = "#6b7a8d"
ACCENT    = "#1b6ca8"
VERDE     = "#27ae60"
NARANJA   = "#e67e22"
ROJO      = "#c0392b"
BTN_GREEN = "#27ae60"
BTN_BLUE  = "#1b6ca8"
BTN_GRAY  = "#7f8c8d"


class SanidadView(tk.Frame):
    """
    Vista principal del Módulo 3.
    Tres tabs: Alertas, Tratamientos, Vacunaciones.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)

        self.var_busq_trat = tk.StringVar()
        self.var_busq_vac  = tk.StringVar()

        self._construir_ui()
        self._cargar_todo()

    # ── Construcción ───────────────────────────────────────────

    def _construir_ui(self) -> None:
        self._construir_encabezado()
        self._construir_notebook()

    def _construir_encabezado(self) -> None:
        frame = tk.Frame(self, bg=HDR, padx=20, pady=14)
        frame.pack(fill="x")
        tk.Label(frame, text="💉  Sanidad, Vacunaciones y Cumplimiento",
                 font=("Arial", 15, "bold"), bg=HDR, fg=HDR_TEXT).pack(side="left")

    def _construir_notebook(self) -> None:
        # Estilo para los tabs del notebook
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[12, 6], font=("Arial", 10))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Alertas
        self.tab_alertas = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(self.tab_alertas, text="  🔔 Alertas  ")
        self._construir_tab_alertas()

        # Tab 2: Tratamientos
        self.tab_trat = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(self.tab_trat, text="  💊 Tratamientos  ")
        self._construir_tab_tratamientos()

        # Tab 3: Vacunaciones
        self.tab_vac = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(self.tab_vac, text="  💉 Vacunaciones  ")
        self._construir_tab_vacunaciones()

        # Recargar datos al cambiar de tab
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    # ── TAB 1: ALERTAS ─────────────────────────────────────────

    def _construir_tab_alertas(self) -> None:
        # Tarjetas de resumen
        self._construir_tarjetas(self.tab_alertas)

        # Sub-notebook con las tres tablas de alerta
        sub = ttk.Notebook(self.tab_alertas)
        sub.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Sub-tab carencia
        f_car = tk.Frame(sub, bg=BG)
        sub.add(f_car, text="  🔴 En carencia  ")
        self.tree_carencia = self._crear_treeview(f_car, [
            ('caravana',         'Caravana',        90),
            ('categoria',        'Categoría',        90),
            ('lote',             'Lote',            120),
            ('farmaco',          'Fármaco',         140),
            ('fecha_inicio',     'Inicio',           80),
            ('fecha_fin_carencia','Fin carencia',   100),
            ('dias_restantes',   'Días restantes',   90),
        ])
        self.tree_carencia.tag_configure('fila', background='#fdecea')

        # Sub-tab próximas
        f_prox = tk.Frame(sub, bg=BG)
        sub.add(f_prox, text="  🟡 Próximas (30d)  ")
        self.tree_proximas = self._crear_treeview(f_prox, [
            ('caravana',        'Caravana',    90),
            ('categoria',       'Categoría',   90),
            ('lote',            'Lote',       120),
            ('vacuna',          'Vacuna',     150),
            ('fecha_aplicacion','Aplicación',  90),
            ('proxima_fecha',   'Próxima',     90),
            ('dias_para_vencer','Días',         70),
        ])
        self.tree_proximas.tag_configure('fila', background='#fef9e7')

        # Sub-tab vencidas
        f_venc = tk.Frame(sub, bg=BG)
        sub.add(f_venc, text="  🔴 Vencidas  ")
        self.tree_vencidas = self._crear_treeview(f_venc, [
            ('caravana',        'Caravana',   90),
            ('categoria',       'Categoría',  90),
            ('lote',            'Lote',      120),
            ('vacuna',          'Vacuna',    150),
            ('fecha_aplicacion','Aplicación', 90),
            ('proxima_fecha',   'Venció',     90),
            ('dias_vencida',    'Días atrás', 80),
        ])
        self.tree_vencidas.tag_configure('fila', background='#fdecea')

    def _construir_tarjetas(self, parent) -> None:
        frame = tk.Frame(parent, bg=BG, pady=12)
        frame.pack(fill="x", padx=12)

        self.lbl_carencia = self._tarjeta(frame, "En carencia", "0", ROJO)
        self.lbl_proximas = self._tarjeta(frame, "Vacunaciones próximas", "0", NARANJA)
        self.lbl_vencidas = self._tarjeta(frame, "Vacunaciones vencidas", "0", ROJO)

    def _tarjeta(self, parent, titulo, valor, color):
        card = tk.Frame(parent, bg="white", relief="flat",
                        highlightbackground=color, highlightthickness=2)
        card.pack(side="left", padx=(0, 12), ipadx=14, ipady=10)

        lbl_val = tk.Label(card, text=valor,
                           font=("Arial", 28, "bold"), bg="white", fg=color)
        lbl_val.pack()
        tk.Label(card, text=titulo, font=("Arial", 9),
                 bg="white", fg=MUTED).pack()
        return lbl_val   # retornamos la label del número para actualizarla luego

    # ── TAB 2: TRATAMIENTOS ────────────────────────────────────

    def _construir_tab_tratamientos(self) -> None:
        # Barra de filtro
        bfiltro = tk.Frame(self.tab_trat, bg=BG, pady=10, padx=12)
        bfiltro.pack(fill="x")

        tk.Label(bfiltro, text="Caravana:", bg=BG, fg=TEXT,
                 font=("Arial", 10)).pack(side="left", padx=(0, 4))
        entry = tk.Entry(bfiltro, textvariable=self.var_busq_trat,
                         font=("Arial", 10), width=18)
        entry.pack(side="left", ipady=4)
        entry.bind("<Return>", lambda _e: self._cargar_tratamientos())

        tk.Button(bfiltro, text="🔍 Buscar", font=("Arial", 10),
                  bg=ACCENT, fg="white", relief="flat", cursor="hand2", padx=8,
                  command=self._cargar_tratamientos).pack(side="left", padx=(6, 0))

        tk.Button(bfiltro, text="✕ Limpiar", font=("Arial", 10),
                  bg=BTN_GRAY, fg="white", relief="flat", cursor="hand2", padx=8,
                  command=self._limpiar_busqueda_trat).pack(side="left", padx=(6, 0))

        # Tabla
        self.tree_trat = self._crear_treeview(self.tab_trat, [
            ('caravana',          'Caravana',      80),
            ('categoria',         'Categoría',     90),
            ('farmaco',           'Fármaco',      140),
            ('diagnostico',       'Diagnóstico',  140),
            ('fecha_inicio',      'Inicio',        80),
            ('fecha_fin_carencia','Fin carencia', 100),
            ('dias_restantes',    'Días',           60),
            ('dosis',             'Dosis',          70),
            ('registrado_por',    'Registrado por',130),
        ])
        self.tree_trat.tag_configure('en_carencia', background='#fdecea')
        self.tree_trat.tag_configure('finalizado',  background='#eafaf1')

        # Botones de acción
        bacciones = tk.Frame(self.tab_trat, bg=BG, pady=8, padx=12)
        bacciones.pack(fill="x")

        if tiene_permiso('sanidad.crear'):
            tk.Button(bacciones, text="＋ Nuevo tratamiento",
                      font=("Arial", 10, "bold"), bg=BTN_GREEN, fg="white",
                      relief="flat", cursor="hand2", padx=12, pady=6,
                      command=self._abrir_tratamiento).pack(side="left", padx=(0, 8))

        tk.Button(bacciones, text="↻ Actualizar",
                  font=("Arial", 10), bg=BTN_GRAY, fg="white",
                  relief="flat", cursor="hand2", padx=12, pady=6,
                  command=self._cargar_tratamientos).pack(side="right")

    # ── TAB 3: VACUNACIONES ────────────────────────────────────

    def _construir_tab_vacunaciones(self) -> None:
        bfiltro = tk.Frame(self.tab_vac, bg=BG, pady=10, padx=12)
        bfiltro.pack(fill="x")

        tk.Label(bfiltro, text="Caravana:", bg=BG, fg=TEXT,
                 font=("Arial", 10)).pack(side="left", padx=(0, 4))
        entry = tk.Entry(bfiltro, textvariable=self.var_busq_vac,
                         font=("Arial", 10), width=18)
        entry.pack(side="left", ipady=4)
        entry.bind("<Return>", lambda _e: self._cargar_vacunaciones())

        tk.Button(bfiltro, text="🔍 Buscar", font=("Arial", 10),
                  bg=ACCENT, fg="white", relief="flat", cursor="hand2", padx=8,
                  command=self._cargar_vacunaciones).pack(side="left", padx=(6, 0))

        tk.Button(bfiltro, text="✕ Limpiar", font=("Arial", 10),
                  bg=BTN_GRAY, fg="white", relief="flat", cursor="hand2", padx=8,
                  command=self._limpiar_busqueda_vac).pack(side="left", padx=(6, 0))

        self.tree_vac = self._crear_treeview(self.tab_vac, [
            ('caravana',         'Caravana',     80),
            ('categoria',        'Categoría',    90),
            ('vacuna',           'Vacuna',      150),
            ('fecha_aplicacion', 'Aplicación',   90),
            ('proxima_fecha',    'Próxima',       90),
            ('estado',           'Estado',       110),
            ('lote_vacuna',      'Lote vacuna',  90),
            ('registrado_por',   'Registrado por',130),
        ])
        self.tree_vac.tag_configure('al_dia',  background='#eafaf1')
        self.tree_vac.tag_configure('proxima', background='#fef9e7')
        self.tree_vac.tag_configure('vencida', background='#fdecea')
        self.tree_vac.tag_configure('unica',   background='#f0f0f0')

        bacciones = tk.Frame(self.tab_vac, bg=BG, pady=8, padx=12)
        bacciones.pack(fill="x")

        if tiene_permiso('sanidad.crear'):
            tk.Button(bacciones, text="＋ Nueva vacunación",
                      font=("Arial", 10, "bold"), bg=BTN_GREEN, fg="white",
                      relief="flat", cursor="hand2", padx=12, pady=6,
                      command=self._abrir_vacunacion).pack(side="left", padx=(0, 8))

        tk.Button(bacciones, text="↻ Actualizar",
                  font=("Arial", 10), bg=BTN_GRAY, fg="white",
                  relief="flat", cursor="hand2", padx=12, pady=6,
                  command=self._cargar_vacunaciones).pack(side="right")

    # ── Widget helper: Treeview con scrollbars ─────────────────

    def _crear_treeview(self, parent, columnas_config: list) -> ttk.Treeview:
        """
        Crea un Treeview con scrollbars dentro de un frame.
        columnas_config: lista de (id_col, titulo, ancho)
        """
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="both", expand=True, padx=8, pady=(0, 0))

        ids = [c[0] for c in columnas_config]
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
        self._cargar_alertas()
        self._cargar_tratamientos()
        self._cargar_vacunaciones()

    def _cargar_alertas(self) -> None:
        # Actualizar tarjetas
        resumen = resumen_alertas()
        self.lbl_carencia.config(text=str(resumen['en_carencia']))
        self.lbl_proximas.config(text=str(resumen['proximas']))
        self.lbl_vencidas.config(text=str(resumen['vencidas']))

        # Tabla en carencia
        self._limpiar_tree(self.tree_carencia)
        for fila in alertas_carencia():
            self.tree_carencia.insert('', 'end', tags=('fila',), values=(
                fila['caravana'],
                fila['categoria'],
                fila['lote'],
                fila['farmaco'],
                formatear(fila['fecha_inicio']),
                formatear(fila['fecha_fin_carencia']),
                f"{fila['dias_restantes']} días",
            ))

        # Tabla próximas
        self._limpiar_tree(self.tree_proximas)
        for fila in alertas_proximas():
            self.tree_proximas.insert('', 'end', tags=('fila',), values=(
                fila['caravana'],
                fila['categoria'],
                fila['lote'],
                fila['vacuna'],
                formatear(fila['fecha_aplicacion']),
                formatear(fila['proxima_fecha']),
                f"{fila['dias_para_vencer']} días",
            ))

        # Tabla vencidas
        self._limpiar_tree(self.tree_vencidas)
        for fila in alertas_vencidas():
            self.tree_vencidas.insert('', 'end', tags=('fila',), values=(
                fila['caravana'],
                fila['categoria'],
                fila['lote'],
                fila['vacuna'],
                formatear(fila['fecha_aplicacion']),
                formatear(fila['proxima_fecha']),
                f"{fila['dias_vencida']} días",
            ))

    def _cargar_tratamientos(self) -> None:
        self._limpiar_tree(self.tree_trat)
        for t in listar_tratamientos(self.var_busq_trat.get()):
            en_car = (t['dias_restantes'] is not None and t['dias_restantes'] >= 0)
            tag    = 'en_carencia' if en_car else 'finalizado'
            dosis  = f"{t['dosis']} {t['unidad_medida'] or ''}" if t['dosis'] else '—'
            self.tree_trat.insert('', 'end', tags=(tag,), values=(
                t['caravana'],
                t['categoria'],
                t['farmaco'],
                t['diagnostico'],
                formatear(t['fecha_inicio']),
                formatear(t['fecha_fin_carencia']),
                f"{t['dias_restantes']}d" if t['dias_restantes'] is not None else '—',
                dosis,
                t['registrado_por'],
            ))

    def _cargar_vacunaciones(self) -> None:
        self._limpiar_tree(self.tree_vac)
        for v in listar_vacunaciones(self.var_busq_vac.get()):
            dias = v['dias_estado']
            if v['proxima_fecha'] is None:
                tag, estado = 'unica', '— Dosis única'
            elif dias is not None and dias < 0:
                tag, estado = 'vencida', f'✗ Vencida ({abs(dias)}d)'
            elif dias is not None and dias <= 30:
                tag, estado = 'proxima', f'⚠ Próxima ({dias}d)'
            else:
                tag, estado = 'al_dia', '✓ Al día'

            self.tree_vac.insert('', 'end', tags=(tag,), values=(
                v['caravana'],
                v['categoria'],
                v['vacuna'],
                formatear(v['fecha_aplicacion']),
                formatear(v['proxima_fecha']) if v['proxima_fecha'] else '—',
                estado,
                v['lote_vacuna'] or '—',
                v['registrado_por'],
            ))

    # ── Helpers ────────────────────────────────────────────────

    def _limpiar_tree(self, tree: ttk.Treeview) -> None:
        for item in tree.get_children():
            tree.delete(item)

    def _limpiar_busqueda_trat(self) -> None:
        self.var_busq_trat.set('')
        self._cargar_tratamientos()

    def _limpiar_busqueda_vac(self) -> None:
        self.var_busq_vac.set('')
        self._cargar_vacunaciones()

    def _on_tab_changed(self, _event) -> None:
        """Recarga los datos del tab al que el usuario acaba de cambiar."""
        tab = self.notebook.index(self.notebook.select())
        if tab == 0:
            self._cargar_alertas()
        elif tab == 1:
            self._cargar_tratamientos()
        elif tab == 2:
            self._cargar_vacunaciones()

    # ── Abrir formularios ──────────────────────────────────────

    def _abrir_tratamiento(self) -> None:
        from views.sanidad.tratamiento_view import TratamientoView
        TratamientoView(self, callback=self._cargar_todo)

    def _abrir_vacunacion(self) -> None:
        from views.sanidad.vacunacion_view import VacunacionView
        VacunacionView(self, callback=self._cargar_todo)