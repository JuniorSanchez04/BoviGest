import tkinter as tk
from tkinter import ttk, messagebox

from controllers.produccion_controller import (
    validar_item_masivo, guardar_pesajes_masivo,
)
from models.catalogo_model import obtener_lotes_activos
from utils.fecha_helper import hoy

BG      = "#f4f6f9"
HDR     = "#16213e"
TEXT    = "#2c3e50"
MUTED   = "#6b7a8d"
VERDE   = "#27ae60"
ROJO    = "#c0392b"
ACCENT  = "#1b6ca8"


class PesajeMasivoView(tk.Toplevel):
    """
    Formulario modal para registrar pesajes en lote ("rodeo de pesada").
    Patrón carrito: el usuario agrega animales uno a uno a una lista
    pendiente y guarda todo en una sola transacción al final.
    """

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback    = callback
        self._pendientes = []   # lista de dicts ya validados

        self.title("Pesaje Masivo")
        self.geometry("680x560")
        self.resizable(False, True)
        self.configure(bg=BG)
        self.grab_set()

        self._construir_ui()
        self._centrar()

    # ── UI ─────────────────────────────────────────────────────

    def _construir_ui(self) -> None:
        tk.Frame(self, bg=HDR, height=6).pack(fill="x")
        tk.Label(self, text="⚖️  Pesaje Masivo",
                 font=("Arial", 13, "bold"),
                 bg=BG, fg=TEXT, pady=10).pack(fill="x", padx=20)

        self._seccion_cabecera()
        self._seccion_entrada_rapida()
        self._seccion_lista_pendiente()
        self._seccion_botones_finales()

    def _seccion_cabecera(self) -> None:
        """Fecha y lote de referencia del rodeo."""
        sec = tk.Frame(self, bg=BG, padx=20, pady=4)
        sec.pack(fill="x")

        tk.Label(sec, text="Fecha del rodeo *  (DD/MM/AAAA):",
                 bg=BG, fg=TEXT, font=("Arial", 10)).grid(row=0, column=0, sticky="w")
        self.var_fecha = tk.StringVar(value=hoy())
        tk.Entry(sec, textvariable=self.var_fecha,
                 font=("Arial", 11), width=14,
                 relief="solid", bd=1).grid(row=0, column=1, padx=(8, 20), ipady=4)

        tk.Label(sec, text="Lote (referencia):",
                 bg=BG, fg=TEXT, font=("Arial", 10)).grid(row=0, column=2, sticky="w")
        lotes = obtener_lotes_activos()
        self._mapa_lotes = {l['nombre']: l['id_lote'] for l in lotes}
        self.var_lote = tk.StringVar()
        ttk.Combobox(sec, textvariable=self.var_lote,
                     values=[''] + [l['nombre'] for l in lotes],
                     state="readonly", width=18,
                     ).grid(row=0, column=3, padx=(8, 0))

    def _seccion_entrada_rapida(self) -> None:
        """Fila de ingreso rápido: caravana + peso + botón Agregar."""
        sec = tk.LabelFrame(self, text="Agregar animal",
                             bg=BG, fg=MUTED, font=("Arial", 9),
                             padx=12, pady=10)
        sec.pack(fill="x", padx=20, pady=(8, 4))

        tk.Label(sec, text="Caravana:", bg=BG, fg=TEXT,
                 font=("Arial", 10)).grid(row=0, column=0, sticky="w")
        self.var_caravana = tk.StringVar()
        self.entry_caravana = tk.Entry(sec, textvariable=self.var_caravana,
                                        font=("Arial", 11), width=16,
                                        relief="solid", bd=1)
        self.entry_caravana.grid(row=0, column=1, padx=(8, 16), ipady=4)
        self.entry_caravana.bind("<Return>", lambda _e: self.entry_peso.focus())
        self.entry_caravana.focus()

        tk.Label(sec, text="Peso (kg):", bg=BG, fg=TEXT,
                 font=("Arial", 10)).grid(row=0, column=2, sticky="w")
        self.var_peso = tk.StringVar()
        self.entry_peso = tk.Entry(sec, textvariable=self.var_peso,
                                    font=("Arial", 12, "bold"), width=10,
                                    relief="solid", bd=1)
        self.entry_peso.grid(row=0, column=3, padx=(8, 16), ipady=4)
        self.entry_peso.bind("<Return>", lambda _e: self._agregar())

        tk.Button(sec, text="＋ Agregar", font=("Arial", 10, "bold"),
                  bg=VERDE, fg="white", relief="flat", cursor="hand2", padx=10,
                  command=self._agregar).grid(row=0, column=4)

        # Label de error/feedback
        self.lbl_feedback = tk.Label(sec, text="",
                                      font=("Arial", 9),
                                      bg=BG, fg=ROJO, wraplength=500)
        self.lbl_feedback.grid(row=1, column=0, columnspan=5,
                                sticky="w", pady=(6, 0))

    def _seccion_lista_pendiente(self) -> None:
        """Treeview que muestra los pesajes pendientes de guardar."""
        sec = tk.LabelFrame(self, text="Pesajes a registrar",
                             bg=BG, fg=MUTED, font=("Arial", 9))
        sec.pack(fill="both", expand=True, padx=20, pady=(4, 4))

        frame = tk.Frame(sec, bg=BG)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.tree = ttk.Treeview(frame,
                                   columns=('num', 'caravana', 'categoria', 'peso'),
                                   show="headings", selectmode="browse")
        for col, titulo, ancho in [
            ('num',      '#',          40),
            ('caravana', 'Caravana',  100),
            ('categoria','Categoría', 120),
            ('peso',     'Peso (kg)',  90),
        ]:
            self.tree.heading(col, text=titulo)
            self.tree.column(col, width=ancho, anchor="center")

        sy = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sy.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        # Botón eliminar seleccionado
        tk.Button(sec, text="✕ Eliminar seleccionado",
                  font=("Arial", 9), bg="#e74c3c", fg="white",
                  relief="flat", cursor="hand2", pady=4,
                  command=self._eliminar_seleccionado).pack(pady=(0, 6))

        # Contador
        self.lbl_conteo = tk.Label(sec, text="0 pesajes en la lista",
                                    font=("Arial", 10, "bold"),
                                    bg=BG, fg=TEXT)
        self.lbl_conteo.pack(pady=(0, 4))

    def _seccion_botones_finales(self) -> None:
        frame = tk.Frame(self, bg=BG, pady=10, padx=20)
        frame.pack(fill="x")
        tk.Button(frame, text="Cancelar", font=("Arial", 10),
                  bg="#bdc3c7", fg="white", relief="flat",
                  cursor="hand2", width=12,
                  command=self.destroy).pack(side="right", padx=(8, 0))
        self.btn_guardar = tk.Button(frame, text="💾 Guardar todo (0)",
                                      font=("Arial", 10, "bold"),
                                      bg=ACCENT, fg="white",
                                      relief="flat", cursor="hand2", padx=14,
                                      state="disabled",
                                      command=self._guardar_todo)
        self.btn_guardar.pack(side="right")

    # ── Lógica ─────────────────────────────────────────────────

    def _ids_en_lista(self) -> set:
        """Retorna el conjunto de id_animal ya agregados a la lista."""
        return {item['id_animal'] for item in self._pendientes}

    def _agregar(self) -> None:
        self.lbl_feedback.config(text="", fg=ROJO)

        item, error = validar_item_masivo(
            self.var_caravana.get(),
            self.var_peso.get(),
            self.var_fecha.get(),
            self._ids_en_lista(),
        )

        if error:
            self.lbl_feedback.config(text=f"✗  {error}")
            return

        self._pendientes.append(item)
        n = len(self._pendientes)

        # Actualizar treeview
        self.tree.insert('', 'end', values=(
            n,
            item['caravana'],
            item['categoria'],
            f"{item['peso_kg']:.1f}",
        ))

        # Feedback positivo breve
        self.lbl_feedback.config(
            text=f"✓  {item['caravana']} — {item['peso_kg']:.1f} kg agregado",
            fg=VERDE)

        # Actualizar contador y botón
        self._actualizar_contador()

        # Limpiar campos para el siguiente animal
        self.var_caravana.set('')
        self.var_peso.set('')
        self.entry_caravana.focus()

    def _eliminar_seleccionado(self) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])   # posición en el treeview (0-based)
        self.tree.delete(sel[0])
        del self._pendientes[idx]

        # Renumerar las filas restantes
        for i, item_id in enumerate(self.tree.get_children()):
            self.tree.item(item_id, values=(
                i + 1,
                *self.tree.item(item_id, 'values')[1:]
            ))

        self._actualizar_contador()

    def _actualizar_contador(self) -> None:
        n = len(self._pendientes)
        self.lbl_conteo.config(text=f"{n} pesaje{'s' if n != 1 else ''} en la lista")
        self.btn_guardar.config(
            text=f"💾 Guardar todo ({n})",
            state="normal" if n > 0 else "disabled",
        )

    def _guardar_todo(self) -> None:
        exito, mensaje = guardar_pesajes_masivo(self._pendientes)
        if exito:
            messagebox.showinfo("Pesajes guardados", mensaje, parent=self)
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje, parent=self)

    def _centrar(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")