import tkinter as tk
from tkinter import ttk, messagebox

from controllers.inventario_controller import listar, resumen, cargar_catalogos
from core.session import tiene_permiso
from utils.fecha_helper import formatear

# ── Colores ────────────────────────────────────────────────────
BG          = "#f4f6f9"
HDR         = "#16213e"
HDR_TEXT    = "#e0e0e0"
ACCENT      = "#1b6ca8"
TEXT        = "#2c3e50"
MUTED       = "#6b7a8d"
ROW_PAR     = "#ffffff"
ROW_IMPAR   = "#f0f4f8"
BTN_GREEN   = "#27ae60"
BTN_RED     = "#c0392b"
BTN_ORANGE  = "#e67e22"
BTN_BLUE    = "#1b6ca8"
BTN_GRAY    = "#7f8c8d"


class InventarioView(tk.Frame):
    """
    Vista principal del Módulo 2.
    Se monta dentro del área de contenido del dashboard.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.pack(fill="both", expand=True)

        # Variables de filtro ligadas a los widgets
        self.var_busqueda   = tk.StringVar()
        self.var_lote       = tk.StringVar()
        self.var_categoria  = tk.StringVar()
        self.var_solo_activos = tk.BooleanVar(value=True)

        # Mapas nombre → id para los comboboxes de filtro
        self._mapa_lotes      = {}
        self._mapa_categorias = {}

        self._construir_ui()
        self.cargar_animales()

    # ── Construcción de la UI ──────────────────────────────────

    def _construir_ui(self) -> None:
        self._construir_encabezado()
        self._construir_filtros()
        self._construir_tabla()
        self._construir_barra_acciones()

    def _construir_encabezado(self) -> None:
        frame = tk.Frame(self, bg=HDR, padx=20, pady=14)
        frame.pack(fill="x")

        tk.Label(
            frame, text="🐮  Padrón de Inventario",
            font=("Arial", 15, "bold"),
            bg=HDR, fg=HDR_TEXT,
        ).pack(side="left")

        self.lbl_total = tk.Label(
            frame, text="",
            font=("Arial", 10),
            bg=HDR, fg=MUTED,
        )
        self.lbl_total.pack(side="right")

    def _construir_filtros(self) -> None:
        frame = tk.Frame(self, bg=BG, pady=10, padx=16)
        frame.pack(fill="x")

        # Carga catálogos para los comboboxes de filtro
        catalogos = cargar_catalogos()

        lotes = catalogos['lotes']
        self._mapa_lotes = {l['nombre']: l['id_lote'] for l in lotes}
        nombres_lotes = ['Todos los lotes'] + [l['nombre'] for l in lotes]

        cats = catalogos['categorias']
        self._mapa_categorias = {c['nombre']: c['id_categoria'] for c in cats}
        nombres_cats = ['Todas las categorías'] + [c['nombre'] for c in cats]

        # Campo de búsqueda
        tk.Label(frame, text="Buscar:", bg=BG, fg=TEXT,
                 font=("Arial", 10)).grid(row=0, column=0, padx=(0, 4))
        entry = tk.Entry(frame, textvariable=self.var_busqueda,
                         font=("Arial", 10), width=18)
        entry.grid(row=0, column=1, padx=(0, 12), ipady=4)
        entry.bind("<Return>", lambda _e: self.cargar_animales())

        # Combobox lote
        tk.Label(frame, text="Lote:", bg=BG, fg=TEXT,
                 font=("Arial", 10)).grid(row=0, column=2, padx=(0, 4))
        self.cmb_lote = ttk.Combobox(
            frame, textvariable=self.var_lote,
            values=nombres_lotes, state="readonly", width=16,
        )
        self.cmb_lote.current(0)
        self.cmb_lote.grid(row=0, column=3, padx=(0, 12))

        # Combobox categoría
        tk.Label(frame, text="Categoría:", bg=BG, fg=TEXT,
                 font=("Arial", 10)).grid(row=0, column=4, padx=(0, 4))
        self.cmb_categoria = ttk.Combobox(
            frame, textvariable=self.var_categoria,
            values=nombres_cats, state="readonly", width=18,
        )
        self.cmb_categoria.current(0)
        self.cmb_categoria.grid(row=0, column=5, padx=(0, 12))

        # Checkbox solo activos
        tk.Checkbutton(
            frame, text="Solo activos",
            variable=self.var_solo_activos,
            bg=BG, fg=TEXT, font=("Arial", 10),
            command=self.cargar_animales,
        ).grid(row=0, column=6, padx=(0, 12))

        # Botón filtrar
        tk.Button(
            frame, text="🔍 Filtrar",
            font=("Arial", 10), bg=ACCENT, fg="white",
            relief="flat", cursor="hand2", padx=10,
            command=self.cargar_animales,
        ).grid(row=0, column=7)

    def _construir_tabla(self) -> None:
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        columnas = ('caravana', 'raza', 'categoria', 'sexo',
                    'lote', 'fecha_alta', 'estado')

        self.tree = ttk.Treeview(
            frame,
            columns=columnas,
            show="headings",
            selectmode="browse",   # solo una fila a la vez
        )

        # Encabezados y anchos
        config_cols = [
            ('caravana',   'Caravana',    100),
            ('raza',       'Raza',        110),
            ('categoria',  'Categoría',   110),
            ('sexo',       'Sexo',         70),
            ('lote',       'Lote',        130),
            ('fecha_alta', 'Fecha Alta',   90),
            ('estado',     'Estado',       70),
        ]
        for col, titulo, ancho in config_cols:
            self.tree.heading(col, text=titulo)
            self.tree.column(col, width=ancho, anchor="center")

        # Colores de filas alternadas
        self.tree.tag_configure('par',   background=ROW_PAR)
        self.tree.tag_configure('impar', background=ROW_IMPAR)
        self.tree.tag_configure('baja',  background='#fdecea', foreground='#c0392b')

        # Scrollbars
        scroll_y = ttk.Scrollbar(frame, orient="vertical",
                                  command=self.tree.yview)
        scroll_x = ttk.Scrollbar(frame, orient="horizontal",
                                  command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set,
                            xscrollcommand=scroll_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        # Evento de selección → habilita/deshabilita botones
        self.tree.bind("<<TreeviewSelect>>", self._on_seleccion)
        # Doble click → ver historial
        self.tree.bind("<Double-1>", lambda _e: self._abrir_historial())

    def _construir_barra_acciones(self) -> None:
        frame = tk.Frame(self, bg=BG, pady=10, padx=16)
        frame.pack(fill="x")

        # Botón Alta (solo si tiene permiso)
        if tiene_permiso('inventario.crear'):
            self._boton_accion(frame, "＋ Alta", BTN_GREEN, self._abrir_alta)

        # Los siguientes se habilitan al seleccionar una fila
        self.btn_baja = self._boton_accion(
            frame, "✕ Baja", BTN_RED, self._abrir_baja, estado='disabled'
        )
        self.btn_traslado = self._boton_accion(
            frame, "↔ Traslado", BTN_ORANGE, self._abrir_traslado, estado='disabled'
        )
        self.btn_historial = self._boton_accion(
            frame, "📋 Historial", BTN_BLUE, self._abrir_historial, estado='disabled'
        )

        # Actualizar a la derecha
        tk.Button(
            frame, text="↻ Actualizar",
            font=("Arial", 10), bg=BTN_GRAY, fg="white",
            relief="flat", cursor="hand2", padx=12, pady=6,
            command=self.cargar_animales,
        ).pack(side="right")

    def _boton_accion(self, parent, texto, color, comando, estado='normal'):
        btn = tk.Button(
            parent, text=texto,
            font=("Arial", 10, "bold"), bg=color, fg="white",
            relief="flat", cursor="hand2", padx=14, pady=6,
            state=estado, command=comando,
        )
        btn.pack(side="left", padx=(0, 8))
        return btn

    # ── Carga de datos ─────────────────────────────────────────

    def cargar_animales(self) -> None:
        """Consulta la BD y recarga la tabla con los filtros activos."""
        # Resolver IDs desde los nombres seleccionados
        nombre_lote = self.var_lote.get()
        nombre_cat  = self.var_categoria.get()
        id_lote     = self._mapa_lotes.get(nombre_lote)
        id_cat      = self._mapa_categorias.get(nombre_cat)

        animales = listar(
            id_lote       = id_lote,
            id_categoria  = id_cat,
            busqueda      = self.var_busqueda.get(),
            solo_activos  = self.var_solo_activos.get(),
        )

        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insertar filas
        for i, a in enumerate(animales):
            tag = 'par' if i % 2 == 0 else 'impar'
            if not a['activo']:
                tag = 'baja'
            self.tree.insert(
                '', 'end',
                iid=str(a['id_animal']),
                values=(
                    a['caravana'],
                    a['raza'],
                    a['categoria'],
                    a['sexo'],
                    a['lote'],
                    formatear(a['fecha_alta']),
                    '✓ Activo' if a['activo'] else '✗ Baja',
                ),
                tags=(tag,),
            )

        total = len(animales)
        self.lbl_total.config(text=f"{total} animal{'es' if total != 1 else ''}")
        self._on_seleccion(None)  # resetea botones

    # ── Eventos ────────────────────────────────────────────────

    def _on_seleccion(self, _event) -> None:
        """Habilita o deshabilita botones según si hay fila seleccionada."""
        hay_sel = bool(self.tree.selection())

        if hasattr(self, 'btn_baja'):
            puede_baja = hay_sel and tiene_permiso('inventario.eliminar')
            self.btn_baja.config(state='normal' if puede_baja else 'disabled')

        if hasattr(self, 'btn_traslado'):
            puede_tras = hay_sel and tiene_permiso('inventario.modificar')
            self.btn_traslado.config(state='normal' if puede_tras else 'disabled')

        if hasattr(self, 'btn_historial'):
            self.btn_historial.config(state='normal' if hay_sel else 'disabled')

    def _id_seleccionado(self) -> int | None:
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    # ── Navegación a formularios ───────────────────────────────

    def _abrir_alta(self) -> None:
        from views.inventario.alta_animal_view import AltaAnimalView
        AltaAnimalView(self, callback=self.cargar_animales)

    def _abrir_baja(self) -> None:
        id_animal = self._id_seleccionado()
        if not id_animal:
            return
        from views.inventario.baja_animal_view import BajaAnimalView
        BajaAnimalView(self, id_animal=id_animal, callback=self.cargar_animales)

    def _abrir_traslado(self) -> None:
        id_animal = self._id_seleccionado()
        if not id_animal:
            return
        from views.inventario.traslado_view import TrasladoView
        TrasladoView(self, id_animal=id_animal, callback=self.cargar_animales)

    def _abrir_historial(self) -> None:
        id_animal = self._id_seleccionado()
        if not id_animal:
            return
        from views.inventario.historial_view import HistorialView
        HistorialView(self, id_animal=id_animal)