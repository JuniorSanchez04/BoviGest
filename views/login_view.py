import tkinter as tk
from controllers.auth_controller import login


# ── Paleta de colores ──────────────────────────────────────────
BG          = "#1a1a2e"   # fondo general (azul muy oscuro)
CARD        = "#16213e"   # fondo de la tarjeta
INPUT_BG    = "#0d1b2a"   # fondo de los campos
ACCENT      = "#1b6ca8"   # línea debajo de los campos
BTN         = "#1b6ca8"   # botón normal
BTN_HOVER   = "#2980b9"   # botón al pasar el mouse
TEXT        = "#e0e0e0"   # texto principal
MUTED       = "#6b7a8d"   # texto secundario / placeholders
ERROR       = "#e74c3c"   # mensajes de error


class LoginView:

    ANCHO  = 420
    ALTO   = 530

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._configurar_ventana()
        self._construir_ui()

    # ── Configuración general de la ventana ───────────────────

    def _configurar_ventana(self) -> None:
        self.root.title("BoviGest — Inicio de Sesión")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self._centrar_ventana()

    def _centrar_ventana(self) -> None:
        self.root.update_idletasks()
        ancho_pantalla  = self.root.winfo_screenwidth()
        alto_pantalla   = self.root.winfo_screenheight()
        x = (ancho_pantalla  - self.ANCHO) // 2
        y = (alto_pantalla   - self.ALTO)  // 2
        self.root.geometry(f"{self.ANCHO}x{self.ALTO}+{x}+{y}")

    # ── Construcción de la interfaz ───────────────────────────

    def _construir_ui(self) -> None:
        # Contenedor principal centrado verticalmente
        contenedor = tk.Frame(self.root, bg=BG)
        contenedor.place(relx=0.5, rely=0.5, anchor="center")

        self._seccion_logo(contenedor)
        self._seccion_card(contenedor)
        self._seccion_version()

        # Foco inicial y atajo de teclado
        self.entry_username.focus()
        self.root.bind("<Return>", lambda _e: self._on_login())

    def _seccion_logo(self, parent: tk.Frame) -> None:
        """Ícono, nombre del sistema y subtítulo."""
        frame = tk.Frame(parent, bg=BG)
        frame.pack(pady=(0, 24))

        tk.Label(
            frame, text="🐄",
            font=("Arial", 46),
            bg=BG, fg=TEXT,
        ).pack()

        tk.Label(
            frame, text="BoviGest",
            font=("Arial", 22, "bold"),
            bg=BG, fg=TEXT,
        ).pack()

        tk.Label(
            frame, text="Sistema de Gestión Ganadera",
            font=("Arial", 9),
            bg=BG, fg=MUTED,
        ).pack()

    def _seccion_card(self, parent: tk.Frame) -> None:
        """Tarjeta con los campos de login."""
        card = tk.Frame(parent, bg=CARD, padx=42, pady=36)
        card.pack()

        # ── Campo: Usuario ─────────────────────────────────
        tk.Label(
            card, text="USUARIO",
            font=("Arial", 8, "bold"),
            bg=CARD, fg=MUTED, anchor="w",
        ).pack(fill="x")

        self.entry_username = tk.Entry(
            card,
            font=("Arial", 12),
            bg=INPUT_BG, fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            width=26,
            bd=0,
        )
        self.entry_username.pack(fill="x", ipady=8)
        tk.Frame(card, bg=ACCENT, height=2).pack(fill="x", pady=(2, 20))

        # ── Campo: Contraseña ──────────────────────────────
        tk.Label(
            card, text="CONTRASEÑA",
            font=("Arial", 8, "bold"),
            bg=CARD, fg=MUTED, anchor="w",
        ).pack(fill="x")

        self.entry_password = tk.Entry(
            card,
            font=("Arial", 12),
            bg=INPUT_BG, fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            width=26,
            bd=0,
            show="●",
        )
        self.entry_password.pack(fill="x", ipady=8)
        tk.Frame(card, bg=ACCENT, height=2).pack(fill="x", pady=(2, 20))

        # ── Mensaje de error (oculto por defecto) ──────────
        self.lbl_error = tk.Label(
            card, text="",
            font=("Arial", 9),
            bg=CARD, fg=ERROR,
            wraplength=280,
        )
        self.lbl_error.pack(pady=(0, 14))

        # ── Botón Ingresar ─────────────────────────────────
        self.btn_login = tk.Button(
            card, text="Ingresar",
            font=("Arial", 11, "bold"),
            bg=BTN, fg="white",
            activebackground=BTN_HOVER, activeforeground="white",
            relief="flat",
            cursor="hand2",
            width=24,
            command=self._on_login,
        )
        self.btn_login.pack(ipady=10)

        # Efecto hover
        self.btn_login.bind("<Enter>", lambda _e: self.btn_login.config(bg=BTN_HOVER))
        self.btn_login.bind("<Leave>", lambda _e: self.btn_login.config(bg=BTN))

    def _seccion_version(self) -> None:
        """Número de versión anclado al borde inferior de la ventana."""
        tk.Label(
            self.root, text="v1.0.0",
            font=("Arial", 8),
            bg=BG, fg=MUTED,
        ).place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-8)

    # ── Lógica de login ───────────────────────────────────────

    def _mostrar_error(self, mensaje: str) -> None:
        self.lbl_error.config(text=mensaje)

    def _limpiar_error(self) -> None:
        self.lbl_error.config(text="")

    def _set_cargando(self, cargando: bool) -> None:
        if cargando:
            self.btn_login.config(text="Verificando...", state="disabled")
        else:
            self.btn_login.config(text="Ingresar", state="normal")

    def _on_login(self) -> None:
        self._limpiar_error()

        username = self.entry_username.get()
        password = self.entry_password.get()

        self._set_cargando(True)
        self.root.update()   # fuerza el repintado antes de la query

        try:
            exito, error = login(username, password)
        except ConnectionError as e:
            self._mostrar_error(str(e))
            self._set_cargando(False)
            return

        if exito:
            self._abrir_dashboard()
        else:
            self._mostrar_error(error)
            self._set_cargando(False)
            # Limpia la contraseña y devuelve el foco
            self.entry_password.delete(0, tk.END)
            self.entry_password.focus()

    def _abrir_dashboard(self) -> None:
        from views.dashboard_view import DashboardView
        self.root.destroy()
        nueva_ventana = tk.Tk()
        DashboardView(nueva_ventana)
        nueva_ventana.mainloop()