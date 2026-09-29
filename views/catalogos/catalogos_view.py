import tkinter as tk
from tkinter import ttk, messagebox

from controllers import catalogos_controller as ctrl
from core.session import tiene_permiso

# ── Paleta de colores (la misma que dashboard_view) ───────────
BG_SIDEBAR = "#16213e"
BG_CONTENT = "#f4f6f9"
TEXT_LIGHT = "#e0e0e0"
TEXT_DARK = "#2c3e50"
ACCENT = "#1b6ca8"
HOVER_ACCENT = "#145382"  # Para efecto hover
MUTED = "#6b7a8d"
HOVER_MUTED = "#535f6e"  # Para efecto hover
DANGER = "#c0392b"
HOVER_DANGER = "#9c2e22"  # Para efecto hover
BTN_OFF_BG = "#dfe3e8"
BTN_OFF_TEXT = "#9aa5b1"

# Diccionario para mapear colores base a colores hover
COLOR_HOVER = {ACCENT: HOVER_ACCENT, MUTED: HOVER_MUTED, DANGER: HOVER_DANGER}


def campo(col, etiqueta, tipo="texto", req=False, ref_listar=None):
    """Define un campo del formulario. tipo: texto | entero | bool | ref"""
    return {"col": col, "etiqueta": etiqueta, "tipo": tipo, "req": req,
            "ref_listar": ref_listar}


# Cada catálogo: título, grupo, tabla (pk + columnas a mostrar) y,
# si no es de solo lectura, sus campos de formulario y sus funciones
# de crear/actualizar/eliminar del controlador.
CATALOGOS = [
    {
        "grupo": "GENERALES", "titulo": "Razas", "pk": "id_raza",
        "listar": ctrl.listar_razas,
        "columnas": [("Nombre", "nombre")],
        "campos": [campo("nombre", "Nombre", req=True)],
        "crear": ctrl.crear_raza, "actualizar": ctrl.actualizar_raza,
        "eliminar": ctrl.eliminar_raza,
    },
    {
        "grupo": "GENERALES", "titulo": "Sexos", "pk": "id_sexo",
        "listar": ctrl.listar_sexos,
        "columnas": [("Nombre", "nombre")],
        "solo_lectura": True,
    },
    {
        "grupo": "GENERALES", "titulo": "Categorías", "pk": "id_categoria",
        "listar": ctrl.listar_categorias,
        "columnas": [("Nombre", "nombre"), ("Descripción", "descripcion")],
        "campos": [
            campo("nombre", "Nombre", req=True),
            campo("descripcion", "Descripción"),
        ],
        "crear": ctrl.crear_categoria, "actualizar": ctrl.actualizar_categoria,
        "eliminar": ctrl.eliminar_categoria,
    },
    {
        "grupo": "GENERALES", "titulo": "Lotes / Potreros", "pk": "id_lote",
        "listar": ctrl.listar_lotes,
        "columnas": [("Nombre", "nombre"), ("Descripción", "descripcion"),
                     ("Capacidad", "capacidad"), ("Activo", "activo")],
        "campos": [
            campo("nombre", "Nombre", req=True),
            campo("descripcion", "Descripción"),
            campo("capacidad", "Capacidad (cabezas)", "entero"),
            campo("activo", "Activo", "bool"),
        ],
        "crear": ctrl.crear_lote, "actualizar": ctrl.actualizar_lote,
        "eliminar": ctrl.eliminar_lote,
    },
    {
        "grupo": "GENERALES", "titulo": "Motivos de baja",
        "pk": "id_motivo_baja",
        "listar": ctrl.listar_motivos_baja,
        "columnas": [("Nombre", "nombre")],
        "campos": [campo("nombre", "Nombre", req=True)],
        "crear": ctrl.crear_motivo_baja,
        "actualizar": ctrl.actualizar_motivo_baja,
        "eliminar": ctrl.eliminar_motivo_baja,
    },
    {
        "grupo": "GENERALES", "titulo": "Tipos de movimiento",
        "pk": "id_tipo_movimiento",
        "listar": ctrl.listar_tipos_movimiento,
        "columnas": [("Nombre", "nombre")],
        "solo_lectura": True,
    },
    {
        "grupo": "SANIDAD", "titulo": "Fármacos", "pk": "id_farmaco",
        "listar": ctrl.listar_farmacos,
        "columnas": [("Nombre", "nombre"),
                     ("Principio activo", "principio_activo"),
                     ("Días de carencia", "dias_carencia"),
                     ("Unidad", "unidad_medida")],
        "campos": [
            campo("nombre", "Nombre", req=True),
            campo("principio_activo", "Principio activo"),
            campo("dias_carencia", "Días de carencia", "entero", req=True),
            campo("unidad_medida", "Unidad"),
        ],
        "crear": ctrl.crear_farmaco, "actualizar": ctrl.actualizar_farmaco,
        "eliminar": ctrl.eliminar_farmaco,
    },
    {
        "grupo": "SANIDAD", "titulo": "Diagnósticos", "pk": "id_diagnostico",
        "listar": ctrl.listar_diagnosticos,
        "columnas": [("Nombre", "nombre"), ("Descripción", "descripcion")],
        "campos": [
            campo("nombre", "Nombre", req=True),
            campo("descripcion", "Descripción"),
        ],
        "crear": ctrl.crear_diagnostico,
        "actualizar": ctrl.actualizar_diagnostico,
        "eliminar": ctrl.eliminar_diagnostico,
    },
    {
        "grupo": "SANIDAD", "titulo": "Vacunas", "pk": "id_vacuna",
        "listar": ctrl.listar_vacunas,
        "columnas": [("Nombre", "nombre"), ("Laboratorio", "laboratorio"),
                     ("Revacunación (días)", "intervalo_revacunacion")],
        "campos": [
            campo("nombre", "Nombre", req=True),
            campo("laboratorio", "Laboratorio"),
            campo("intervalo_revacunacion", "Revacunación (días)", "entero"),
        ],
        "crear": ctrl.crear_vacuna, "actualizar": ctrl.actualizar_vacuna,
        "eliminar": ctrl.eliminar_vacuna,
    },
]


