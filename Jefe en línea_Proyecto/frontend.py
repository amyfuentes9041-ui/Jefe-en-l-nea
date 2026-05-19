import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime

# ── Importar todo desde el backend ───────────────────────────────────────────
from backend import (
    auth_sys, tareas_sys, inventario_sys,
    finanzas_sys, ventas_prod_sys, mensajes_sys,
    ReporteDesempeno, CalendarioVisual
)

# ── Matplotlib integrado en Tkinter ──────────────────────────────────────────
import matplotlib
matplotlib.use("TkAgg")                          # Usa el backend de Tkinter
from matplotlib.figure import Figure            # Lienzo de la gráfica
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Widget Tkinter para la figura

# ─────────────────────────────────────────────────────────────────────────────
# PALETA Y CONFIGURACIÓN VISUAL
# ─────────────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

C_FONDO      = "#0d1117"
C_PANEL      = "#161b22"
C_BORDE      = "#30363d"
C_AZUL       = "#1f6feb"
C_AZUL_H     = "#388bfd"
C_VERDE      = "#238636"
C_VERDE_H    = "#2ea043"
C_ROJO       = "#da3633"
C_ROJO_H     = "#f85149"
C_AMBAR      = "#9e6a03"
C_AMBAR_H    = "#d29922"
C_LILA       = "#6e40c9"
C_LILA_H     = "#8957e5"
C_TEXTO      = "#e6edf3"
C_TEXTO_SUB  = "#8b949e"

# Colores para las gráficas matplotlib (modo oscuro)
COLORES_GRAF = ["#388bfd", "#2ea043", "#d29922", "#f85149",
                "#8957e5", "#3fb950", "#58a6ff", "#ffa657"]

# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES DE LA UI
# ─────────────────────────────────────────────────────────────────────────────

def limpiar(widget) -> None:
    """Destruye todos los hijos de un widget (limpia el área de contenido)."""
    for w in widget.winfo_children():
        w.destroy()

def estilo_tabla() -> None:
    """Aplica el tema oscuro a todos los Treeview de la app."""
    s = ttk.Style()
    s.theme_use("default")
    s.configure("Treeview",
                background="#161b22", foreground="#e6edf3",
                fieldbackground="#161b22", rowheight=26,
                font=("Consolas", 11))
    s.configure("Treeview.Heading",
                background="#21262d", foreground="#8b949e",
                font=("Consolas", 11, "bold"))
    s.map("Treeview", background=[("selected", "#1f6feb")])

def btn_nav(parent, texto, cmd, color=C_PANEL):
    """Botón de navegación lateral estandarizado."""
    return ctk.CTkButton(
        parent, text=texto, anchor="w",
        fg_color=color, hover_color="#21262d",
        font=("Consolas", 12, "bold"), height=38, corner_radius=6,
        command=cmd
    )

def titulo(parent, texto, pad_top=24):
    """Etiqueta de sección grande."""
    ctk.CTkLabel(parent, text=texto,
                 font=("Consolas", 19, "bold"),
                 text_color=C_TEXTO
                 ).pack(anchor="w", padx=28, pady=(pad_top, 8))

def separador(parent):
    ctk.CTkFrame(parent, height=1, fg_color=C_BORDE).pack(fill="x", pady=3)


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENTE: GRÁFICA MATPLOTLIB DENTRO DE UN FRAME CTK
# ─────────────────────────────────────────────────────────────────────────────

def crear_figura_oscura(ancho=5, alto=3.2) -> tuple:
    """
    Crea una figura de Matplotlib con fondo oscuro.
    Retorna (fig, ax) listos para agregar datos.
    El fondo coincide con la paleta de la app.
    """
    fig = Figure(figsize=(ancho, alto), dpi=100)
    fig.patch.set_facecolor("#161b22")   # Fondo del lienzo
    ax = fig.add_subplot(111)
    ax.set_facecolor("#0d1117")           # Fondo del área de la gráfica
    ax.tick_params(colors=C_TEXTO_SUB)   # Color de los números en los ejes
    ax.spines["bottom"].set_color(C_BORDE)
    ax.spines["left"].set_color(C_BORDE)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return fig, ax

def embed_figura(parent, fig) -> FigureCanvasTkAgg:
    """
    Incrusta una figura de Matplotlib dentro de un widget CustomTkinter.
    Retorna el canvas para que pueda actualizarse después.
    """
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
    return canvas


# ═════════════════════════════════════════════════════════════════════════════
# PANTALLA DE LOGIN
# ═════════════════════════════════════════════════════════════════════════════

def mostrar_login(ventana) -> None:
    """
    Pantalla inicial.  Pide usuario y contraseña.
    Llama a auth_sys.autenticar() y redirige al panel correcto según el rol.
    """
    limpiar(ventana)
    ventana.title("Jefe en Línea — Acceso")
    ventana.configure(fg_color=C_FONDO)

    marco = ctk.CTkFrame(ventana, fg_color=C_PANEL, corner_radius=18,
                          border_width=1, border_color=C_BORDE, width=420)
    marco.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(marco, text="👔", font=("Segoe UI Emoji", 52)).pack(pady=(28, 4))
    ctk.CTkLabel(marco, text="Jefe en Línea",
                 font=("Consolas", 26, "bold"), text_color=C_AZUL_H).pack()
    ctk.CTkLabel(marco, text="Sistema de Administración de Negocios",
                 font=("Consolas", 11), text_color=C_TEXTO_SUB).pack(pady=(0, 22))

    ent_user = ctk.CTkEntry(marco, placeholder_text="Usuario",
                             width=300, height=40, corner_radius=8)
    ent_user.pack(pady=6)

    ent_pass = ctk.CTkEntry(marco, placeholder_text="Contraseña",
                             show="*", width=300, height=40, corner_radius=8)
    ent_pass.pack(pady=6)

    lbl_err = ctk.CTkLabel(marco, text="", text_color=C_ROJO_H, font=("Consolas", 11))
    lbl_err.pack(pady=4)

    PANELS = {
        "jefe":       mostrar_panel_jefe,
        "gerente":    mostrar_panel_gerente,
        "supervisor": mostrar_panel_supervisor,
        "empleado":   mostrar_panel_empleado,
    }

    def intentar_login(event=None):
        """Lee los campos y llama a auth_sys.autenticar() para verificar."""
        user = ent_user.get().strip()
        pw   = ent_pass.get().strip()
        rol  = auth_sys.autenticar(user, pw)
        if rol in PANELS:
            PANELS[rol](ventana, user)
        else:
            lbl_err.configure(text="✖  Usuario o contraseña incorrectos.")

    ent_user.bind("<Return>", intentar_login)
    ent_pass.bind("<Return>", intentar_login)

    ctk.CTkButton(marco, text="Iniciar Sesión",
                  fg_color=C_AZUL, hover_color=C_AZUL_H,
                  font=("Consolas", 14, "bold"),
                  width=300, height=42, corner_radius=8,
                  command=intentar_login).pack(pady=(4, 28))


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: construye la ventana base (header + sidebar + área de contenido)
# ─────────────────────────────────────────────────────────────────────────────

def _construir_layout(ventana, nombre_usuario: str, secciones: list,
                       color_header=C_PANEL, subtitulo: str = "") -> ctk.CTkFrame:
    """
    Construye el layout estándar de un panel:
      - Header superior con nombre y botón de cerrar sesión
      - Sidebar izquierdo con botones de navegación
      - Área de contenido a la derecha (retornada para que la sección la use)
    """
    limpiar(ventana)
    ventana.after(0, lambda: ventana.state("zoomed"))

    # ── Header ────────────────────────────────────────────────────────────────
    hdr = ctk.CTkFrame(ventana, fg_color=color_header,
                        corner_radius=0, height=56)
    hdr.pack(fill="x", side="top")
    hdr.pack_propagate(False)

    ctk.CTkLabel(hdr, text=f"  👔  JEFE EN LÍNEA",
                 font=("Consolas", 19, "bold"),
                 text_color=C_AZUL_H).pack(side="left", padx=18, pady=10)
    ctk.CTkLabel(hdr, text=subtitulo,
                 font=("Consolas", 13), text_color=C_TEXTO_SUB
                 ).pack(side="left", padx=8)
    ctk.CTkLabel(hdr, text=f"👤  {nombre_usuario}",
                 font=("Consolas", 13, "bold"),
                 text_color=C_VERDE_H).pack(side="right", padx=120)
    ctk.CTkButton(hdr, text="Cerrar Sesión",
                  fg_color=C_ROJO, hover_color=C_ROJO_H,
                  font=("Consolas", 12, "bold"), width=130, height=34,
                  command=lambda: mostrar_login(ventana)
                  ).pack(side="right", padx=10, pady=10)

    # ── Body: sidebar + contenido ──────────────────────────────────────────────
    body = ctk.CTkFrame(ventana, fg_color=C_FONDO, corner_radius=0)
    body.pack(fill="both", expand=True)

    sidebar = ctk.CTkFrame(body, fg_color=C_PANEL, width=210,
                            corner_radius=0, border_width=1,
                            border_color=C_BORDE)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    area = ctk.CTkFrame(body, fg_color=C_FONDO, corner_radius=0)
    area.pack(side="left", fill="both", expand=True)

    ctk.CTkLabel(sidebar, text="MENÚ",
                 font=("Consolas", 10, "bold"),
                 text_color=C_TEXTO_SUB).pack(pady=(18, 4), padx=14, anchor="w")

    for texto, cmd in secciones:
        btn_nav(sidebar, texto, cmd).pack(fill="x", padx=10, pady=2)

    separador(sidebar)
    ctk.CTkLabel(sidebar,
                 text=f"{datetime.now().strftime('%d/%m/%Y')}",
                 font=("Consolas", 10), text_color=C_TEXTO_SUB).pack(pady=6)

    return area   # El llamador usa esta área para inyectar el contenido


# ═════════════════════════════════════════════════════════════════════════════
# PANEL: JEFE
# ═════════════════════════════════════════════════════════════════════════════

def mostrar_panel_jefe(ventana, usuario: str) -> None:
    """Panel del dueño del negocio. Ve las gráficas maestras y finanzas globales."""
    ventana.title(f"Jefe en Línea — Jefe  |  {usuario}")
    secciones = [
        ("📊  Dashboard Maestro",  lambda: sec_dashboard_jefe(area, usuario)),
        ("💰  Finanzas",           lambda: sec_finanzas(area, usuario)),
        ("👥  Gestión de Personal",lambda: sec_empleados(area, usuario)),
        ("✉️  Mensajes",           lambda: sec_mensajes(area, usuario)),
    ]
    area = _construir_layout(ventana, usuario, secciones,
                              subtitulo="— Jefe / Dueño")
    sec_dashboard_jefe(area, usuario)


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD JEFE: gráfica de pastel + barras + KPIs
# ─────────────────────────────────────────────────────────────────────────────

