import tkinter as tk
from core.session import get_sesion, tiene_permiso
from controllers.auth_controller import logout


# ── Paleta de colores (la misma base que el login) ────────────
BG_SIDEBAR  = "#16213e"
BG_CONTENT  = "#f4f6f9"
TEXT_LIGHT  = "#e0e0e0"
TEXT_DARK   = "#2c3e50"
ACCENT      = "#1b6ca8"
MUTED       = "#6b7a8d"


class DashboardView:
    """
    Ventana principal post-login.
    Estructura: sidebar izquierdo + área de contenido derecha.
    Se irá completando módulo a módulo.
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root    = root
        self.sesion  = get_sesion()
        self._configurar_ventana()
        self._construir_ui()

    # ── Configuración de la ventana ───────────────────────────

    def _configurar_ventana(self) -> None:
        nombre = f"{self.sesion['nombre']} {self.sesion['apellido']}"
        self.root.title(f"BoviGest — {nombre}  [{self.sesion['rol']}]")
        self.root.state("zoomed")          # maximizada al abrir
        self.root.configure(bg=BG_CONTENT)
        self.root.protocol("WM_DELETE_WINDOW", self._on_cerrar)

    # ── Construcción general ──────────────────────────────────

    def _construir_ui(self) -> None:
        self._construir_sidebar()
        self._construir_area_contenido()
        self._mostrar_bienvenida()

    # ── Sidebar ───────────────────────────────────────────────

    def _construir_sidebar(self) -> None:
        self.sidebar = tk.Frame(self.root, bg=BG_SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / nombre del sistema
        tk.Label(
            self.sidebar, text="🐄  BoviGest",
            font=("Arial", 14, "bold"),
            bg=BG_SIDEBAR, fg=TEXT_LIGHT,
            pady=20,
        ).pack(fill="x", padx=16)

        tk.Frame(self.sidebar, bg=ACCENT, height=1).pack(fill="x", padx=16, pady=(0, 8))

        # Opciones del menú según permisos de la sesión
        opciones = self._opciones_segun_rol()
        for texto, icono, clave_permiso, comando in opciones:
            if tiene_permiso(clave_permiso):
                self._boton_sidebar(texto, icono, comando)

        # Separador y botón Cerrar sesión al fondo
        tk.Frame(self.sidebar, bg=ACCENT, height=1).pack(
            fill="x", padx=16, side="bottom", pady=8
        )
        self._boton_sidebar("Cerrar sesión", "🚪", self._cerrar_sesion, abajo=True)

        # Datos del usuario al fondo
        tk.Label(
            self.sidebar,
            text=f"{self.sesion['nombre']} {self.sesion['apellido']}\n{self.sesion['rol']}",
            font=("Arial", 9),
            bg=BG_SIDEBAR, fg=MUTED,
            justify="left",
        ).pack(side="bottom", padx=16, pady=(0, 6), anchor="w")

    def _boton_sidebar(
        self, texto: str, icono: str, comando, abajo: bool = False
    ) -> None:
        btn = tk.Button(
            self.sidebar,
            text=f"  {icono}  {texto}",
            font=("Arial", 10),
            bg=BG_SIDEBAR, fg=TEXT_LIGHT,
            activebackground=ACCENT, activeforeground="white",
            relief="flat",
            anchor="w",
            cursor="hand2",
            command=comando,
        )
        side = "bottom" if abajo else "top"
        btn.pack(fill="x", padx=8, pady=2, side=side, ipady=8)
        btn.bind("<Enter>", lambda _e, b=btn: b.config(bg=ACCENT))
        btn.bind("<Leave>", lambda _e, b=btn: b.config(bg=BG_SIDEBAR))

    def _opciones_segun_rol(self) -> list[tuple]:
        """
        Devuelve la lista de opciones del sidebar.
        Cada entrada: (etiqueta, icono, permiso_requerido, comando)
        """
        return [
            ("Inicio",            "🏠", "inventario.consultar",  self._mostrar_bienvenida),
            ("Inventario",        "🐮", "inventario.consultar",  self._placeholder),
            ("Sanidad",           "💉", "sanidad.consultar",     self._placeholder),
            ("Producción / GMD",  "⚖️", "produccion.consultar",  self._placeholder),
            ("Usuarios",          "👥", "acceso.consultar",      self._placeholder),
            ("Catálogos",         "📋", "catalogos.consultar",   self._placeholder),
        ]

    # ── Área de contenido ─────────────────────────────────────

    def _construir_area_contenido(self) -> None:
        self.area = tk.Frame(self.root, bg=BG_CONTENT)
        self.area.pack(side="right", fill="both", expand=True)

    def _limpiar_area(self) -> None:
        """Elimina todos los widgets del área de contenido."""
        for widget in self.area.winfo_children():
            widget.destroy()

    # ── Pantalla de bienvenida ────────────────────────────────

    def _mostrar_bienvenida(self) -> None:
        self._limpiar_area()

        tk.Label(
            self.area,
            text=f"Bienvenido, {self.sesion['nombre']} 👋",
            font=("Arial", 20, "bold"),
            bg=BG_CONTENT, fg=TEXT_DARK,
        ).pack(pady=(60, 8))

        tk.Label(
            self.area,
            text=f"Rol: {self.sesion['rol']}  ·  "
                 f"Permisos activos: {len(self.sesion['permisos'])}",
            font=("Arial", 11),
            bg=BG_CONTENT, fg=MUTED,
        ).pack()

        # Tarjetas de módulos disponibles (según permisos)
        frame_tarjetas = tk.Frame(self.area, bg=BG_CONTENT)
        frame_tarjetas.pack(pady=40)

        modulos = [
            ("🐮", "Inventario",       "inventario.consultar"),
            ("💉", "Sanidad",          "sanidad.consultar"),
            ("⚖️", "Producción / GMD", "produccion.consultar"),
            ("👥", "Usuarios",         "acceso.consultar"),
        ]
        for icono, nombre, permiso in modulos:
            if tiene_permiso(permiso):
                self._tarjeta_modulo(frame_tarjetas, icono, nombre)

    def _tarjeta_modulo(
        self, parent: tk.Frame, icono: str, nombre: str
    ) -> None:
        card = tk.Frame(parent, bg="white", width=140, height=120, relief="flat")
        card.pack(side="left", padx=12, ipadx=10, ipady=10)
        card.pack_propagate(False)

        tk.Label(card, text=icono, font=("Arial", 28), bg="white").pack(pady=(16, 4))
        tk.Label(
            card, text=nombre,
            font=("Arial", 10, "bold"),
            bg="white", fg=TEXT_DARK,
        ).pack()

    # ── Placeholder (módulos pendientes) ─────────────────────

    def _placeholder(self) -> None:
        self._limpiar_area()
        tk.Label(
            self.area,
            text="🚧  Módulo en construcción",
            font=("Arial", 16),
            bg=BG_CONTENT, fg=MUTED,
        ).place(relx=0.5, rely=0.5, anchor="center")

    # ── Cerrar sesión / ventana ───────────────────────────────

    def _cerrar_sesion(self) -> None:
        logout()
        self.root.destroy()
        import tkinter as tk2
        from views.login_view import LoginView
        nueva_raiz = tk2.Tk()
        LoginView(nueva_raiz)
        nueva_raiz.mainloop()

    def _on_cerrar(self) -> None:
        """Al hacer click en la X de la ventana."""
        logout()
        self.root.destroy()