import tkinter as tk
from tkinter import ttk, messagebox

from controllers import usuarios_controller as ctrl
from core.session import tiene_permiso

# ── Paleta de colores ──
BG_SIDEBAR = "#16213e"
BG_CONTENT = "#f4f6f9"
TEXT_LIGHT = "#e0e0e0"
TEXT_DARK = "#2c3e50"
ACCENT = "#1b6ca8"
HOVER_ACCENT = "#145382"
MUTED = "#6b7a8d"
HOVER_MUTED = "#535f6e"
DANGER = "#c0392b"
HOVER_DANGER = "#9c2e22"
BTN_OFF_BG = "#dfe3e8"
BTN_OFF_TEXT = "#9aa5b1"
SUCCESS = "#1e8e5a"
BORDER = "#e2e5eb"

COLOR_HOVER = {ACCENT: HOVER_ACCENT, MUTED: HOVER_MUTED, DANGER: HOVER_DANGER}


class UsuariosView:


    def __init__(self, area: tk.Frame) -> None:
        self.area = area
        self._filas = []
        self._configurar_estilos()
        self._construir_ui()
        self._cargar_datos()

    # ── Estilos visuales ────────────────────────────────────────

    def _configurar_estilos(self) -> None:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        # Estilo de la tabla
        style.configure("Treeview",
                        background="white",
                        fieldbackground="white",
                        foreground=TEXT_DARK,
                        rowheight=42,  # Filas un poco más altas para mejor lectura
                        font=("Arial", 10),
                        borderwidth=0)
        style.map("Treeview",
                  background=[("selected", "#eaf1f8")],
                  foreground=[("selected", TEXT_DARK)])

        style.configure("Treeview.Heading",
                        background="#eef1f6",
                        foreground=MUTED,
                        font=("Arial", 9, "bold"),
                        relief="flat",
                        padding=(10, 10))
        style.map("Treeview.Heading", background=[("active", "#e4e8ee")])

        # Estilo de inputs del formulario
        style.configure("Usuarios.TEntry", padding=8)
        style.configure("Usuarios.TCombobox", padding=8)

    # ── Construcción general ────────────────────────────────────

    def _construir_ui(self) -> None:
        encabezado = tk.Frame(self.area, bg=BG_CONTENT)
        encabezado.pack(fill="x", padx=24, pady=(20, 0))

        tk.Label(
            encabezado, text="👥  Usuarios",
            font=("Arial", 18, "bold"),
            bg=BG_CONTENT, fg=TEXT_DARK,
        ).pack(anchor="w")

        tk.Label(
            encabezado, text="Gestión de cuentas, roles y accesos del sistema.",
            font=("Arial", 10),
            bg=BG_CONTENT, fg=MUTED,
        ).pack(anchor="w", pady=(2, 0))

        self.contenedor_raiz = tk.Frame(self.area, bg=BG_CONTENT)
        self.contenedor_raiz.pack(fill="both", expand=True, padx=24, pady=(16, 20))

        self._construir_barra_superior()

        self.contenedor = tk.Frame(self.contenedor_raiz, bg=BG_CONTENT)
        self.contenedor.pack(fill="both", expand=True, pady=(16, 0))

        self._construir_tabla()

    def _construir_barra_superior(self) -> None:
        barra = tk.Frame(self.contenedor_raiz, bg=BG_CONTENT)
        barra.pack(fill="x")

        # ── Buscador ──
        caja_busqueda = tk.Frame(barra, bg="white", highlightbackground=BORDER, highlightthickness=1)
        caja_busqueda.pack(side="left", fill="x", expand=True, ipady=5)

        tk.Label(caja_busqueda, text="🔍", bg="white", fg=MUTED,
                 font=("Arial", 11)).pack(side="left", padx=(12, 6))

        self.var_busqueda = tk.StringVar()
        self.var_busqueda.trace_add("write", lambda *a: self._filtrar())
        entrada_buscar = tk.Entry(caja_busqueda, textvariable=self.var_busqueda,
                                  font=("Arial", 10), bd=0, bg="white",
                                  fg=TEXT_DARK, relief="flat")
        entrada_buscar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._placeholder_busqueda(entrada_buscar)

        # ── Botones de acción ──
        acciones = tk.Frame(barra, bg=BG_CONTENT)
        acciones.pack(side="right", padx=(16, 0))

        self.btn_nuevo = self._boton(acciones, "＋  Nuevo usuario", self._nuevo, ACCENT)
        self.btn_nuevo.pack(side="left")

        self.btn_editar = self._boton(acciones, "Editar", self._editar, MUTED)
        self.btn_editar.pack(side="left", padx=8)

        # Botón dinámico que cambiará entre Dar de baja / Reactivar
        self.btn_estado = self._boton(acciones, "Dar de baja", self._cambiar_estado, DANGER)
        self.btn_estado.pack(side="left")

    def _placeholder_busqueda(self, entry: tk.Entry) -> None:
        texto = "Buscar por nombre o usuario..."
        self._texto_placeholder = texto
        entry.insert(0, texto)
        entry.config(fg=MUTED)

        def on_focus_in(_e):
            if entry.get() == texto:
                entry.delete(0, "end")
                entry.config(fg=TEXT_DARK)

        def on_focus_out(_e):
            if not entry.get():
                entry.insert(0, texto)
                entry.config(fg=MUTED)

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def _boton(self, padre, texto: str, comando, color: str) -> tk.Label:
        lbl = tk.Label(padre, text=texto, bg=color, fg="white",
                       relief="flat", padx=18, pady=9, cursor="hand2",
                       font=("Arial", 9, "bold"))
        lbl._color_on = color
        lbl._color_hover = COLOR_HOVER.get(color, color)
        lbl._comando = comando
        lbl._habilitado = True

        lbl.bind("<Enter>", lambda e: lbl.config(bg=lbl._color_hover) if lbl._habilitado else None)
        lbl.bind("<Leave>", lambda e: lbl.config(bg=lbl._color_on) if lbl._habilitado else None)
        lbl.bind("<Button-1>", lambda e: lbl._comando() if lbl._habilitado else None)
        return lbl

    def _set_estado_boton(self, lbl: tk.Label, habilitado: bool) -> None:
        lbl._habilitado = habilitado
        lbl.config(bg=lbl._color_on if habilitado else BTN_OFF_BG,
                   fg="white" if habilitado else BTN_OFF_TEXT,
                   cursor="hand2" if habilitado else "arrow")

    # ── Tabla ────────────────────────────────────────────────────

    def _construir_tabla(self) -> None:
        self.frame_tabla = tk.Frame(self.contenedor, bg="white",
                                    highlightbackground=BORDER, highlightthickness=1)
        self.frame_tabla.pack(fill="both", expand=True)

        scroll_y = ttk.Scrollbar(self.frame_tabla, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        columnas = ("username", "nombre_completo", "rol", "estado")
        self.tabla = ttk.Treeview(self.frame_tabla, columns=columnas,
                                  show="headings", selectmode="browse",
                                  yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tabla.yview)

        self.tabla.heading("username", text="USUARIO")
        self.tabla.heading("nombre_completo", text="NOMBRE COMPLETO")
        self.tabla.heading("rol", text="ROL")
        self.tabla.heading("estado", text="ESTADO")

        # Alineación centrada para las etiquetas de Rol y Estado
        self.tabla.column("username", anchor="w", width=160)
        self.tabla.column("nombre_completo", anchor="w", width=250)
        self.tabla.column("rol", anchor="center", width=140)
        self.tabla.column("estado", anchor="center", width=120)

        self.tabla.pack(side="left", fill="both", expand=True)

        # Solo configuramos colores intercalados (cebra) para no saturar
        self.tabla.tag_configure("oddrow", background="white")
        self.tabla.tag_configure("evenrow", background="#f9fafc")

        self.tabla.bind("<<TreeviewSelect>>", lambda e: self._refrescar_botones())

        self.lbl_conteo = tk.Label(self.contenedor, text="", bg=BG_CONTENT,
                                   fg=MUTED, font=("Arial", 9))
        self.lbl_conteo.pack(anchor="w", pady=(10, 0))

    def _cargar_datos(self) -> None:
        self._filas = ctrl.listar_usuarios()
        self._mostrar_filas(self._filas)

    def _mostrar_filas(self, filas: list[dict]) -> None:
        self.tabla.delete(*self.tabla.get_children())

        for i, fila in enumerate(filas):
            nombre_completo = f"{fila['nombre']} {fila['apellido']}"
            activo = fila["activo"]

            # Puntos visuales modernos
            estado = "  Activo" if activo else "  Inactivo"
            tag_fondo = "evenrow" if i % 2 == 0 else "oddrow"

            self.tabla.insert(
                "", "end", iid=str(fila["id_usuario"]),
                values=(fila["username"], nombre_completo, fila["rol"], estado),
                tags=(tag_fondo,))

        total = len(self._filas)
        mostrados = len(filas)
        self.lbl_conteo.config(text=f"Mostrando {mostrados} de {total} usuarios")
        self._refrescar_botones()

    def _filtrar(self) -> None:
        if not hasattr(self, "tabla"):
            return
        texto = self.var_busqueda.get().strip().lower()
        if texto == self._texto_placeholder.lower():
            texto = ""
        filtradas = [
            f for f in self._filas
            if texto in f["username"].lower()
               or texto in f"{f['nombre']} {f['apellido']}".lower()
        ]
        self._mostrar_filas(filtradas)

    def _refrescar_botones(self) -> None:
        fila = self._fila_seleccionada()
        hay_seleccion = bool(fila)

        self._set_estado_boton(self.btn_nuevo, tiene_permiso("acceso.crear"))
        self._set_estado_boton(self.btn_editar, tiene_permiso("acceso.modificar") and hay_seleccion)

        # Lógica dinámica para el botón de estado
        permiso_estado = tiene_permiso("acceso.eliminar") and hay_seleccion
        self._set_estado_boton(self.btn_estado, permiso_estado)

        if hay_seleccion:
            if fila["activo"]:
                # Si está activo, el botón es para dar de baja (Rojo)
                self.btn_estado.config(text="Dar de baja", bg=DANGER)
                self.btn_estado._color_on = DANGER
                self.btn_estado._color_hover = HOVER_DANGER
            else:
                # Si está inactivo, el botón es para reactivar (Verde)
                self.btn_estado.config(text="Reactivar", bg=SUCCESS)
                self.btn_estado._color_on = SUCCESS
                self.btn_estado._color_hover = "#176e46"  # Color verde oscuro para el hover

    def _fila_seleccionada(self) -> dict | None:
        seleccion = self.tabla.selection()
        if not seleccion:
            return None
        pk = int(seleccion[0])
        return next((f for f in self._filas if f["id_usuario"] == pk), None)

    # ── Formulario de alta / edición (Diseño Mejorado) ─────────

    def _abrir_formulario(self, titulo: str, es_edicion: bool, valores: dict | None) -> None:
        if hasattr(self, "formulario"):
            return

        self.frame_tabla.pack_forget()
        self.lbl_conteo.pack_forget()
        self._set_estado_boton(self.btn_nuevo, False)
        self._set_estado_boton(self.btn_editar, False)
        self._set_estado_boton(self.btn_estado, False)  # Apaga el botón de estado

        # Contenedor principal del formulario (simulando una tarjeta)
        self.formulario = tk.Frame(self.contenedor, bg="white",
                                   highlightbackground=BORDER, highlightthickness=1)
        self.formulario.pack(fill="both", expand=True)

        canvas = tk.Canvas(self.formulario, bg="white", highlightthickness=0)
        scroll_form = ttk.Scrollbar(self.formulario, orient="vertical", command=canvas.yview)
        contenido = tk.Frame(canvas, bg="white")

        contenido.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=contenido, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scroll_form.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self._form_canvas = canvas

        canvas.pack(side="left", fill="both", expand=True)
        scroll_form.pack(side="right", fill="y")

        # ── Cabecera del formulario ──
        header_form = tk.Frame(contenido, bg="white")
        header_form.pack(fill="x", padx=40, pady=(35, 15))

        tk.Label(header_form, text=titulo, font=("Arial", 16, "bold"),
                 bg="white", fg=TEXT_DARK).pack(anchor="w")
        tk.Label(header_form, text="Completa la información. Los campos con * son obligatorios.",
                 font=("Arial", 9), bg="white", fg=MUTED).pack(anchor="w", pady=(4, 0))

        tk.Frame(contenido, bg=BORDER, height=1).pack(fill="x", padx=40)

        # ── Área de campos en grilla (Espaciada y limpia) ──
        campos_frame = tk.Frame(contenido, bg="white")
        campos_frame.pack(fill="x", padx=40, pady=(25, 10))
        campos_frame.columnconfigure(0, weight=1, uniform="col")
        campos_frame.columnconfigure(1, weight=1, uniform="col")

        self._widgets = {}
        roles = ctrl.listar_roles()
        nombres_rol = [r["nombre"] for r in roles]

        if es_edicion:
            self._campo_texto(campos_frame, "username", "Nombre de Usuario", valores, req=True, fila=0, columna=0)
            self._campo_combo(campos_frame, "id_rol", "Rol de Sistema", nombres_rol, roles, valores, req=True, fila=0,
                              columna=1)
        else:
            self._campo_texto(campos_frame, "nombre", "Nombres", valores, req=True, fila=0, columna=0)
            self._campo_texto(campos_frame, "apellido", "Apellidos", valores, req=True, fila=0, columna=1)
            self._campo_texto(campos_frame, "ci", "Documento de Identidad (CI)", valores, req=True, fila=1, columna=0)
            self._campo_texto(campos_frame, "telefono", "Número de Teléfono", valores, fila=1, columna=1)
            self._campo_texto(campos_frame, "email", "Correo Electrónico", valores, fila=2, columna=0, colspan=2)

            tk.Frame(campos_frame, bg=BORDER, height=1).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 25))

            self._campo_texto(campos_frame, "username", "Nombre de Usuario", valores, req=True, fila=4, columna=0)
            self._campo_texto(campos_frame, "password", "Contraseña", valores, req=True, oculto=True, fila=4, columna=1)
            self._campo_combo(campos_frame, "id_rol", "Rol de Sistema", nombres_rol, roles, valores, req=True, fila=5,
                              columna=0, colspan=2)

        self.lbl_error = tk.Label(contenido, text="", bg="white", fg=DANGER, font=("Arial", 9), wraplength=500,
                                  justify="left")
        self.lbl_error.pack(anchor="w", padx=40, pady=(0, 10))

        # ── Pie del formulario (Botones) ──
        pie = tk.Frame(contenido, bg="white")
        pie.pack(anchor="w", padx=40, pady=(10, 40))
        comando_guardar = self._guardar_edicion if es_edicion else self._guardar_nuevo

        self._boton(pie, "Guardar Cambios", comando_guardar, ACCENT).pack(side="left")
        self._boton(pie, "Cancelar", self._cerrar_formulario, MUTED).pack(side="left", padx=(12, 0))

    def _campo_texto(self, padre, clave: str, etiqueta: str, valores: dict | None,
                     req: bool = False, oculto: bool = False, fila: int = 0,
                     columna: int = 0, colspan: int = 1) -> None:
        contenedor = tk.Frame(padre, bg="white")
        pad_izq = 0 if columna == 0 else 15
        pad_der = 15 if columna == 0 and colspan == 1 else 0
        contenedor.grid(row=fila, column=columna, columnspan=colspan,
                        sticky="ew", padx=(pad_izq, pad_der), pady=(0, 20))

        texto_etiqueta = etiqueta + (" *" if req else "")
        tk.Label(contenedor, text=texto_etiqueta, font=("Arial", 9, "bold"),
                 bg="white", fg=TEXT_DARK).pack(anchor="w", pady=(0, 6))

        entry = ttk.Entry(contenedor, font=("Arial", 10), style="Usuarios.TEntry", show="•" if oculto else "")
        entry.pack(anchor="w", fill="x", ipady=4)
        if valores is not None and clave in valores and valores[clave]:
            entry.insert(0, str(valores[clave]))
        self._widgets[clave] = entry

    def _campo_combo(self, padre, clave: str, etiqueta: str, nombres: list[str],
                     opciones: list[dict], valores: dict | None, req: bool = False,
                     fila: int = 0, columna: int = 0, colspan: int = 1) -> None:
        contenedor = tk.Frame(padre, bg="white")
        pad_izq = 0 if columna == 0 else 15
        pad_der = 15 if columna == 0 and colspan == 1 else 0
        contenedor.grid(row=fila, column=columna, columnspan=colspan,
                        sticky="ew", padx=(pad_izq, pad_der), pady=(0, 20))

        texto_etiqueta = etiqueta + (" *" if req else "")
        tk.Label(contenedor, text=texto_etiqueta, font=("Arial", 9, "bold"),
                 bg="white", fg=TEXT_DARK).pack(anchor="w", pady=(0, 6))

        combo = ttk.Combobox(contenedor, values=nombres, state="readonly", font=("Arial", 10),
                             style="Usuarios.TCombobox")
        combo.pack(anchor="w", fill="x", ipady=4)
        if valores is not None and valores.get("rol"):
            combo.set(valores["rol"])
        self._widgets[clave] = (combo, opciones)

    def _leer_id_rol(self) -> int | None:
        combo, opciones = self._widgets["id_rol"]
        seleccion = combo.get()
        return next((o["id_rol"] for o in opciones if o["nombre"] == seleccion), None)

    def _cerrar_formulario(self) -> None:
        if hasattr(self, "formulario"):
            if hasattr(self, "_form_canvas"):
                self._form_canvas.unbind_all("<MouseWheel>")
                del self._form_canvas
            self.formulario.destroy()
            del self.formulario
        self.frame_tabla.pack(fill="both", expand=True)
        self.lbl_conteo.pack(anchor="w", pady=(10, 0))
        self._refrescar_botones()

    # ── Acciones de Base de datos ────────────────────────────────

    def _nuevo(self) -> None:
        if not tiene_permiso("acceso.crear"):
            return
        self._abrir_formulario("Nuevo Usuario", es_edicion=False, valores=None)

    def _guardar_nuevo(self) -> None:
        exito, error = ctrl.crear_usuario(
            self._widgets["nombre"].get().strip(),
            self._widgets["apellido"].get().strip(),
            self._widgets["ci"].get().strip(),
            self._widgets["telefono"].get().strip(),
            self._widgets["email"].get().strip(),
            self._widgets["username"].get().strip(),
            self._widgets["password"].get(),
            self._leer_id_rol(),
        )
        if exito:
            messagebox.showinfo("Éxito", "Usuario creado correctamente.")
            self._cerrar_formulario()
            self._cargar_datos()
        else:
            self.lbl_error.config(text=error)

    def _editar(self) -> None:
        if not tiene_permiso("acceso.modificar"):
            return
        fila = self._fila_seleccionada()
        if fila is None:
            return
        self._fila_en_edicion = fila
        self._abrir_formulario("Editar Usuario", es_edicion=True, valores=fila)

    def _guardar_edicion(self) -> None:
        exito, error = ctrl.actualizar_usuario(
            self._fila_en_edicion["id_usuario"],
            self._widgets["username"].get().strip(),
            self._leer_id_rol(),
        )
        if exito:
            messagebox.showinfo("Éxito", "Usuario actualizado correctamente.")
            self._cerrar_formulario()
            self._cargar_datos()
        else:
            self.lbl_error.config(text=error)

    def _cambiar_estado(self) -> None:
        if not tiene_permiso("acceso.eliminar"):
            return

        fila = self._fila_seleccionada()
        if fila is None:
            return

        esta_activo = fila["activo"]

        if esta_activo:
            mensaje = f"¿Estás seguro de dar de baja a «{fila['username']}»?"
            titulo = "Dar de baja"
        else:
            mensaje = f"¿Deseas reactivar al usuario «{fila['username']}» para que pueda volver a ingresar?"
            titulo = "Reactivar usuario"

        if not messagebox.askyesno(titulo, mensaje):
            return

        if esta_activo:
            exito, error = ctrl.eliminar_usuario(fila["id_usuario"])
            msg_exito = "Usuario dado de baja correctamente."
        else:
            exito, error = ctrl.activar_usuario(fila["id_usuario"])
            msg_exito = "Usuario reactivado correctamente."

        if exito:
            messagebox.showinfo("Éxito", msg_exito)
            self._cargar_datos()
        else:
            messagebox.showerror("Error", error)