def sec_dashboard_jefe(area, usuario: str) -> None:
    """
    Muestra:
      · Tarjetas KPI (ventas del mes, utilidad, mensajes nuevos, alertas)
      · Gráfica de PASTEL  → distribución de dinero por categoría
      · Gráfica de BARRAS  → ventas diarias del mes actual
    """
    limpiar(area)
    titulo(area, "📊  Dashboard Maestro")

    # ── Fila de KPIs ──────────────────────────────────────────────────────────
    frame_kpis = ctk.CTkFrame(area, fg_color="transparent")
    frame_kpis.pack(fill="x", padx=28, pady=4)

    ventas_m = finanzas_sys.obtener_total_ventas("mensual")
    utilidad = finanzas_sys.calcular_utilidad_neta()
    msgs_n   = mensajes_sys.no_leidos_de(usuario)
    alertas  = len(inventario_sys.alertas_stock())
    vencidas = len(tareas_sys.tareas_vencidas())
    colisiones = len(tareas_sys.colisiones_activas())

    kpis = [
        ("💰 Ventas Mes",      f"${ventas_m:,.0f}",   C_VERDE),
        ("📈 Utilidad Neta",   f"${utilidad:,.0f}",   C_AZUL),
        ("✉️ Mensajes Nuevos", str(msgs_n),            C_AZUL_H),
        ("⚠ Stock Bajo",      str(alertas),           C_AMBAR_H),
        ("⏰ Tareas Vencidas", str(vencidas),          C_ROJO_H),
        ("🔀 Colisiones",      str(colisiones),        C_LILA_H),
    ]
    for i, (lbl, val, color) in enumerate(kpis):
        card = ctk.CTkFrame(frame_kpis, fg_color=C_PANEL, corner_radius=10,
                             border_width=2, border_color=color,
                             width=165, height=88)
        card.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=val, font=("Consolas", 26, "bold"),
                     text_color=color).place(relx=0.5, rely=0.38, anchor="center")
        ctk.CTkLabel(card, text=lbl, font=("Consolas", 9),
                     text_color=C_TEXTO_SUB).place(relx=0.5, rely=0.78, anchor="center")
    for c in range(len(kpis)):
        frame_kpis.grid_columnconfigure(c, weight=1)

    # ── Dos gráficas lado a lado ───────────────────────────────────────────────
    frame_graficas = ctk.CTkFrame(area, fg_color="transparent")
    frame_graficas.pack(fill="both", expand=True, padx=28, pady=8)

    # ── GRÁFICA DE PASTEL ─────────────────────────────────────────────────────
    frame_pastel = ctk.CTkFrame(frame_graficas, fg_color=C_PANEL,
                                 corner_radius=12, border_width=1,
                                 border_color=C_BORDE)
    frame_pastel.pack(side="left", fill="both", expand=True, padx=(0, 6))

    ctk.CTkLabel(frame_pastel, text="Distribución por Categoría (Pastel)",
                 font=("Consolas", 11, "bold"),
                 text_color=C_TEXTO_SUB).pack(anchor="w", padx=12, pady=(10, 0))

    datos_pastel = finanzas_sys.datos_grafica_pastel()
    fig_p, ax_p = crear_figura_oscura(5, 3.4)
    if datos_pastel:
        ax_p.pie(
            list(datos_pastel.values()),
            labels=list(datos_pastel.keys()),
            colors=COLORES_GRAF[:len(datos_pastel)],
            autopct="%1.1f%%",
            pctdistance=0.82,
            textprops={"color": C_TEXTO, "fontsize": 9},
            wedgeprops={"edgecolor": C_FONDO, "linewidth": 2},
        )
        ax_p.set_title("Flujo de Dinero", color=C_TEXTO, fontsize=11, pad=8)
    else:
        ax_p.text(0.5, 0.5, "Sin datos aún", ha="center", va="center",
                  color=C_TEXTO_SUB, fontsize=12, transform=ax_p.transAxes)
    embed_figura(frame_pastel, fig_p)

    # ── GRÁFICA DE BARRAS ─────────────────────────────────────────────────────
    frame_barras = ctk.CTkFrame(frame_graficas, fg_color=C_PANEL,
                                 corner_radius=12, border_width=1,
                                 border_color=C_BORDE)
    frame_barras.pack(side="left", fill="both", expand=True, padx=(6, 0))

    ctk.CTkLabel(frame_barras, text="Ventas Diarias del Mes (Barras)",
                 font=("Consolas", 11, "bold"),
                 text_color=C_TEXTO_SUB).pack(anchor="w", padx=12, pady=(10, 0))

    datos_barras = finanzas_sys.datos_grafica_barras()
    fig_b, ax_b = crear_figura_oscura(5, 3.4)
    if datos_barras:
        dias   = list(datos_barras.keys())
        ventas = list(datos_barras.values())
        bars   = ax_b.bar(dias, ventas, color=C_AZUL, edgecolor=C_FONDO,
                           linewidth=1.5, width=0.7)
        ax_b.set_xlabel("Día del mes", color=C_TEXTO_SUB, fontsize=9)
        ax_b.set_ylabel("$ MXN",       color=C_TEXTO_SUB, fontsize=9)
        ax_b.set_title("Ventas del Mes", color=C_TEXTO, fontsize=11, pad=8)
        # Etiqueta con el valor encima de cada barra
        for bar, val in zip(bars, ventas):
            ax_b.text(bar.get_x() + bar.get_width() / 2,
                       bar.get_height() + max(ventas) * 0.02,
                       f"${val:,.0f}",
                       ha="center", va="bottom",
                       color=C_TEXTO, fontsize=7)
    else:
        ax_b.text(0.5, 0.5, "Sin datos aún", ha="center", va="center",
                  color=C_TEXTO_SUB, fontsize=12, transform=ax_b.transAxes)
    embed_figura(frame_barras, fig_b)


# ═════════════════════════════════════════════════════════════════════════════
# PANEL: GERENTE
# ═════════════════════════════════════════════════════════════════════════════

def mostrar_panel_gerente(ventana, usuario: str) -> None:
    """Panel del gerente: metas, tareas, inventario, promociones y sus gráficas."""
    ventana.title(f"Jefe en Línea — Gerente  |  {usuario}")
    secciones = [
        ("📊  Dashboard Operativo", lambda: sec_dashboard_gerente(area, usuario)),
        ("📋  Gestión de Tareas",   lambda: sec_tareas(area, usuario, puede_crear=True)),
        ("📦  Inventario",          lambda: sec_inventario(area, usuario)),
        ("🏷️  Promociones",         lambda: sec_promociones(area, usuario)),
        ("✉️  Mensajes",            lambda: sec_mensajes(area, usuario)),
    ]
    area = _construir_layout(ventana, usuario, secciones,
                              subtitulo="— Gerente")
    sec_dashboard_gerente(area, usuario)


def sec_dashboard_gerente(area, usuario: str) -> None:
    """
    Dashboard del gerente. Muestra:
      · Gráfica de barras: ventas reales vs metas configuradas
      · Gráfica de pastel: distribución de gastos operativos
      · Tabla de tareas vencidas y colisiones horarias
    """
    limpiar(area)
    titulo(area, "📊  Dashboard Operativo")

    gerente_obj = auth_sys.usuarios.get(usuario)
    metas = getattr(gerente_obj, "metas_mensuales", {}) if gerente_obj else {}

    # ── Gráfica de barras: Real vs Meta ───────────────────────────────────────
    frame_g = ctk.CTkFrame(area, fg_color="transparent")
    frame_g.pack(fill="both", expand=True, padx=28, pady=6)

    # Panel derecho: pastel de gastos
    frame_p2 = ctk.CTkFrame(frame_g, fg_color=C_PANEL, corner_radius=12,
                              border_width=1, border_color=C_BORDE)
    frame_p2.pack(side="left", fill="both", expand=True, padx=(0, 0))

    ctk.CTkLabel(frame_p2, text="Distribución de Gastos",
                 font=("Consolas", 11, "bold"),
                 text_color=C_TEXTO_SUB).pack(anchor="w", padx=12, pady=(10, 0))

    datos_p = finanzas_sys.datos_grafica_pastel()
    solo_gastos = {k: v for k, v in datos_p.items() if k != "Venta"}
    fig_p2, ax_p2 = crear_figura_oscura(5, 3.5)
    if solo_gastos:
        ax_p2.pie(
            list(solo_gastos.values()),
            labels=list(solo_gastos.keys()),
            colors=COLORES_GRAF[:len(solo_gastos)],
            autopct="%1.1f%%", pctdistance=0.82,
            textprops={"color": C_TEXTO, "fontsize": 9},
            wedgeprops={"edgecolor": C_FONDO, "linewidth": 2},
        )
        ax_p2.set_title("Egresos", color=C_TEXTO, fontsize=11, pad=8)
    else:
        ax_p2.text(0.5, 0.5, "Sin gastos registrados",
                   ha="center", va="center", color=C_TEXTO_SUB,
                   fontsize=11, transform=ax_p2.transAxes)
    embed_figura(frame_p2, fig_p2)

    # ── Alertas ───────────────────────────────────────────────────────────────
    colisiones = tareas_sys.colisiones_activas()
    if colisiones:
        ctk.CTkLabel(area, text=f"🔀  {len(colisiones)} colisión(es) horaria(s) detectadas:",
                     font=("Consolas", 12, "bold"),
                     text_color=C_LILA_H).pack(anchor="w", padx=28, pady=(6, 2))
        scroll = ctk.CTkScrollableFrame(area, fg_color=C_PANEL,
                                         height=70, corner_radius=8)
        scroll.pack(fill="x", padx=28, pady=(0, 6))
        for a, b in colisiones:
            ctk.CTkLabel(scroll,
                         text=f"  ⚡ {a.titulo} ({a.hora_inicio}-{a.hora_fin})  ↔  "
                              f"{b.titulo} ({b.hora_inicio}-{b.hora_fin})  →  {a.asignado_a}",
                         font=("Consolas", 10), text_color=C_LILA_H,
                         anchor="w").pack(anchor="w", padx=10, pady=1)


# ═════════════════════════════════════════════════════════════════════════════
# PANEL: SUPERVISOR
# ═════════════════════════════════════════════════════════════════════════════

def mostrar_panel_supervisor(ventana, usuario: str) -> None:
    """Panel del supervisor: pizarra kanban de su equipo + mensajes."""
    ventana.title(f"Jefe en Línea — Supervisor  |  {usuario}")
    secciones = [
        ("📋  Pizarra Kanban",     lambda: sec_pizarra_kanban(area, usuario)),
        ("📈  Reporte de Turno",   lambda: sec_reporte_turno(area, usuario)),
        ("✉️  Mensajes",           lambda: sec_mensajes(area, usuario)),
    ]
    area = _construir_layout(ventana, usuario, secciones,
                              subtitulo="— Supervisor")
    sec_pizarra_kanban(area, usuario)