class CatalogosView:
    """
    Pantalla de Catálogos. Recibe el frame contenedor (self.area del
    dashboard) y arma ahí adentro el panel de catálogos + la tabla.
    """

    def __init__(self, area: tk.Frame) -> None:
        self.area = area
        self.catalogo_actual = CATALOGOS[0]
        self._configurar_estilos()
        self._construir_ui()
        self._cargar_datos()

    # ── Estilos Visuales Mejorados ────────────────────────────

    def _configurar_estilos(self):
        """Configura estilos de ttk para modernizar la tabla y forms."""
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("Treeview",
                        background="white",
                        fieldbackground="white",
                        foreground=TEXT_DARK,
                        rowheight=32,
                        font=("Arial", 10),
                        borderwidth=0)
        style.map("Treeview", background=[("selected", ACCENT)])

        style.configure("Treeview.Heading",
                        background="#eaf1f8",
                        foreground=TEXT_DARK,
                        font=("Arial", 10, "bold"),
                        relief="flat",
                        padding=(5, 8))
        style.map("Treeview.Heading", background=[("active", "#dfe3e8")])

        style.configure("TCheckbutton", background="white", font=("Arial", 10))

    # ── Construcción general ──────────────────────────────────

    def _construir_ui(self) -> None:
        tk.Label(
            self.area, text="Catálogos del Sistema",
            font=("Arial", 16, "bold"),
            bg=BG_CONTENT, fg=TEXT_DARK,
        ).pack(anchor="w", padx=20, pady=(16, 0))

        tk.Label(
            self.area, text="Datos base que se usan en los demás módulos.",
            font=("Arial", 9),
            bg=BG_CONTENT, fg=MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 10))

        cuerpo = tk.Frame(self.area, bg=BG_CONTENT)
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._construir_lista_catalogos(cuerpo)
        self._construir_panel_derecho(cuerpo)

    def _construir_lista_catalogos(self, cuerpo: tk.Frame) -> None:
        panel = tk.Frame(cuerpo, bg="white", width=190,
                         highlightbackground="#dfe3e8", highlightthickness=1)
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)

        self._botones_catalogo = {}
        grupo_actual = None
        for cat in CATALOGOS:
            if cat["grupo"] != grupo_actual:
                grupo_actual = cat["grupo"]
                tk.Label(panel, text=grupo_actual, font=("Arial", 8, "bold"),
                         bg="white", fg=MUTED, anchor="w").pack(
                    fill="x", padx=14, pady=(14, 4))
            btn = tk.Label(panel, text=cat["titulo"], font=("Arial", 10),
                           bg="white", fg=TEXT_DARK, anchor="w", padx=14,
                           pady=8, cursor="hand2")
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, c=cat: self._elegir_catalogo(c))

            btn.bind("<Enter>", lambda e, b=btn: self._hover_menu(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._hover_menu(b, False))

            self._botones_catalogo[cat["titulo"]] = btn

        self._marcar_catalogo_activo()

    def _hover_menu(self, btn, is_hover):
        titulo = btn.cget("text")
        if titulo != self.catalogo_actual["titulo"]:
            btn.config(bg="#f8f9fa" if is_hover else "white")

    def _marcar_catalogo_activo(self) -> None:
        for titulo, btn in self._botones_catalogo.items():
            activo = titulo == self.catalogo_actual["titulo"]
            btn.config(bg="#eaf1f8" if activo else "white",
                       fg=ACCENT if activo else TEXT_DARK,
                       font=("Arial", 10, "bold" if activo else "normal"))

    def _elegir_catalogo(self, catalogo: dict) -> None:
        self.catalogo_actual = catalogo
        self._marcar_catalogo_activo()
        self._cerrar_formulario()
        self._cargar_datos()

    # ── Panel derecho: título, botones, buscador, tabla ───────

    def _construir_panel_derecho(self, cuerpo: tk.Frame) -> None:
        self.panel_derecho = tk.Frame(cuerpo, bg=BG_CONTENT)
        self.panel_derecho.pack(side="left", fill="both", expand=True,
                                padx=(20, 0))

        barra = tk.Frame(self.panel_derecho, bg=BG_CONTENT)
        barra.pack(fill="x")

        self.lbl_titulo = tk.Label(barra, text=self.catalogo_actual["titulo"],
                                   font=("Arial", 14, "bold"),
                                   bg=BG_CONTENT, fg=TEXT_DARK)
        self.lbl_titulo.pack(side="left")

        self.lbl_aviso = tk.Label(barra, text="", font=("Arial", 9),
                                  bg=BG_CONTENT, fg=MUTED)
        self.lbl_aviso.pack(side="left", padx=(10, 0))

        self.btn_eliminar = self._boton(barra, "Eliminar", self._eliminar,
                                        DANGER)
        self.btn_eliminar.pack(side="right")
        self.btn_editar = self._boton(barra, "Editar", self._editar, MUTED)
        self.btn_editar.pack(side="right", padx=8)
        self.btn_nuevo = self._boton(barra, "Nuevo", self._nuevo, ACCENT)
        self.btn_nuevo.pack(side="right")

        busqueda = tk.Frame(self.panel_derecho, bg=BG_CONTENT)
        busqueda.pack(fill="x", pady=(14, 10))
        tk.Label(busqueda, text="Buscar:", bg=BG_CONTENT, fg=MUTED,
                 font=("Arial", 9, "bold")).pack(side="left", padx=(0, 8))
        self.var_busqueda = tk.StringVar()
        self.var_busqueda.trace_add("write", lambda *a: self._filtrar())

        entrada_buscar = ttk.Entry(busqueda, textvariable=self.var_busqueda, font=("Arial", 10))
        entrada_buscar.pack(side="left", fill="x", expand=True, ipady=3)

        self.contenedor = tk.Frame(self.panel_derecho, bg=BG_CONTENT)
        self.contenedor.pack(fill="both", expand=True)

        self._construir_tabla()

    # ── Botones Interactivos (Hover Effect) ───────────────────

    def _boton(self, padre, texto: str, comando, color: str) -> tk.Label:
        lbl = tk.Label(padre, text=texto, bg=color, fg="white",
                       relief="flat", padx=16, pady=6, cursor="hand2",
                       font=("Arial", 9, "bold"))
        lbl._color_on = color
        lbl._color_hover = COLOR_HOVER.get(color, color)
        lbl._comando = comando
        lbl._habilitado = True

        def on_enter(e):
            if lbl._habilitado: lbl.config(bg=lbl._color_hover)

        def on_leave(e):
            if lbl._habilitado: lbl.config(bg=lbl._color_on)

        lbl.bind("<Enter>", on_enter)
        lbl.bind("<Leave>", on_leave)
        lbl.bind("<Button-1>", lambda e: lbl._comando() if lbl._habilitado else None)
        return lbl

    def _set_estado_boton(self, lbl: tk.Label, habilitado: bool) -> None:
        lbl._habilitado = habilitado
        lbl.config(bg=lbl._color_on if habilitado else BTN_OFF_BG,
                   fg="white" if habilitado else BTN_OFF_TEXT,
                   cursor="hand2" if habilitado else "arrow")

    def _construir_tabla(self) -> None:
        self.frame_tabla = tk.Frame(self.contenedor, bg="white",
                                    highlightbackground="#dfe3e8",
                                    highlightthickness=1)
        self.frame_tabla.pack(fill="both", expand=True)

        scroll_y = ttk.Scrollbar(self.frame_tabla, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        self.tabla = ttk.Treeview(self.frame_tabla, show="headings",
                                  selectmode="browse", yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tabla.yview)
        self.tabla.pack(side="left", fill="both", expand=True)

        self.tabla.tag_configure("oddrow", background="white")
        self.tabla.tag_configure("evenrow", background="#f9fafc")

        self.tabla.bind("<<TreeviewSelect>>", lambda e: self._refrescar_botones())

    # ── Carga y filtrado de datos ──────────────────────────────

    def _cargar_datos(self) -> None:
        cat = self.catalogo_actual
        self.lbl_titulo.config(text=cat["titulo"])
        self.lbl_aviso.config(
            text="Solo lectura: valores fijos del sistema"
            if cat.get("solo_lectura") else "")

        columnas = [clave for _, clave in cat["columnas"]]
        self.tabla["columns"] = columnas
        for etiqueta, clave in cat["columnas"]:
            self.tabla.heading(clave, text=etiqueta)
            self.tabla.column(clave, anchor="w", width=150)

        self._filas = cat["listar"]()
        self.var_busqueda.set("")
        self._mostrar_filas(self._filas)

    def _mostrar_filas(self, filas: list[dict]) -> None:
        cat = self.catalogo_actual
        self.tabla.delete(*self.tabla.get_children())

        for i, fila in enumerate(filas):
            valores = []
            for _, clave in cat["columnas"]:
                valor = fila.get(clave)
                if clave == "activo" and valor is not None:
                    valor = "Sí" if valor else "No"
                valores.append("" if valor is None else valor)

            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tabla.insert("", "end", iid=str(fila[cat["pk"]]),
                              values=valores, tags=(tag,))
        self._refrescar_botones()

    def _filtrar(self) -> None:
        texto = self.var_busqueda.get().strip().lower()
        filtradas = [f for f in self._filas
                     if texto in str(f.get("nombre", "")).lower()]
        self._mostrar_filas(filtradas)

    # ── Permisos y estado de botones ──────────────────────────

    def _puede(self, permiso: str) -> bool:
        if self.catalogo_actual.get("solo_lectura"):
            return False
        return tiene_permiso(permiso)

    def _refrescar_botones(self) -> None:
        hay_seleccion = bool(self.tabla.selection())
        self._set_estado_boton(self.btn_nuevo, self._puede("catalogos.crear"))
        self._set_estado_boton(
            self.btn_editar,
            self._puede("catalogos.modificar") and hay_seleccion)
        self._set_estado_boton(
            self.btn_eliminar,
            self._puede("catalogos.eliminar") and hay_seleccion)

    def _fila_seleccionada(self) -> dict | None:
        seleccion = self.tabla.selection()
        if not seleccion:
            return None
        pk = int(seleccion[0])
        return next((f for f in self._filas
                     if f[self.catalogo_actual["pk"]] == pk), None)

    # ── Formulario de alta / edición ───────────────────────────

    def _abrir_formulario(self, titulo: str, valores: dict | None,
                          al_guardar) -> None:
        if hasattr(self, "formulario"):
            return

        cat = self.catalogo_actual
        self.frame_tabla.pack_forget()

        self._set_estado_boton(self.btn_nuevo, False)
        self._set_estado_boton(self.btn_editar, False)
        self._set_estado_boton(self.btn_eliminar, False)

        self.formulario = tk.Frame(self.contenedor, bg="white",
                                   highlightbackground="#dfe3e8",
                                   highlightthickness=1)
        self.formulario.pack(fill="x", anchor="n")

        header_form = tk.Frame(self.formulario, bg="white")
        header_form.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(header_form, text=titulo, font=("Arial", 14, "bold"),
                 bg="white", fg=TEXT_DARK).pack(anchor="w")
        tk.Label(header_form, text="Los campos con * son obligatorios.",
                 font=("Arial", 8), bg="white", fg=MUTED).pack(anchor="w", pady=(2, 0))

        self.campos_frame = tk.Frame(self.formulario, bg="white")
        self.campos_frame.pack(fill="x", padx=24, pady=5)

        self._widgets = {}
        for c in cat["campos"]:
            self._crear_campo(self.campos_frame, c, valores)

        self.lbl_error = tk.Label(self.formulario, text="", bg="white",
                                  fg=DANGER, font=("Arial", 9),
                                  wraplength=400, justify="left")
        self.lbl_error.pack(anchor="w", padx=24, pady=(10, 0))

        pie = tk.Frame(self.formulario, bg="white")
        pie.pack(anchor="w", padx=24, pady=(15, 24))
        self._boton(pie, "Guardar", lambda: al_guardar(), ACCENT).pack(
            side="left")
        self._boton(pie, "Cancelar", self._cerrar_formulario, MUTED).pack(
            side="left", padx=(10, 0))

    def _crear_campo(self, padre, c: dict, valores: dict | None) -> None:
        contenedor_campo = tk.Frame(padre, bg="white")
        contenedor_campo.pack(fill="x", pady=(0, 12))

        etiqueta = c["etiqueta"] + (" *" if c["req"] else "")
        tk.Label(contenedor_campo, text=etiqueta, font=("Arial", 9, "bold"),
                 bg="white", fg=TEXT_DARK).pack(anchor="w", pady=(0, 4))

        actual = None if valores is None else valores.get(c["col"])

        if c["tipo"] == "bool":
            valor_inicial = bool(actual) if valores else (c["col"] == "activo")
            var = tk.BooleanVar(value=valor_inicial)
            ttk.Checkbutton(contenedor_campo, variable=var).pack(anchor="w", padx=2)
            self._widgets[c["col"]] = var

        elif c["tipo"] == "ref":
            opciones = c["ref_listar"]()
            clave_id = next(k for k in opciones[0] if k != "nombre") if opciones else None
            nombres = [o["nombre"] for o in opciones]
            combo = ttk.Combobox(contenedor_campo, values=nombres, state="readonly",
                                 font=("Arial", 10))
            combo.pack(anchor="w", fill="x", ipady=4)
            if actual is not None:
                for o in opciones:
                    if o[clave_id] == actual:
                        combo.set(o["nombre"])
                        break
            self._widgets[c["col"]] = ("ref", combo, opciones, clave_id)

        else:
            entry = ttk.Entry(contenedor_campo, font=("Arial", 10))
            entry.pack(anchor="w", fill="x", ipady=4)
            if actual is not None:
                entry.insert(0, str(actual))
            self._widgets[c["col"]] = entry

    def _leer_formulario(self) -> list:
        valores = []
        for c in self.catalogo_actual["campos"]:
            w = self._widgets[c["col"]]
            if c["tipo"] == "bool":
                valores.append(w.get())
            elif isinstance(w, tuple) and w[0] == "ref":
                _, combo, opciones, clave_id = w
                seleccion = combo.get()
                encontrado = next(
                    (o[clave_id] for o in opciones if o["nombre"] == seleccion),
                    None)
                valores.append(encontrado)
            else:
                valores.append(w.get())
        return valores

    def _cerrar_formulario(self) -> None:
        if hasattr(self, "formulario"):
            self.formulario.destroy()
            del self.formulario
        self.frame_tabla.pack(fill="both", expand=True)
        self._refrescar_botones()

    def _nuevo(self) -> None:
        if not self._puede("catalogos.crear"):
            return
        cat = self.catalogo_actual

        def guardar():
            valores = self._leer_formulario()
            exito, error = cat["crear"](*valores)
            if exito:
                messagebox.showinfo("Éxito", "Se guardó correctamente.")
                self._cerrar_formulario()
                self._cargar_datos()
            else:
                self.lbl_error.config(text=error)

        self._abrir_formulario(f"Nueva {cat['titulo'].rstrip('s')}", None, guardar)

    def _editar(self) -> None:
        if not self._puede("catalogos.modificar"):
            return
        fila = self._fila_seleccionada()
        if fila is None:
            return
        cat = self.catalogo_actual

        def guardar():
            valores = self._leer_formulario()
            pk = fila[cat["pk"]]
            exito, error = cat["actualizar"](pk, *valores)
            if exito:
                messagebox.showinfo("Éxito", "Se actualizó correctamente.")
                self._cerrar_formulario()
                self._cargar_datos()
            else:
                self.lbl_error.config(text=error)

        self._abrir_formulario(f"Editar {cat['titulo'].rstrip('s')}", fila, guardar)

    def _eliminar(self) -> None:
        if not self._puede("catalogos.eliminar"):
            return
        fila = self._fila_seleccionada()
        if fila is None:
            return
        if not messagebox.askyesno(
                "Eliminar", f"¿Estás seguro de eliminar «{fila['nombre']}»?"):
            return
        cat = self.catalogo_actual
        pk = fila[cat["pk"]]
        exito, error = cat["eliminar"](pk)
        if exito:
            messagebox.showinfo("Éxito", "Se eliminó correctamente.")
            self._cargar_datos()
        else:
            messagebox.showerror("No se pudo eliminar", error)