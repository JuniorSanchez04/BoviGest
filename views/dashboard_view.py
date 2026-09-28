import tkinter as tk
from core.session import get_sesion, tiene_permiso
from controllers.auth_controller import logout

BG_SIDEBAR = "#16213e"
BG_CONTENT = "#f4f6f9"
TEXT_LIGHT = "#e0e0e0"
TEXT_DARK  = "#2c3e50"
ACCENT     = "#1b6ca8"
MUTED      = "#6b7a8d"


class DashboardView:

    def __init__(self, root: tk.Tk) -> None:
        self.root   = root
        self.sesion = get_sesion()
        self._configurar_ventana()
        self._construir_ui()

    def _configurar_ventana(self) -> None:
        nombre = f"{self.sesion['nombre']} {self.sesion['apellido']}"
        self.root.title(f"BoviGest — {nombre}  [{self.sesion['rol']}]")
        self.root.state("zoomed")
        self.root.configure(bg=BG_CONTENT)
        self.root.protocol("WM_DELETE_WINDOW", self._on_cerrar)

    def _construir_ui(self) -> None:
        self._construir_sidebar()
        self._construir_area_contenido()
        self._mostrar_bienvenida()

    # ── Sidebar ───────────────────────────────────────────────

    def _construir_sidebar(self) -> None:
        self.sidebar = tk.Frame(self.root, bg=BG_SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="🐄  BoviGest",
                 font=("Arial", 14, "bold"),
                 bg=BG_SIDEBAR, fg=TEXT_LIGHT, pady=20).pack(fill="x", padx=16)
        tk.Frame(self.sidebar, bg=ACCENT, height=1).pack(fill="x", padx=16, pady=(0, 8))

        for texto, icono, permiso, comando in self._opciones_menu():
            if tiene_permiso(permiso):
                self._boton_sidebar(texto, icono, comando)

        tk.Frame(self.sidebar, bg=ACCENT, height=1).pack(
            fill="x", padx=16, side="bottom", pady=8)
        self._boton_sidebar("Cerrar sesión", "🚪", self._cerrar_sesion, abajo=True)

        tk.Label(self.sidebar,
                 text=f"{self.sesion['nombre']} {self.sesion['apellido']}\n"
                      f"{self.sesion['rol']}",
                 font=("Arial", 9), bg=BG_SIDEBAR, fg=MUTED, justify="left",
                 ).pack(side="bottom", padx=16, pady=(0, 6), anchor="w")

    def _boton_sidebar(self, texto, icono, comando, abajo=False) -> None:
        btn = tk.Button(
            self.sidebar, text=f"  {icono}  {texto}",
            font=("Arial", 10), bg=BG_SIDEBAR, fg=TEXT_LIGHT,
            activebackground=ACCENT, activeforeground="white",
            relief="flat", anchor="w", cursor="hand2",
            command=comando,
        )
        btn.pack(fill="x", padx=8, pady=2,
                 side="bottom" if abajo else "top", ipady=8)
        btn.bind("<Enter>", lambda _e, b=btn: b.config(bg=ACCENT))
        btn.bind("<Leave>", lambda _e, b=btn: b.config(bg=BG_SIDEBAR))

    def _opciones_menu(self) -> list[tuple]:
        return [
            ("Inicio",           "🏠", "inventario.consultar", self._mostrar_bienvenida),
            ("Inventario",       "🐮", "inventario.consultar", self._ir_a_inventario),
            ("Sanidad",          "💉", "sanidad.consultar",    self._ir_a_sanidad),
            ("Producción / GMD", "⚖️", "produccion.consultar", self._ir_a_produccion),
            ("Usuarios",         "👥", "acceso.consultar",     self._placeholder),
            ("Catálogos",        "📋", "catalogos.consultar",  self._placeholder),
        ]

    # ── Área de contenido ─────────────────────────────────────

    def _construir_area_contenido(self) -> None:
        self.area = tk.Frame(self.root, bg=BG_CONTENT)
        self.area.pack(side="right", fill="both", expand=True)

    def _limpiar_area(self) -> None:
        for widget in self.area.winfo_children():
            widget.destroy()

    # ── Pantallas ──────────────────────────────────────────────

    def _mostrar_bienvenida(self) -> None:
        self._limpiar_area()
        tk.Label(self.area,
                 text=f"Bienvenido, {self.sesion['nombre']} 👋",
                 font=("Arial", 20, "bold"),
                 bg=BG_CONTENT, fg=TEXT_DARK).pack(pady=(60, 8))
        tk.Label(self.area,
                 text=f"Rol: {self.sesion['rol']}  ·  "
                      f"Permisos activos: {len(self.sesion['permisos'])}",
                 font=("Arial", 11), bg=BG_CONTENT, fg=MUTED).pack()

        cards = tk.Frame(self.area, bg=BG_CONTENT)
        cards.pack(pady=40)
        for icono, nombre, permiso in [
            ("🐮", "Inventario",       "inventario.consultar"),
            ("💉", "Sanidad",          "sanidad.consultar"),
            ("⚖️", "Producción / GMD", "produccion.consultar"),
            ("👥", "Usuarios",         "acceso.consultar"),
        ]:
            if tiene_permiso(permiso):
                c = tk.Frame(cards, bg="white", width=140, height=120)
                c.pack(side="left", padx=12, ipadx=10, ipady=10)
                c.pack_propagate(False)
                tk.Label(c, text=icono, font=("Arial", 28), bg="white").pack(pady=(16, 4))
                tk.Label(c, text=nombre, font=("Arial", 10, "bold"),
                         bg="white", fg=TEXT_DARK).pack()

    def _ir_a_inventario(self) -> None:
        self._limpiar_area()
        from views.inventario.inventario_view import InventarioView
        InventarioView(self.area)

    def _ir_a_sanidad(self) -> None:
        self._limpiar_area()
        from views.sanidad.sanidad_view import SanidadView
        SanidadView(self.area)


    def _ir_a_produccion(self) -> None:
        self._limpiar_area()
        from views.produccion.produccion_view import ProduccionView
        ProduccionView(self.area)
    def _placeholder(self) -> None:
        self._limpiar_area()
        tk.Label(self.area, text="🚧  Módulo en construcción",
                 font=("Arial", 16), bg=BG_CONTENT, fg=MUTED,
                 ).place(relx=0.5, rely=0.5, anchor="center")

    # ── Sesión ────────────────────────────────────────────────

    def _cerrar_sesion(self) -> None:
        logout()
        self.root.destroy()
        import tkinter as tk2
        from views.login_view import LoginView
        nueva = tk2.Tk()
        LoginView(nueva)
        nueva.mainloop()

    def _on_cerrar(self) -> None:
        logout()
        self.root.destroy()