def sec_pizarra_kanban(area, usuario: str) -> None:
    """
    Pizarra digital del supervisor.
    Muestra todas las tareas del equipo con código de colores por estado.
    Resalta en rojo las colisiones horarias detectadas.
    Permite asignar nuevas tareas y cambiar estados.
    """
    limpiar(area)
    estilo_tabla()
    titulo(area, "📋  Pizarra Kanban del Equipo")

    # ── Formulario de nueva tarea ─────────────────────────────────────────────
    frame_form = ctk.CTkFrame(area, fg_color=C_PANEL, corner_radius=10,
                               border_width=1, border_color=C_BORDE)
    frame_form.pack(fill="x", padx=28, pady=(0, 8))

    ctk.CTkLabel(frame_form, text="  Asignar Nueva Tarea",
                 font=("Consolas", 11, "bold"),
                 text_color=C_AZUL_H).grid(row=0, column=0, columnspan=8,
                                            sticky="w", padx=10, pady=(8, 4))

    empleados_n = [u.nombre_usuario for u in auth_sys.por_rol("empleado")]
    if not empleados_n:
        empleados_n = ["(sin empleados)"]

    ent_tit  = ctk.CTkEntry(frame_form, placeholder_text="Título",    width=170)
    ent_desc = ctk.CTkEntry(frame_form, placeholder_text="Descripción",width=170)
    combo_emp= ctk.CTkComboBox(frame_form, values=empleados_n,         width=130)
    combo_pri= ctk.CTkComboBox(frame_form, values=["1","2","3","4","5"],width=60)
    combo_pri.set("3")
    ent_ini  = ctk.CTkEntry(frame_form, placeholder_text="HH:MM ini", width=80)
    ent_fin  = ctk.CTkEntry(frame_form, placeholder_text="HH:MM fin", width=80)
    ent_fecha= ctk.CTkEntry(frame_form, placeholder_text="AAAA-MM-DD",width=110)

    ws = [ent_tit, ent_desc, combo_emp, combo_pri, ent_ini, ent_fin, ent_fecha]
    ls = ["Título","Descripción","Asignar a","Prio.","H.Inicio","H.Fin","Fecha"]
    for i, (lbl, w) in enumerate(zip(ls, ws)):
        ctk.CTkLabel(frame_form, text=lbl, font=("Consolas", 9),
                     text_color=C_TEXTO_SUB).grid(row=1, column=i, padx=6, pady=1)
        w.grid(row=2, column=i, padx=6, pady=6)

    # ── Tabla de pizarra ──────────────────────────────────────────────────────
    cols = ("id","titulo","asignado","prio","estado","ini","fin","fecha","col")
    tabla = ttk.Treeview(area, columns=cols, show="headings", height=13)
    datos_cols = [
        ("id",      60,  "ID"),
        ("titulo",  180, "Título"),
        ("asignado",120, "Asignado a"),
        ("prio",    60,  "Prio."),
        ("estado",  100, "Estado"),
        ("ini",     70,  "Inicio"),
        ("fin",     70,  "Fin"),
        ("fecha",   100, "Fecha"),
        ("col",     90,  "⚡Colisión"),
    ]
    for col, ancho, lbl in datos_cols:
        tabla.heading(col, text=lbl)
        tabla.column(col, width=ancho)
    tabla.pack(padx=28, pady=4, fill="both", expand=True)
    tabla.tag_configure("colision",   background="#2d0f3c", foreground="#8957e5")
    tabla.tag_configure("vencida",    background="#3d0000", foreground="#f85149")
    tabla.tag_configure("completada", background="#0d2818", foreground="#2ea043")
    tabla.tag_configure("en_curso",   background="#0d1f3c", foreground="#388bfd")

    def actualizar_tabla():
        for item in tabla.get_children():
            tabla.delete(item)
        # Obtener los pares con colisión para poder marcarlos
        pares_col = tareas_sys.colisiones_activas()
        ids_col   = {t.id_tarea for par in pares_col for t in par}

        for t in tareas_sys.tareas:
            col_marca = "⚡ SÍ" if t.id_tarea in ids_col else ""
            if t.id_tarea in ids_col:
                tag = "colision"
            elif t.verificar_plazo():
                tag = "vencida"
            elif t.estado == "Completado":
                tag = "completada"
            elif t.estado == "En curso":
                tag = "en_curso"
            else:
                tag = ""
            tabla.insert("", "end",
                         values=(t.id_tarea, t.titulo, t.asignado_a,
                                 t.prioridad, t.estado,
                                 t.hora_inicio, t.hora_fin, t.fecha,
                                 col_marca),
                         tags=(tag,))

    # ── Botones de acción ─────────────────────────────────────────────────────
    frame_acc = ctk.CTkFrame(area, fg_color="transparent")
    frame_acc.pack(padx=28, pady=(0, 8))

    def crear_tarea():
        t    = ent_tit.get().strip()
        desc = ent_desc.get().strip()
        emp  = combo_emp.get()
        prio = int(combo_pri.get())
        ini  = ent_ini.get().strip()
        fin  = ent_fin.get().strip()
        fech = ent_fecha.get().strip()

        if not all([t, emp, ini, fin, fech]):
            messagebox.showwarning("Atención", "Completa al menos: título, empleado, horario y fecha.")
            return

        nueva, colisiones = tareas_sys.crear_tarea(t, desc, prio, emp,
                                                    ini, fin, usuario, fech)
        if colisiones:
            txt = "\n".join(f"  • {a.titulo} ↔ {b.titulo}" for a, b in colisiones)
            messagebox.showwarning("⚡ Colisión Horaria",
                                   f"La tarea se creó pero se detectaron choques:\n{txt}")
        actualizar_tabla()
        for w in [ent_tit, ent_desc, ent_ini, ent_fin, ent_fecha]:
            w.delete(0, "end")

    def cambiar_estado():
        sel = tabla.selection()
        if not sel:
            return
        id_t = tabla.item(sel[0])["values"][0]
        dlg  = ctk.CTkToplevel()
        dlg.title("Cambiar Estado")
        dlg.geometry("300x170")
        dlg.grab_set()
        ctk.CTkLabel(dlg, text=f"Estado de {id_t}",
                     font=("Consolas", 13, "bold")).pack(pady=14)
        combo = ctk.CTkComboBox(dlg,
                                 values=["Pendiente","En curso","Revisión","Completado"],
                                 width=240)
        combo.pack(pady=8)
        def aplicar():
            tareas_sys.actualizar_estado(str(id_t), combo.get())
            actualizar_tabla()
            dlg.destroy()
        ctk.CTkButton(dlg, text="Aplicar", fg_color=C_AZUL,
                      command=aplicar).pack(pady=8)

    def eliminar_tarea():
        sel = tabla.selection()
        if not sel:
            return
        id_t = tabla.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar la tarea {id_t}?"):
            tareas_sys.eliminar_tarea(str(id_t))
            actualizar_tabla()

    ctk.CTkButton(frame_form, text="Asignar Tarea",
                  fg_color=C_VERDE, hover_color=C_VERDE_H,
                  font=("Consolas", 11, "bold"),
                  command=crear_tarea).grid(row=2, column=7, padx=10)

    ctk.CTkButton(frame_acc, text="Cambiar Estado",
                  fg_color=C_AMBAR, hover_color=C_AMBAR_H,
                  font=("Consolas", 11, "bold"),
                  command=cambiar_estado).grid(row=0, column=0, padx=8)
    ctk.CTkButton(frame_acc, text="Eliminar Tarea",
                  fg_color=C_ROJO, hover_color=C_ROJO_H,
                  font=("Consolas", 11, "bold"),
                  command=eliminar_tarea).grid(row=0, column=1, padx=8)

    actualizar_tabla()


def sec_reporte_turno(area, usuario: str) -> None:
    """
    El supervisor ve el reporte de productividad de cada miembro de su equipo.
    Una tarjeta por empleado con barra de eficiencia.
    """
    limpiar(area)
    titulo(area, "📈  Reporte de Productividad del Turno")

    sup_obj = auth_sys.usuarios.get(usuario)
    area_txt = getattr(sup_obj, "area_asignada", "Sin área") if sup_obj else "Sin área"
    ctk.CTkLabel(area, text=f"Área: {area_txt}",
                 font=("Consolas", 12), text_color=C_AZUL_H
                 ).pack(anchor="w", padx=28, pady=(0, 12))

    empleados = auth_sys.por_rol("empleado")
    if not empleados:
        ctk.CTkLabel(area, text="No hay empleados registrados.",
                     text_color=C_TEXTO_SUB, font=("Consolas", 12)).pack(padx=28, pady=20)
        return

    scroll = ctk.CTkScrollableFrame(area, fg_color=C_FONDO)
    scroll.pack(fill="both", expand=True, padx=28, pady=6)

    for emp in empleados:
        rpt   = ReporteDesempeno(emp.nombre_usuario)
        boleta = rpt.generar_boleta_empleado(tareas_sys)
        efic   = boleta["eficiencia_%"]
        color  = C_VERDE_H if efic >= 70 else (C_AMBAR_H if efic >= 40 else C_ROJO_H)

        card = ctk.CTkFrame(scroll, fg_color=C_PANEL, corner_radius=10,
                             border_width=1, border_color=C_BORDE)
        card.pack(fill="x", pady=5)

        cab = ctk.CTkFrame(card, fg_color=C_AZUL, corner_radius=6, height=32)
        cab.pack(fill="x", padx=2, pady=2)
        cab.pack_propagate(False)
        ctk.CTkLabel(cab,
                     text=f"  👤 {emp.nombre_usuario}  |  {getattr(emp,'puesto','Empleado')}",
                     font=("Consolas", 12, "bold"), text_color="white"
                     ).pack(side="left", padx=12, pady=5)
        ctk.CTkLabel(cab,
                     text=f"Calificación: {boleta['calificacion']:.1f}/10",
                     font=("Consolas", 12, "bold"), text_color=color
                     ).pack(side="right", padx=14)

        cuerpo = ctk.CTkFrame(card, fg_color="transparent")
        cuerpo.pack(fill="x", padx=18, pady=8)
        mets = [
            ("Total Tareas",  boleta["total"],       C_TEXTO),
            ("Completadas",   boleta["completadas"], C_VERDE_H),
            ("En Curso",      boleta["en_curso"],    C_AZUL_H),
            ("Pendientes",    boleta["pendientes"],  C_AMBAR_H),
            ("Eficiencia",    f"{efic}%",            color),
        ]
        for i, (lbl, val, c) in enumerate(mets):
            ctk.CTkLabel(cuerpo, text=lbl, font=("Consolas", 9),
                         text_color=C_TEXTO_SUB).grid(row=0, column=i, padx=16)
            ctk.CTkLabel(cuerpo, text=str(val), font=("Consolas", 18, "bold"),
                         text_color=c).grid(row=1, column=i, padx=16, pady=2)


# ═════════════════════════════════════════════════════════════════════════════
# PANEL: EMPLEADO
# ═════════════════════════════════════════════════════════════════════════════

def mostrar_panel_empleado(ventana, usuario: str) -> None:
    """Panel operativo. Según el puesto muestra el módulo de ventas o sólo tareas."""
    ventana.title(f"Jefe en Línea — Empleado  |  {usuario}")
    emp_obj = auth_sys.usuarios.get(usuario)
    puesto  = getattr(emp_obj, "puesto", "General") if emp_obj else "General"

    secciones = [
        ("📋  Mis Tareas",       lambda: sec_mis_tareas(area, usuario)),
        ("✅  Asistencia",       lambda: sec_asistencia(area, usuario)),
        ("📩  Reporte Incidencia",lambda: sec_reporte_incidencia(area, usuario)),
        ("✉️  Mis Mensajes",     lambda: sec_mensajes(area, usuario)),
    ]
    # Los vendedores y cajeros tienen acceso al módulo de ventas
    if puesto in ("Vendedor", "Cajero"):
        secciones.insert(1, ("🛒  Registrar Venta", lambda: sec_ventas_empleado(area, usuario)))

    area = _construir_layout(ventana, usuario, secciones,
                              subtitulo=f"— {puesto}")
    sec_mis_tareas(area, usuario)


def sec_mis_tareas(area, usuario: str) -> None:
    """El empleado ve y actualiza sus propias tareas."""
    limpiar(area)
    estilo_tabla()
    titulo(area, "📋  Mis Tareas Asignadas")

    cols = ("id","titulo","desc","prio","estado","ini","fin","fecha","venc")
    tabla = ttk.Treeview(area, columns=cols, show="headings", height=15)
    for col, ancho, lbl in [
        ("id",    60,"ID"), ("titulo",180,"Título"), ("desc",200,"Descripción"),
        ("prio",  60,"Prio."),("estado",100,"Estado"),
        ("ini",   70,"Inicio"),("fin",70,"Fin"),
        ("fecha",100,"Fecha"),("venc",70,"Vencida"),
    ]:
        tabla.heading(col, text=lbl)
        tabla.column(col, width=ancho)
    tabla.pack(padx=28, pady=8, fill="both", expand=True)
    tabla.tag_configure("vencida",    background="#3d0000", foreground="#f85149")
    tabla.tag_configure("completada", background="#0d2818", foreground="#2ea043")
    tabla.tag_configure("en_curso",   background="#0d1f3c", foreground="#388bfd")

    def actualizar():
        for item in tabla.get_children():
            tabla.delete(item)
        for t in tareas_sys.tareas_de(usuario):
            venc = "Sí" if t.verificar_plazo() else "No"
            tag  = ("vencida" if venc == "Sí"
                    else "completada" if t.estado == "Completado"
                    else "en_curso"   if t.estado == "En curso"
                    else "")
            tabla.insert("", "end",
                         values=(t.id_tarea, t.titulo, t.descripcion,
                                 t.prioridad, t.estado,
                                 t.hora_inicio, t.hora_fin, t.fecha, venc),
                         tags=(tag,))

    def actualizar_estado():
        sel = tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona una tarea.")
            return
        id_t = tabla.item(sel[0])["values"][0]
        dlg  = ctk.CTkToplevel()
        dlg.title("Mi progreso")
        dlg.geometry("300x170")
        dlg.grab_set()
        ctk.CTkLabel(dlg, text="Nuevo estado:",
                     font=("Consolas", 13, "bold")).pack(pady=14)
        combo = ctk.CTkComboBox(dlg,
                                 values=["Pendiente","En curso","Revisión","Completado"],
                                 width=240)
        combo.pack(pady=8)
        def aplicar():
            tareas_sys.actualizar_estado(str(id_t), combo.get())
            actualizar()
            dlg.destroy()
        ctk.CTkButton(dlg, text="Guardar", fg_color=C_VERDE,
                      command=aplicar).pack(pady=8)

    ctk.CTkButton(area, text="Actualizar Mi Estado",
                  fg_color=C_AZUL, hover_color=C_AZUL_H,
                  font=("Consolas", 13, "bold"),
                  command=actualizar_estado).pack(pady=8)

    actualizar()


def sec_asistencia(area, usuario: str) -> None:
    """Reloj checador con registro de entrada y salida."""
    limpiar(area)
    titulo(area, "✅  Marcar Asistencia")

    emp_obj = auth_sys.usuarios.get(usuario)
    ctk.CTkLabel(area,
                 text=f"Empleado: {getattr(emp_obj,'nombre_real',usuario)}  "
                      f"|  Puesto: {getattr(emp_obj,'puesto','—')}",
                 font=("Consolas", 12), text_color=C_TEXTO_SUB
                 ).pack(anchor="w", padx=28, pady=(0, 10))

    marco = ctk.CTkFrame(area, fg_color=C_PANEL, corner_radius=16,
                          border_width=1, border_color=C_BORDE)
    marco.pack(padx=28, pady=20)

    lbl_hora = ctk.CTkLabel(marco, text="",
                             font=("Consolas", 48, "bold"), text_color=C_AZUL_H)
    lbl_hora.pack(pady=(28, 4))
    lbl_fech = ctk.CTkLabel(marco, text="",
                             font=("Consolas", 14), text_color=C_TEXTO_SUB)
    lbl_fech.pack(pady=(0, 16))

    def tick():
        ahora = datetime.now()
        lbl_hora.configure(text=ahora.strftime("%H:%M:%S"))
        lbl_fech.configure(text=ahora.strftime("%A  %d de %B, %Y"))
        area.after(1000, tick)
    tick()

    historial = ctk.CTkScrollableFrame(marco, fg_color="#0d1117",
                                        height=120, width=440, corner_radius=8)
    historial.pack(padx=18, pady=6)
    ctk.CTkLabel(marco, text="Registros de esta sesión:",
                 font=("Consolas", 9), text_color=C_TEXTO_SUB).pack()

    frame_btns = ctk.CTkFrame(marco, fg_color="transparent")
    frame_btns.pack(pady=18)

    def registrar(tipo: str):
        emp = auth_sys.usuarios.get(usuario)
        marca = emp.marcar_asistencia(tipo) if emp else f"{tipo.upper()} — {datetime.now()}"
        ctk.CTkLabel(historial, text=f"  {marca}",
                     font=("Consolas", 11),
                     text_color=C_VERDE_H if tipo == "entrada" else C_AMBAR_H,
                     anchor="w").pack(anchor="w", padx=8, pady=2)

    ctk.CTkButton(frame_btns, text="▶  Entrada",
                  fg_color=C_VERDE, hover_color=C_VERDE_H,
                  font=("Consolas", 14, "bold"), width=160, height=46,
                  command=lambda: registrar("entrada")).grid(row=0, column=0, padx=12)
    ctk.CTkButton(frame_btns, text="◼  Salida",
                  fg_color=C_AMBAR, hover_color=C_AMBAR_H,
                  font=("Consolas", 14, "bold"), width=160, height=46,
                  command=lambda: registrar("salida")).grid(row=0, column=1, padx=12)


def sec_ventas_empleado(area, usuario: str) -> None:
    """
    Módulo de Ventas para Vendedores y Cajeros.
    Pueden buscar productos por nombre O código (como en un supermercado),
    agregarlos al carrito y confirmar la venta.
    """
    limpiar(area)
    titulo(area, "🛒  Registrar Venta")

    carrito: dict = {}   # {id_producto: {"nombre", "precio", "cantidad"}}

    # ── Buscador de productos ─────────────────────────────────────────────────
    frame_busq = ctk.CTkFrame(area, fg_color=C_PANEL, corner_radius=10,
                               border_width=1, border_color=C_BORDE)
    frame_busq.pack(fill="x", padx=28, pady=(0, 8))

    ctk.CTkLabel(frame_busq, text="  Buscar producto (nombre o código):",
                 font=("Consolas", 11, "bold"),
                 text_color=C_AZUL_H).grid(row=0, column=0, columnspan=3,
                                            sticky="w", padx=10, pady=(8, 4))

    ent_busq = ctk.CTkEntry(frame_busq, placeholder_text="Ej: Refresco  ó  INV_5",
                             width=300)
    ent_busq.grid(row=1, column=0, padx=10, pady=8)

    ent_cant = ctk.CTkEntry(frame_busq, placeholder_text="Cantidad", width=80)
    ent_cant.grid(row=1, column=1, padx=6, pady=8)

    lbl_res = ctk.CTkLabel(frame_busq, text="", font=("Consolas", 10),
                            text_color=C_TEXTO_SUB)
    lbl_res.grid(row=2, column=0, columnspan=3, padx=10, sticky="w")

    # ── Panel de carrito ──────────────────────────────────────────────────────
    frame_der = ctk.CTkFrame(area, fg_color="transparent")
    frame_der.pack(fill="both", expand=True, padx=28, pady=4)

    # Resultados de búsqueda (izquierda)
    frame_resultados = ctk.CTkFrame(frame_der, fg_color=C_PANEL,
                                     corner_radius=10, border_width=1,
                                     border_color=C_BORDE)
    frame_resultados.pack(side="left", fill="both", expand=True, padx=(0, 6))
    ctk.CTkLabel(frame_resultados, text="Resultados de búsqueda",
                 font=("Consolas", 11, "bold"),
                 text_color=C_TEXTO_SUB).pack(anchor="w", padx=12, pady=(8, 0))

    estilo_tabla()
    cols_r = ("id","nombre","categoria","precio","stock")
    tabla_r = ttk.Treeview(frame_resultados, columns=cols_r,
                            show="headings", height=8)
    for col, ancho, lbl in [("id",70,"ID"),("nombre",160,"Nombre"),
                              ("categoria",100,"Cat."),
                              ("precio",80,"Precio"),("stock",70,"Stock")]:
        tabla_r.heading(col, text=lbl)
        tabla_r.column(col, width=ancho)
    tabla_r.pack(fill="both", expand=True, padx=8, pady=6)

    def buscar(event=None):
        termino = ent_busq.get().strip()
        for item in tabla_r.get_children():
            tabla_r.delete(item)
        resultados = inventario_sys.buscar_por_nombre_o_codigo(termino)
        for p in resultados:
            tabla_r.insert("", "end",
                           values=(p.id_producto, p.nombre, p.categoria,
                                   f"${p.precio_venta:.2f}", p.cantidad_stock))
        lbl_res.configure(text=f"{len(resultados)} resultado(s)")

    ent_busq.bind("<Return>", buscar)
    ctk.CTkButton(frame_busq, text="🔍 Buscar",
                  fg_color=C_AZUL, hover_color=C_AZUL_H,
                  font=("Consolas", 11, "bold"),
                  command=buscar).grid(row=1, column=2, padx=8)

    # Carrito (derecha)
    frame_cart = ctk.CTkFrame(frame_der, fg_color=C_PANEL,
                               corner_radius=10, border_width=1,
                               border_color=C_BORDE, width=310)
    frame_cart.pack(side="right", fill="y", padx=(6, 0))
    frame_cart.pack_propagate(False)

    ctk.CTkLabel(frame_cart, text="🛒  Carrito",
                 font=("Consolas", 14, "bold"),
                 text_color=C_AMBAR_H).pack(pady=(12, 4))

    scroll_cart = ctk.CTkScrollableFrame(frame_cart, fg_color="#0d1117",
                                          corner_radius=8)
    scroll_cart.pack(fill="both", expand=True, padx=10, pady=4)

    lbl_total = ctk.CTkLabel(frame_cart, text="Total: $0.00",
                              font=("Consolas", 16, "bold"),
                              text_color=C_VERDE_H)
    lbl_total.pack(pady=6)

    def refrescar_carrito():
        for w in scroll_cart.winfo_children():
            w.destroy()
        total = 0.0
        for pid, it in carrito.items():
            total += it["precio"] * it["cantidad"]
            fr = ctk.CTkFrame(scroll_cart, fg_color="#1e293b", corner_radius=6)
            fr.pack(fill="x", pady=2, padx=4)
            ctk.CTkLabel(fr, text=f"{it['nombre']}",
                         font=("Consolas", 10, "bold"), anchor="w",
                         wraplength=180).grid(row=0, column=0, columnspan=4,
                                              padx=6, pady=(4, 0), sticky="w")
            ctk.CTkLabel(fr, text=f"x{it['cantidad']}  ${it['precio']*it['cantidad']:.2f}",
                         font=("Consolas", 10), text_color=C_VERDE_H
                         ).grid(row=1, column=0, padx=6, pady=(0, 4), sticky="w")

            def quitar(p=pid):
                if carrito[p]["cantidad"] > 1:
                    carrito[p]["cantidad"] -= 1
                else:
                    del carrito[p]
                refrescar_carrito()

            ctk.CTkButton(fr, text="−", width=26, height=22,
                           fg_color=C_ROJO, font=("Consolas", 11, "bold"),
                           command=quitar).grid(row=1, column=2, padx=3, pady=(0,4))

        lbl_total.configure(text=f"Total: ${total:.2f}")

    def agregar_al_carrito():
        sel = tabla_r.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un producto.")
            return
        try:
            cant = int(ent_cant.get()) if ent_cant.get() else 1
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            return

        vals = tabla_r.item(sel[0])["values"]
        pid   = str(vals[0])
        prod  = inventario_sys.productos.get(pid)
        if not prod or prod.cantidad_stock < cant:
            messagebox.showwarning("Sin Stock", f"Stock insuficiente para '{vals[1]}'.")
            return
        if pid in carrito:
            carrito[pid]["cantidad"] += cant
        else:
            carrito[pid] = {"nombre": vals[1], "precio": prod.precio_venta, "cantidad": cant}
        refrescar_carrito()

    def confirmar_venta():
        if not carrito:
            messagebox.showwarning("Carrito vacío", "Agrega al menos un producto.")
            return
        items = [{"id_producto": pid, "nombre": it["nombre"],
                  "cantidad": it["cantidad"],
                  "subtotal": it["precio"] * it["cantidad"]}
                 for pid, it in carrito.items()]
        total = sum(i["subtotal"] for i in items)

        if messagebox.askyesno("Confirmar Venta",
                                f"Total a cobrar: ${total:.2f} MXN\n¿Confirmar?"):
            ventas_prod_sys.registrar_venta(usuario, items, inventario_sys)
            # También registramos en finanzas como ingreso
            finanzas_sys.registrar_movimiento(
                total, "Venta", "Efectivo",
                f"Venta registrada por {usuario}", usuario
            )
            carrito.clear()
            refrescar_carrito()
            messagebox.showinfo("Venta Exitosa",
                                f"Venta guardada. Total: ${total:.2f} MXN")

    ctk.CTkButton(frame_busq, text="+ Agregar al Carrito",
                  fg_color=C_VERDE, hover_color=C_VERDE_H,
                  font=("Consolas", 11, "bold"),
                  command=agregar_al_carrito).grid(row=1, column=3, padx=8)

    ctk.CTkButton(frame_cart, text="✔  Confirmar Venta",
                  fg_color=C_VERDE, hover_color=C_VERDE_H,
                  font=("Consolas", 13, "bold"), width=260, height=44,
                  command=confirmar_venta).pack(pady=(0, 6))

    ctk.CTkButton(frame_cart, text="Vaciar Carrito",
                  fg_color="#334155", hover_color="#475569",
                  font=("Consolas", 11), width=260, height=34,
                  command=lambda: [carrito.clear(), refrescar_carrito()]
                  ).pack(pady=(0, 12))

    # Cargar todos los productos al iniciar
    for p in inventario_sys.productos.values():
        tabla_r.insert("", "end",
                       values=(p.id_producto, p.nombre, p.categoria,
                               f"${p.precio_venta:.2f}", p.cantidad_stock))


def sec_reporte_incidencia(area, usuario: str) -> None:
    """
    Formulario para reportar incidencias.
    Si el nivel es 'Grave', el mensaje va directo al Jefe.
    """
    limpiar(area)
    titulo(area, "📩  Reportar Incidencia")

    marco = ctk.CTkFrame(area, fg_color=C_PANEL, corner_radius=14,
                          border_width=1, border_color=C_BORDE)
    marco.pack(padx=28, pady=20, fill="x")

    ctk.CTkLabel(marco, text="Tipo de incidencia:",
                 font=("Consolas", 12, "bold"),
                 text_color=C_TEXTO_SUB).pack(anchor="w", padx=18, pady=(14, 4))
    combo_tipo = ctk.CTkComboBox(marco,
                                  values=["Falta de material","Equipo dañado",
                                          "Conflicto personal","Retraso proveedor",
                                          "Problema de seguridad","Otro"],
                                  width=300)
    combo_tipo.pack(anchor="w", padx=18, pady=4)

    ctk.CTkLabel(marco, text="Nivel de gravedad:",
                 font=("Consolas", 12, "bold"),
                 text_color=C_TEXTO_SUB).pack(anchor="w", padx=18, pady=(10, 4))
    combo_nivel = ctk.CTkComboBox(marco,
                                   values=["Normal","Moderado","Grave"],
                                   width=200)
    combo_nivel.set("Normal")
    combo_nivel.pack(anchor="w", padx=18, pady=4)

    ctk.CTkLabel(marco, text="Descripción:",
                 font=("Consolas", 12, "bold"),
                 text_color=C_TEXTO_SUB).pack(anchor="w", padx=18, pady=(10, 4))
    txt = ctk.CTkTextbox(marco, height=120, width=560,
                          font=("Consolas", 12), wrap="word")
    txt.pack(padx=18, pady=4)

    lbl_conf = ctk.CTkLabel(marco, text="", font=("Consolas", 11))
    lbl_conf.pack(pady=6)

    def enviar():
        tipo  = combo_tipo.get()
        nivel = combo_nivel.get()
        desc  = txt.get("0.0", "end").strip()
        if not desc:
            messagebox.showwarning("Atención", "Escribe la descripción antes de enviar.")
            return

        jefes = [u.nombre_usuario for u in auth_sys.por_rol("jefe")]
        sups  = [u.nombre_usuario for u in auth_sys.por_rol("supervisor")]

        emp_obj = auth_sys.usuarios.get(usuario)
        if emp_obj and hasattr(emp_obj, "enviar_reporte_incidencia"):
            emp_obj.enviar_reporte_incidencia(nivel, desc,
                                               mensajes_sys, sups, jefes)
        else:
            destino = jefes[0] if (nivel == "Grave" and jefes) else (sups[0] if sups else "admin")
            mensajes_sys.enviar_mensaje(usuario, destino,
                                         f"[{nivel}] {tipo}", desc)
        txt.delete("0.0", "end")
        lbl_conf.configure(text="✔  Reporte enviado correctamente.",
                           text_color=C_VERDE_H)

    ctk.CTkButton(marco, text="Enviar Reporte",
                  fg_color=C_AZUL, hover_color=C_AZUL_H,
                  font=("Consolas", 14, "bold"), width=220, height=42,
                  command=enviar).pack(pady=(4, 18))


# ═════════════════════════════════════════════════════════════════════════════
# SECCIONES COMPARTIDAS (usadas por varios roles)
# ═════════════════════════════════════════════════════════════════════════════

def sec_tareas(area, usuario: str, puede_crear: bool = False) -> None:
    """Vista completa de tareas. El Gerente puede crear; el Jefe solo visualiza."""
    limpiar(area)
    estilo_tabla()
    titulo(area, "📋  Gestión de Tareas")

    if puede_crear:
        frame_form = ctk.CTkFrame(area, fg_color=C_PANEL, corner_radius=10,
                                   border_width=1, border_color=C_BORDE)
        frame_form.pack(fill="x", padx=28, pady=(0, 8))

        ctk.CTkLabel(frame_form, text="  Nueva Tarea",
                     font=("Consolas", 11, "bold"),
                     text_color=C_AZUL_H).grid(row=0, column=0, columnspan=8,
                                                sticky="w", padx=10, pady=(8, 4))

        empleados_n = [u.nombre_usuario for u in auth_sys.por_rol("empleado")] or ["(sin empleados)"]
        ent_tit  = ctk.CTkEntry(frame_form, placeholder_text="Título",     width=160)
        ent_desc = ctk.CTkEntry(frame_form, placeholder_text="Descripción",width=160)
        cb_emp   = ctk.CTkComboBox(frame_form, values=empleados_n,         width=130)
        cb_prio  = ctk.CTkComboBox(frame_form, values=["1","2","3","4","5"],width=60)
        cb_prio.set("3")
        ent_ini  = ctk.CTkEntry(frame_form, placeholder_text="HH:MM ini",  width=80)
        ent_fin  = ctk.CTkEntry(frame_form, placeholder_text="HH:MM fin",  width=80)
        ent_fech = ctk.CTkEntry(frame_form, placeholder_text="AAAA-MM-DD", width=110)

        for i, (lbl, w) in enumerate(zip(
            ["Título","Descripción","Asignar a","Prio.","H.Inicio","H.Fin","Fecha"],
            [ent_tit, ent_desc, cb_emp, cb_prio, ent_ini, ent_fin, ent_fech]
        )):
            ctk.CTkLabel(frame_form, text=lbl, font=("Consolas", 9),
                         text_color=C_TEXTO_SUB).grid(row=1, column=i, padx=6)
            w.grid(row=2, column=i, padx=6, pady=6)

        def guardar():
            t, desc = ent_tit.get().strip(), ent_desc.get().strip()
            emp, ini, fin = cb_emp.get(), ent_ini.get().strip(), ent_fin.get().strip()
            fech = ent_fech.get().strip()
            if not all([t, emp, ini, fin, fech]):
                messagebox.showwarning("Atención", "Completa todos los campos obligatorios.")
                return
            _, col = tareas_sys.crear_tarea(t, desc, int(cb_prio.get()),
                                             emp, ini, fin, usuario, fech)
            if col:
                messagebox.showwarning("⚡ Colisión",
                                       f"Tarea creada con {len(col)} colisión(es) horaria(s).")
            tabla_act()
            for w in [ent_tit, ent_desc, ent_ini, ent_fin, ent_fech]:
                w.delete(0, "end")

        ctk.CTkButton(frame_form, text="Crear",
                      fg_color=C_VERDE, hover_color=C_VERDE_H,
                      font=("Consolas", 11, "bold"),
                      command=guardar).grid(row=2, column=7, padx=10)

    cols = ("id","titulo","asig","prio","estado","ini","fin","fecha","venc")
    tabla = ttk.Treeview(area, columns=cols, show="headings", height=13)
    for col, ancho, lbl in [
        ("id",60,"ID"),("titulo",180,"Título"),("asig",130,"Asignado a"),
        ("prio",60,"Prio."),("estado",100,"Estado"),
        ("ini",70,"Inicio"),("fin",70,"Fin"),("fecha",100,"Fecha"),("venc",70,"Vencida"),
    ]:
        tabla.heading(col, text=lbl)
        tabla.column(col, width=ancho)
    tabla.pack(padx=28, pady=4, fill="both", expand=True)
    tabla.tag_configure("vencida",    background="#3d0000", foreground="#f85149")
    tabla.tag_configure("completada", background="#0d2818", foreground="#2ea043")
    tabla.tag_configure("en_curso",   background="#0d1f3c", foreground="#388bfd")

    def tabla_act():
        for item in tabla.get_children():
            tabla.delete(item)
        for t in tareas_sys.tareas:
            venc = "Sí" if t.verificar_plazo() else "No"
            tag  = ("vencida" if venc=="Sí" else
                    "completada" if t.estado=="Completado" else
                    "en_curso"   if t.estado=="En curso" else "")
            tabla.insert("", "end",
                         values=(t.id_tarea, t.titulo, t.asignado_a,
                                 t.prioridad, t.estado,
                                 t.hora_inicio, t.hora_fin, t.fecha, venc),
                         tags=(tag,))

    frame_acc = ctk.CTkFrame(area, fg_color="transparent")
    frame_acc.pack(padx=28, pady=(0, 8))

    def cambiar_estado():
        sel = tabla.selection()
        if not sel:
            return
        id_t = tabla.item(sel[0])["values"][0]
        dlg = ctk.CTkToplevel()
        dlg.title("Cambiar Estado")
        dlg.geometry("300x170")
        dlg.grab_set()
        ctk.CTkLabel(dlg, text=f"Estado de {id_t}", font=("Consolas", 13, "bold")).pack(pady=14)
        combo = ctk.CTkComboBox(dlg, values=["Pendiente","En curso","Revisión","Completado"], width=240)
        combo.pack(pady=8)
        def ap():
            tareas_sys.actualizar_estado(str(id_t), combo.get())
            tabla_act()
            dlg.destroy()
        ctk.CTkButton(dlg, text="Aplicar", fg_color=C_AZUL, command=ap).pack(pady=8)

    def eliminar():
        sel = tabla.selection()
        if not sel:
            return
        id_t = tabla.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar tarea {id_t}?"):
            tareas_sys.eliminar_tarea(str(id_t))
            tabla_act()

    ctk.CTkButton(frame_acc, text="Cambiar Estado",
                  fg_color=C_AMBAR, hover_color=C_AMBAR_H,
                  font=("Consolas", 11, "bold"),
                  command=cambiar_estado).grid(row=0, column=0, padx=8)
    ctk.CTkButton(frame_acc, text="Eliminar",
                  fg_color=C_ROJO, hover_color=C_ROJO_H,
                  font=("Consolas", 11, "bold"),
                  command=eliminar).grid(row=0, column=1, padx=8)

    tabla_act()


def sec_inventario(area, usuario: str) -> None:
    """Gestión de inventario: alta, edición de stock y lista de compras."""
    limpiar(area)
    estilo_tabla()
    titulo(area, "📦  Gestión de Inventario")

    frame_form = ctk.CTkFrame(area, fg_color=C_PANEL, corner_radius=10,
                               border_width=1, border_color=C_BORDE)
    frame_form.pack(fill="x", padx=28, pady=(0, 8))
    ctk.CTkLabel(frame_form, text="  Registrar Producto",
                 font=("Consolas", 11, "bold"),
                 text_color=C_AZUL_H).grid(row=0, column=0, columnspan=7,
                                            sticky="w", padx=10, pady=(8, 4))

    ent_nom   = ctk.CTkEntry(frame_form, placeholder_text="Nombre",     width=160)
    cb_cat    = ctk.CTkComboBox(frame_form,
                                 values=["Insumos","Equipos","Papelería",
                                         "Limpieza","Alimentos","Otro"],
                                 width=120)
    ent_costo = ctk.CTkEntry(frame_form, placeholder_text="$Costo",     width=90)
    ent_pvta  = ctk.CTkEntry(frame_form, placeholder_text="$P.Venta",   width=90)
    ent_stk   = ctk.CTkEntry(frame_form, placeholder_text="Stock",      width=70)
    ent_preo  = ctk.CTkEntry(frame_form, placeholder_text="P.Reorden",  width=80)

    for i, (lbl, w) in enumerate(zip(
        ["Nombre","Categoría","Costo","P.Venta","Stock","P.Reorden"],
        [ent_nom, cb_cat, ent_costo, ent_pvta, ent_stk, ent_preo]
    )):
        ctk.CTkLabel(frame_form, text=lbl, font=("Consolas", 9),
                     text_color=C_TEXTO_SUB).grid(row=1, column=i, padx=6)
        w.grid(row=2, column=i, padx=6, pady=6)

    cols = ("id","nombre","cat","costo","pventa","stock","reorden","estado")
    tabla = ttk.Treeview(area, columns=cols, show="headings", height=11)
    for col, ancho, lbl in [
        ("id",70,"ID"),("nombre",180,"Nombre"),("cat",100,"Categoría"),
        ("costo",90,"Costo"),("pventa",90,"P.Venta"),
        ("stock",70,"Stock"),("reorden",90,"P.Reorden"),("estado",110,"Estado"),
    ]:
        tabla.heading(col, text=lbl)
        tabla.column(col, width=ancho)
    tabla.pack(padx=28, pady=4, fill="both", expand=True)
    tabla.tag_configure("bajo",    background="#3d2200", foreground="#d29922")
    tabla.tag_configure("agotado", background="#3d0000", foreground="#f85149")
    tabla.tag_configure("ok",      background="#0d2818", foreground="#2ea043")

    def tabla_act():
        for item in tabla.get_children():
            tabla.delete(item)
        for p in inventario_sys.productos.values():
            if p.cantidad_stock == 0:
                tag, est = "agotado", "⛔ AGOTADO"
            elif p.cantidad_stock <= p.punto_reorden:
                tag, est = "bajo", "⚠ Stock Bajo"
            else:
                tag, est = "ok", "✔ OK"
            tabla.insert("", "end",
                         values=(p.id_producto, p.nombre, p.categoria,
                                 f"${p.costo_compra:.2f}", f"${p.precio_venta:.2f}",
                                 p.cantidad_stock, p.punto_reorden, est),
                         tags=(tag,))

    def guardar_prod():
        n = ent_nom.get().strip()
        if not n:
            messagebox.showwarning("Atención", "El nombre es obligatorio.")
            return
        try:
            inventario_sys.registrar_producto(
                n, cb_cat.get(),
                float(ent_costo.get() or 0),
                float(ent_pvta.get()  or 0),
                int(ent_stk.get()    or 0),
                int(ent_preo.get()   or 5),
            )
            tabla_act()
            for w in [ent_nom, ent_costo, ent_pvta, ent_stk, ent_preo]:
                w.delete(0, "end")
        except ValueError:
            messagebox.showerror("Error", "Costo, precio y stock deben ser números.")

    ctk.CTkButton(frame_form, text="Registrar",
                  fg_color=C_VERDE, hover_color=C_VERDE_H,
                  font=("Consolas", 11, "bold"),
                  command=guardar_prod).grid(row=2, column=6, padx=10)

    frame_acc = ctk.CTkFrame(area, fg_color="transparent")
    frame_acc.pack(padx=28, pady=(0, 8))

    def ajustar():
        sel = tabla.selection()
        if not sel:
            return
        id_p = tabla.item(sel[0])["values"][0]
        prod = inventario_sys.productos.get(id_p)
        dlg = ctk.CTkToplevel()
        dlg.title("Ajustar Stock")
        dlg.geometry("300x190")
        dlg.grab_set()
        ctk.CTkLabel(dlg, text=f"{prod.nombre}",
                     font=("Consolas", 13, "bold")).pack(pady=14)
        ctk.CTkLabel(dlg, text=f"Stock actual: {prod.cantidad_stock}",
                     font=("Consolas", 12), text_color=C_AZUL_H).pack()
        ent_aj = ctk.CTkEntry(dlg, placeholder_text="Ej: +50 ó -10", width=200)
        ent_aj.pack(pady=8)
        def ap():
            try:
                prod.ajustar_stock(int(ent_aj.get()))
                inventario_sys._guardar_completo()
                tabla_act()
                dlg.destroy()
            except ValueError:
                messagebox.showerror("Error", "Ingresa un número entero.")
        ctk.CTkButton(dlg, text="Aplicar", fg_color=C_AZUL, command=ap).pack(pady=8)

    def lista_compras():
        lst = inventario_sys.generar_lista_compras()
        dlg = ctk.CTkToplevel()
        dlg.title("Lista de Compras")
        dlg.geometry("400x320")
        dlg.grab_set()
        ctk.CTkLabel(dlg, text="🛒  Productos a Reabastecer",
                     font=("Consolas", 14, "bold"),
                     text_color=C_AMBAR_H).pack(pady=14)
        if not lst:
            ctk.CTkLabel(dlg, text="✔ Todo en nivel óptimo.",
                         text_color=C_VERDE_H, font=("Consolas", 12)).pack()
        else:
            sc = ctk.CTkScrollableFrame(dlg, fg_color=C_PANEL)
            sc.pack(fill="both", expand=True, padx=14, pady=8)
            for p in lst:
                ctk.CTkLabel(sc,
                             text=f"  • {p.nombre}  |  Stock: {p.cantidad_stock}  |  Mín: {p.punto_reorden}",
                             font=("Consolas", 11), text_color=C_AMBAR_H,
                             anchor="w").pack(anchor="w", pady=2)

    def eliminar_prod():
        sel = tabla.selection()
        if not sel:
            return
        id_p = str(tabla.item(sel[0])["values"][0])
        nom  = tabla.item(sel[0])["values"][1]
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{nom}'?"):
            inventario_sys.eliminar_producto(id_p)
            tabla_act()

    ctk.CTkButton(frame_acc, text="Ajustar Stock",
                  fg_color=C_AZUL, hover_color=C_AZUL_H,
                  font=("Consolas", 11, "bold"), command=ajustar
                  ).grid(row=0, column=0, padx=8)
    ctk.CTkButton(frame_acc, text="Lista de Compras",
                  fg_color=C_AMBAR, hover_color=C_AMBAR_H,
                  font=("Consolas", 11, "bold"), command=lista_compras
                  ).grid(row=0, column=1, padx=8)
    ctk.CTkButton(frame_acc, text="Eliminar",
                  fg_color=C_ROJO, hover_color=C_ROJO_H,
                  font=("Consolas", 11, "bold"), command=eliminar_prod
                  ).grid(row=0, column=2, padx=8)

    tabla_act()


def sec_finanzas(area, usuario: str) -> None:
    """Registro y vista de todos los movimientos de dinero."""
    limpiar(area)
    estilo_tabla()
    titulo(area, "💰  Registro Financiero")

    # Resumen rápido
    frame_res = ctk.CTkFrame(area, fg_color=C_PANEL, corner_radius=10,
                              border_width=1, border_color=C_BORDE)
    frame_res.pack(fill="x", padx=28, pady=(0, 8))
    for i, (lbl, val, color) in enumerate([
        ("Ventas Hoy",  f"${finanzas_sys.obtener_total_ventas('diario'):,.2f}",  C_VERDE),
        ("Ventas Mes",  f"${finanzas_sys.obtener_total_ventas('mensual'):,.2f}", C_AZUL),
        ("Utilidad",    f"${finanzas_sys.calcular_utilidad_neta():,.2f}",        C_AMBAR_H),
    ]):
        ctk.CTkLabel(frame_res, text=lbl, font=("Consolas", 10),
                     text_color=C_TEXTO_SUB).grid(row=0, column=i*2, padx=30, pady=6)
        ctk.CTkLabel(frame_res, text=val, font=("Consolas", 20, "bold"),
                     text_color=color).grid(row=1, column=i*2, padx=30, pady=(0, 12))
        if i < 2:
            ctk.CTkFrame(frame_res, width=1, height=50,
                         fg_color=C_BORDE).grid(row=0, column=i*2+1, rowspan=2, pady=8)

    # Formulario
    frame_form = ctk.CTkFrame(area, fg_color=C_PANEL, corner_radius=10,
                               border_width=1, border_color=C_BORDE)
    frame_form.pack(fill="x", padx=28, pady=(0, 8))
    ctk.CTkLabel(frame_form, text="  Registrar Movimiento",
                 font=("Consolas", 11, "bold"),
                 text_color=C_AZUL_H).grid(row=0, column=0, columnspan=6,
                                            sticky="w", padx=10, pady=(8, 4))

    ent_monto = ctk.CTkEntry(frame_form, placeholder_text="Monto (+/-)", width=160)
    cb_cat    = ctk.CTkComboBox(frame_form,
                                 values=["Venta","Gasto Fijo","Insumos","Sueldos","Otro"],
                                 width=130)
    cb_pago   = ctk.CTkComboBox(frame_form,
                                 values=["Efectivo","Tarjeta","Transferencia"],
                                 width=130)
    ent_desc  = ctk.CTkEntry(frame_form, placeholder_text="Descripción", width=200)

    for i, (lbl, w) in enumerate(zip(
        ["Monto","Categoría","Método Pago","Descripción"],
        [ent_monto, cb_cat, cb_pago, ent_desc]
    )):
        ctk.CTkLabel(frame_form, text=lbl, font=("Consolas", 9),
                     text_color=C_TEXTO_SUB).grid(row=1, column=i, padx=8)
        w.grid(row=2, column=i, padx=8, pady=6)

    cols = ("id","monto","cat","pago","desc","fecha","anulado")
    tabla = ttk.Treeview(area, columns=cols, show="headings", height=9)
    for col, ancho, lbl in [
        ("id",80,"ID"),("monto",100,"Monto"),("cat",100,"Categoría"),
        ("pago",110,"Método"),("desc",200,"Descripción"),
        ("fecha",150,"Fecha/Hora"),("anulado",70,"Anulado"),
    ]:
        tabla.heading(col, text=lbl)
        tabla.column(col, width=ancho)
    tabla.pack(padx=28, pady=4, fill="both", expand=True)
    tabla.tag_configure("anulado", foreground="#6e7681")
    tabla.tag_configure("gasto",   foreground="#f85149")
    tabla.tag_configure("venta",   foreground="#2ea043")

    def tabla_act():
        for item in tabla.get_children():
            tabla.delete(item)
        for m in reversed(finanzas_sys.movimientos):
            tag = "anulado" if m.anulado else ("gasto" if m.monto < 0 else "venta")
            tabla.insert("", "end",
                         values=(m.id_trans, f"${m.monto:,.2f}", m.categoria,
                                 m.metodo_pago, m.descripcion, m.fecha_hora,
                                 "Sí" if m.anulado else ""),
                         tags=(tag,))

    frame_acc = ctk.CTkFrame(area, fg_color="transparent")
    frame_acc.pack(padx=28, pady=(0, 8))

    def guardar():
        try:
            monto = float(ent_monto.get())
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número.")
            return
        finanzas_sys.registrar_movimiento(monto, cb_cat.get(), cb_pago.get(),
                                           ent_desc.get().strip() or "—", usuario)
        tabla_act()
        ent_monto.delete(0, "end")
        ent_desc.delete(0, "end")

    def anular():
        sel = tabla.selection()
        if not sel:
            return
        id_m = tabla.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Anular {id_m}?"):
            finanzas_sys.anular_transaccion(id_m)
            tabla_act()

    ctk.CTkButton(frame_form, text="Registrar",
                  fg_color=C_VERDE, hover_color=C_VERDE_H,
                  font=("Consolas", 11, "bold"),
                  command=guardar).grid(row=2, column=4, padx=12)
    ctk.CTkButton(frame_acc, text="Anular Seleccionado",
                  fg_color=C_ROJO, hover_color=C_ROJO_H,
                  font=("Consolas", 11, "bold"),
                  command=anular).grid(row=0, column=0, padx=8)

    tabla_act()


def sec_mensajes(area, usuario: str) -> None:
    """Bandeja de mensajes internos compartida por todos los roles."""
    limpiar(area)
    estilo_tabla()

    no_l = mensajes_sys.no_leidos_de(usuario)
    titulo(area, f"✉️  Mensajes" + (f"  ({no_l} nuevos)" if no_l else ""))

    frame_form = ctk.CTkFrame(area, fg_color=C_PANEL, corner_radius=10,
                               border_width=1, border_color=C_BORDE)
    frame_form.pack(fill="x", padx=28, pady=(0, 8))
    ctk.CTkLabel(frame_form, text="  Enviar Mensaje",
                 font=("Consolas", 11, "bold"),
                 text_color=C_AZUL_H).grid(row=0, column=0, columnspan=4,
                                            sticky="w", padx=10, pady=(8, 4))

    # Todos pueden recibir mensajes
    todos = [u.nombre_usuario for u in auth_sys.usuarios.values()
             if u.nombre_usuario != usuario] or ["(sin usuarios)"]
    cb_dest  = ctk.CTkComboBox(frame_form, values=todos,          width=160)
    ent_asnt = ctk.CTkEntry(frame_form, placeholder_text="Asunto",  width=220)
    ent_msg  = ctk.CTkEntry(frame_form, placeholder_text="Mensaje…",width=300)

    for i, (lbl, w) in enumerate(zip(
        ["Destinatario","Asunto","Mensaje"],
        [cb_dest, ent_asnt, ent_msg]
    )):
        ctk.CTkLabel(frame_form, text=lbl, font=("Consolas", 9),
                     text_color=C_TEXTO_SUB).grid(row=1, column=i, padx=10)
        w.grid(row=2, column=i, padx=10, pady=6)

    cols = ("id","de","asunto","fecha","leido")
    tabla = ttk.Treeview(area, columns=cols, show="headings", height=11)
    for col, ancho, lbl in [
        ("id",80,"ID"),("de",140,"De"),
        ("asunto",260,"Asunto"),("fecha",160,"Fecha/Hora"),("leido",70,"Leído"),
    ]:
        tabla.heading(col, text=lbl)
        tabla.column(col, width=ancho)
    tabla.pack(padx=28, pady=4, fill="both", expand=True)
    tabla.tag_configure("nuevo", foreground="#388bfd")

    def tabla_act():
        for item in tabla.get_children():
            tabla.delete(item)
        for m in mensajes_sys.bandeja_de(usuario):
            tag = "" if m.leido else "nuevo"
            tabla.insert("", "end",
                         values=(m.id_mensaje, m.remitente, m.asunto,
                                 m.fecha_hora, "✔" if m.leido else "●"),
                         tags=(tag,))

    def leer():
        sel = tabla.selection()
        if not sel:
            return
        id_m = tabla.item(sel[0])["values"][0]
        msg  = next((m for m in mensajes_sys.mensajes if m.id_mensaje == id_m), None)
        if not msg:
            return
        mensajes_sys.marcar_leido(id_m)
        dlg = ctk.CTkToplevel()
        dlg.title(msg.asunto)
        dlg.geometry("460x290")
        dlg.grab_set()
        ctk.CTkLabel(dlg, text=msg.asunto,
                     font=("Consolas", 15, "bold"),
                     text_color=C_AZUL_H).pack(padx=18, pady=(14, 2), anchor="w")
        ctk.CTkLabel(dlg, text=f"De: {msg.remitente}  ·  {msg.fecha_hora}",
                     font=("Consolas", 10),
                     text_color=C_TEXTO_SUB).pack(padx=18, anchor="w")
        txt = ctk.CTkTextbox(dlg, height=150, wrap="word", font=("Consolas", 12))
        txt.pack(fill="both", expand=True, padx=18, pady=8)
        txt.insert("0.0", msg.cuerpo)
        txt.configure(state="disabled")
        ctk.CTkButton(dlg, text="Cerrar",
                      fg_color=C_PANEL, command=dlg.destroy).pack(pady=6)
        tabla_act()

    def enviar():
        dest  = cb_dest.get()
        asnt  = ent_asnt.get().strip()
        cuerpo= ent_msg.get().strip()
        if not asnt or not cuerpo:
            messagebox.showwarning("Atención", "Completa asunto y mensaje.")
            return
        mensajes_sys.enviar_mensaje(usuario, dest, asnt, cuerpo)
        ent_asnt.delete(0, "end")
        ent_msg.delete(0, "end")
        messagebox.showinfo("Enviado", f"Mensaje enviado a {dest}.")

    ctk.CTkButton(frame_form, text="Enviar",
                  fg_color=C_AZUL, hover_color=C_AZUL_H,
                  font=("Consolas", 11, "bold"),
                  command=enviar).grid(row=2, column=3, padx=10)

    frame_acc = ctk.CTkFrame(area, fg_color="transparent")
    frame_acc.pack(padx=28, pady=(0, 8))
    ctk.CTkButton(frame_acc, text="Leer Mensaje",
                  fg_color=C_VERDE, hover_color=C_VERDE_H,
                  font=("Consolas", 11, "bold"),
                  command=leer).grid(row=0, column=0, padx=8)

    tabla_act()


def sec_empleados(area, usuario: str) -> None:
    """Gestión de usuarios (alta, suspensión y baja). Disponible para Jefe y Gerente."""
    limpiar(area)
    estilo_tabla()
    titulo(area, "👥  Gestión de Personal")

    frame_form = ctk.CTkFrame(area, fg_color=C_PANEL, corner_radius=10,
                               border_width=1, border_color=C_BORDE)
    frame_form.pack(fill="x", padx=28, pady=(0, 8))
    ctk.CTkLabel(frame_form, text="  Registrar Usuario",
                 font=("Consolas", 11, "bold"),
                 text_color=C_AZUL_H).grid(row=0, column=0, columnspan=6,
                                            sticky="w", padx=10, pady=(8, 4))

    ent_un  = ctk.CTkEntry(frame_form, placeholder_text="Usuario (login)", width=150)
    ent_pw  = ctk.CTkEntry(frame_form, placeholder_text="Contraseña",      width=130)
    ent_nr  = ctk.CTkEntry(frame_form, placeholder_text="Nombre real",     width=170)
    cb_rol  = ctk.CTkComboBox(frame_form,
                               values=["empleado","supervisor","gerente","jefe"],
                               width=110)
    ent_pus = ctk.CTkEntry(frame_form, placeholder_text="Puesto / Área",   width=140)

    for i, (lbl, w) in enumerate(zip(
        ["Usuario","Contraseña","Nombre Real","Rol","Puesto/Área"],
        [ent_un, ent_pw, ent_nr, cb_rol, ent_pus]
    )):
        ctk.CTkLabel(frame_form, text=lbl, font=("Consolas", 9),
                     text_color=C_TEXTO_SUB).grid(row=1, column=i, padx=8)
        w.grid(row=2, column=i, padx=8, pady=6)

    cols = ("user","nombre","rol","puesto","estado")
    tabla = ttk.Treeview(area, columns=cols, show="headings", height=12)
    for col, ancho, lbl in [
        ("user",150,"Usuario"),("nombre",200,"Nombre Real"),
        ("rol",100,"Rol"),("puesto",140,"Puesto/Área"),("estado",100,"Estado"),
    ]:
        tabla.heading(col, text=lbl)
        tabla.column(col, width=ancho)
    tabla.pack(padx=28, pady=4, fill="both", expand=True)
    tabla.tag_configure("inactivo", foreground="#6e7681")

    def tabla_act():
        for item in tabla.get_children():
            tabla.delete(item)
        for u in auth_sys.usuarios.values():
            puesto = getattr(u, "puesto", getattr(u, "area_asignada", "—"))
            tabla.insert("", "end",
                         values=(u.nombre_usuario, u.nombre_real, u.rol,
                                 puesto, "Activo" if u.estado_cuenta else "Suspendido"),
                         tags=("" if u.estado_cuenta else "inactivo",))

    frame_acc = ctk.CTkFrame(area, fg_color="transparent")
    frame_acc.pack(padx=28, pady=(0, 8))

    def guardar():
        un = ent_un.get().strip()
        pw = ent_pw.get().strip()
        if not un or not pw:
            messagebox.showwarning("Atención", "Usuario y contraseña son obligatorios.")
            return
        if un in auth_sys.usuarios:
            messagebox.showerror("Error", f"El usuario '{un}' ya existe.")
            return
        auth_sys.registrar_usuario(un, pw, cb_rol.get(),
                                    ent_nr.get().strip(),
                                    ent_pus.get().strip() or "General")
        tabla_act()
        for w in [ent_un, ent_pw, ent_nr, ent_pus]:
            w.delete(0, "end")

    def toggle_estado():
        sel = tabla.selection()
        if not sel:
            return
        un = tabla.item(sel[0])["values"][0]
        u  = auth_sys.usuarios.get(un)
        if u and un != usuario:
            u.estado_cuenta = not u.estado_cuenta
            auth_sys._guardar_completo()
            tabla_act()

    def eliminar():
        sel = tabla.selection()
        if not sel:
            return
        un = tabla.item(sel[0])["values"][0]
        if un == usuario:
            messagebox.showerror("Error", "No puedes eliminarte a ti mismo.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar al usuario '{un}'?"):
            auth_sys.eliminar_usuario(un)
            tabla_act()

    ctk.CTkButton(frame_form, text="Registrar",
                  fg_color=C_VERDE, hover_color=C_VERDE_H,
                  font=("Consolas", 11, "bold"),
                  command=guardar).grid(row=2, column=5, padx=10)
    ctk.CTkButton(frame_acc, text="Suspender / Activar",
                  fg_color=C_AMBAR, hover_color=C_AMBAR_H,
                  font=("Consolas", 11, "bold"),
                  command=toggle_estado).grid(row=0, column=0, padx=8)
    ctk.CTkButton(frame_acc, text="Eliminar Usuario",
                  fg_color=C_ROJO, hover_color=C_ROJO_H,
                  font=("Consolas", 11, "bold"),
                  command=eliminar).grid(row=0, column=1, padx=8)

    tabla_act()


def sec_promociones(area, usuario: str) -> None:
    """Módulo del Gerente para planear promociones para los clientes."""
    limpiar(area)
    titulo(area, "🏷️  Gestión de Promociones")

    gerente_obj = auth_sys.usuarios.get(usuario)
    promos = getattr(gerente_obj, "promociones", []) if gerente_obj else []

    frame_form = ctk.CTkFrame(area, fg_color=C_PANEL, corner_radius=12,
                               border_width=1, border_color=C_BORDE)
    frame_form.pack(fill="x", padx=28, pady=(0, 10))

    ctk.CTkLabel(frame_form, text="  Nueva Promoción",
                 font=("Consolas", 12, "bold"),
                 text_color=C_AMBAR_H).pack(anchor="w", padx=14, pady=(12, 4))

    ent_desc = ctk.CTkEntry(frame_form, placeholder_text="Descripción de la promo",
                             width=340)
    ent_desc.pack(padx=14, pady=4, anchor="w")

    frame_desc = ctk.CTkFrame(frame_form, fg_color="transparent")
    frame_desc.pack(fill="x", padx=14, pady=4)

    ctk.CTkLabel(frame_desc, text="Descuento %:",
                 font=("Consolas", 11), text_color=C_TEXTO_SUB).pack(side="left", padx=(0, 8))
    ent_desc2 = ctk.CTkEntry(frame_desc, placeholder_text="Ej: 15", width=80)
    ent_desc2.pack(side="left")

    lbl_conf = ctk.CTkLabel(frame_form, text="", font=("Consolas", 11))
    lbl_conf.pack(pady=4)

    scroll = ctk.CTkScrollableFrame(area, fg_color=C_PANEL, corner_radius=10,
                                     border_width=1, border_color=C_BORDE)
    scroll.pack(fill="both", expand=True, padx=28, pady=4)

    ctk.CTkLabel(scroll, text="  Promociones activas:",
                 font=("Consolas", 11, "bold"),
                 text_color=C_AMBAR_H).pack(anchor="w", padx=14, pady=(8, 4))

    def refrescar_promos():
        for w in scroll.winfo_children()[1:]:   # Conserva la etiqueta del título
            w.destroy()
        if not promos:
            ctk.CTkLabel(scroll, text="  Aún no hay promociones.",
                         font=("Consolas", 11),
                         text_color=C_TEXTO_SUB).pack(anchor="w", padx=18, pady=4)
            return
        for p in promos:
            fr = ctk.CTkFrame(scroll, fg_color="#1e293b", corner_radius=8)
            fr.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(fr,
                         text=f"  🏷️  {p['descripcion']}  —  {p['descuento_%']}% OFF  |  {p['fecha']}",
                         font=("Consolas", 12), text_color=C_AMBAR_H,
                         anchor="w").pack(anchor="w", padx=8, pady=8)

    def agregar_promo():
        desc = ent_desc.get().strip()
        try:
            dsc = float(ent_desc2.get())
        except ValueError:
            messagebox.showerror("Error", "El descuento debe ser un número.")
            return
        if not desc:
            messagebox.showwarning("Atención", "Escribe una descripción.")
            return
        if gerente_obj and hasattr(gerente_obj, "planear_promocion"):
            gerente_obj.planear_promocion(desc, dsc)
        else:
            promos.append({"descripcion": desc, "descuento_%": dsc,
                           "fecha": datetime.now().strftime("%Y-%m-%d")})
        ent_desc.delete(0, "end")
        ent_desc2.delete(0, "end")
        lbl_conf.configure(text="✔  Promoción registrada.", text_color=C_VERDE_H)
        refrescar_promos()

    ctk.CTkButton(frame_form, text="Agregar Promoción",
                  fg_color=C_AMBAR, hover_color=C_AMBAR_H,
                  font=("Consolas", 12, "bold"), width=220, height=40,
                  command=agregar_promo).pack(pady=(4, 14))

    refrescar_promos()


# ═════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═════════════════════════════════════════════════════════════════════════════

def iniciar_app() -> None:
    """Crea la ventana principal y lanza el login."""
    ventana = ctk.CTk()
    ventana.geometry("960x660")
    ventana.minsize(880, 600)
    ventana.configure(fg_color=C_FONDO)
    ventana.title("Jefe en Línea")
    mostrar_login(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    iniciar_app()