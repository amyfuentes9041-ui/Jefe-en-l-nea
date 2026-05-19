import csv                          # Leer y escribir archivos CSV (nuestra "base de datos")
import os                           # Rutas de archivos y verificar si existen
from datetime import datetime       # Registrar fecha/hora exacta en cada operación

# ─── Directorio base: todos los CSV quedan junto a este script ────────────────
RUTA_BASE = os.path.dirname(os.path.abspath(__file__))


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — MODELOS DE DATOS (las "fichas" de cada entidad)
# ═════════════════════════════════════════════════════════════════════════════

class Usuario:
    """
    Clase BASE de la jerarquía.
    Define los atributos y métodos comunes a TODOS los usuarios del sistema.
    De aquí heredan Jefe, Gerente, Supervisor y Empleado.
    """

    def __init__(self, id_usuario: int, nombre_usuario: str, password: str,
                 nombre_real: str, rol: str, estado_cuenta: bool = True):
        self.id_usuario    = int(id_usuario)       # Número único de identificación
        self.nombre_usuario = nombre_usuario        # Nickname para el login
        self.password      = password              # Contraseña (texto plano por simplicidad académica)
        self.nombre_real   = nombre_real           # Nombre y apellidos completos
        self.rol           = rol                   # "jefe" | "gerente" | "supervisor" | "empleado"
        self.estado_cuenta = estado_cuenta         # True = activo, False = suspendido

    # ── Métodos de la clase base ──────────────────────────────────────────────

    def validar_credenciales(self, user: str, pw: str) -> bool:
        """
        Comprueba si el usuario y contraseña dados coinciden con los de este objeto.
        Retorna True si son correctos, False en caso contrario.
        """
        return self.nombre_usuario == user and self.password == pw

    def cambiar_password(self, nueva_pw: str) -> None:
        """Reemplaza la contraseña actual por la nueva."""
        self.password = nueva_pw

    def obtener_perfil(self) -> dict:
        """
        Retorna un diccionario con los datos públicos del usuario.
        (Sin contraseña, para mostrarlos en pantalla de forma segura.)
        """
        return {
            "id":           self.id_usuario,
            "usuario":      self.nombre_usuario,
            "nombre_real":  self.nombre_real,
            "rol":          self.rol,
            "activo":       self.estado_cuenta,
        }

    def __repr__(self) -> str:
        """Representación de texto del objeto, útil para depuración."""
        return f"<{self.rol.capitalize()} '{self.nombre_usuario}'>"


# ─────────────────────────────────────────────────────────────────────────────

class Jefe(Usuario):
    """
    Hereda de Usuario.
    Dueño del negocio. Ve el dashboard maestro, autoriza presupuesto
    y envía comunicados de alta prioridad.
    """

    def __init__(self, id_usuario, nombre_usuario, password, nombre_real,
                 estado_cuenta=True, patrimonio: float = 0.0):
        # super() llama al __init__ de Usuario, fijando rol="jefe"
        super().__init__(id_usuario, nombre_usuario, password, nombre_real,
                         "jefe", estado_cuenta)
        self.patrimonio_negocio   = float(patrimonio)  # Capital total del negocio
        self.metas_estrategicas: dict  = {}             # Ej. {"ventas_anuales": 500000}
        self.lista_gerentes: list      = []             # IDs de gerentes a su cargo

    def autorizar_presupuesto(self, monto: float) -> str:
        """
        Aprueba un monto de gasto.
        Retorna un mensaje de confirmación o de error si el monto supera el patrimonio.
        """
        if monto <= self.patrimonio_negocio:
            self.patrimonio_negocio -= monto
            return f"✔ Presupuesto de ${monto:,.2f} autorizado. Patrimonio restante: ${self.patrimonio_negocio:,.2f}"
        return f"✖ Fondos insuficientes. Patrimonio actual: ${self.patrimonio_negocio:,.2f}"

    def enviar_comunicado_general(self, texto: str, sistema_mensajes) -> None:
        """
        Crea un mensaje de alta prioridad y lo envía a TODOS los usuarios registrados.
        Recibe el sistema_mensajes para poder llamar su método enviar_mensaje().
        """
        sistema_mensajes.enviar_a_todos(
            remitente=self.nombre_usuario,
            asunto="📢 Comunicado General del Jefe",
            cuerpo=texto,
            excluir=self.nombre_usuario    # No se envía a sí mismo
        )


# ─────────────────────────────────────────────────────────────────────────────

class Gerente(Usuario):
    """
    Hereda de Usuario.
    Administrador operativo. Gestiona personal, define metas mensuales
    y planea promociones con el presupuesto que el Jefe le asigna.
    """

    def __init__(self, id_usuario, nombre_usuario, password, nombre_real,
                 estado_cuenta=True, presupuesto_operativo: float = 0.0):
        super().__init__(id_usuario, nombre_usuario, password, nombre_real,
                         "gerente", estado_cuenta)
        self.presupuesto_operativo = float(presupuesto_operativo)  # Dinero disponible para operar
        self.lista_empleados: list  = []   # IDs de supervisores y empleados a su cargo
        self.metas_mensuales: dict  = {}   # Ej. {"ventas_ropa": 50000}
        self.promociones: list      = []   # Lista de promos activas

    def configurar_metas_operativas(self, clave: str, valor) -> None:
        """Agrega o actualiza un objetivo mensual."""
        self.metas_mensuales[clave] = valor

    def planear_promocion(self, descripcion: str, descuento: float) -> dict:
        """
        Crea una promoción y la agrega a la lista interna.
        Retorna el dict de la promoción para que la UI lo pueda mostrar.
        """
        promo = {
            "descripcion": descripcion,
            "descuento_%": float(descuento),
            "fecha":       datetime.now().strftime("%Y-%m-%d"),
        }
        self.promociones.append(promo)
        return promo

    def solicitar_recursos_al_jefe(self, monto: float, motivo: str,
                                    sistema_mensajes, nombre_jefe: str) -> None:
        """Envía una solicitud formal de presupuesto al jefe vía mensajería."""
        sistema_mensajes.enviar_mensaje(
            remitente=self.nombre_usuario,
            destinatario=nombre_jefe,
            asunto=f"Solicitud de Recursos — ${monto:,.2f}",
            cuerpo=f"Motivo: {motivo}\nMonto solicitado: ${monto:,.2f}"
        )


# ─────────────────────────────────────────────────────────────────────────────

class Supervisor(Usuario):
    """
    Hereda de Usuario.
    Mando intermedio. Asigna tareas, autoriza operaciones críticas
    y genera reportes de productividad de su turno.
    """

    def __init__(self, id_usuario, nombre_usuario, password, nombre_real,
                 estado_cuenta=True, area_asignada: str = "General"):
        super().__init__(id_usuario, nombre_usuario, password, nombre_real,
                         "supervisor", estado_cuenta)
        self.area_asignada      = area_asignada    # "Cajas" | "Piso de Venta" | "Almacén"
        self.codigo_autorizacion = ""              # Clave para operaciones críticas
        self.equipo_turno: list  = []              # IDs de empleados activos en su turno
        self.estado_turno: bool  = False           # True si ya inició jornada

    def asignar_tarea_pizarra(self, id_empleado: str, tarea_obj,
                               sistema_tareas) -> str:
        """
        Vincula una tarea a un empleado.
        Antes de asignar, verifica colisiones horarias con el CalendarioVisual.
        """
        tarea_obj.asignado_a = id_empleado
        sistema_tareas.tareas.append(tarea_obj)
        sistema_tareas._guardar_completo()
        return f"Tarea '{tarea_obj.titulo}' asignada a {id_empleado}"

    def autorizar_operacion_critica(self, codigo_ingresado: str) -> bool:
        """
        Desbloquea acciones restringidas (cancelaciones, devoluciones).
        Retorna True si el código es correcto.
        """
        return codigo_ingresado == self.codigo_autorizacion

    def generar_reporte_productividad(self, sistema_tareas) -> dict:
        """
        Calcula el desempeño de todo el equipo del turno.
        Retorna un dict con estadísticas listo para mostrarse en pantalla.
        """
        total = sum(1 for t in sistema_tareas.tareas
                    if t.asignado_a in self.equipo_turno)
        completadas = sum(1 for t in sistema_tareas.tareas
                          if t.asignado_a in self.equipo_turno
                          and t.estado == "Completado")
        eficiencia = round((completadas / total * 100), 1) if total > 0 else 0.0
        return {
            "area":        self.area_asignada,
            "total":       total,
            "completadas": completadas,
            "eficiencia%": eficiencia,
        }


# ─────────────────────────────────────────────────────────────────────────────

class Empleado(Usuario):
    """
    Hereda de Usuario.
    Personal operativo. Marca asistencia, consulta su pizarra kanban
    y reporta incidencias según el nivel de gravedad.
    """

    def __init__(self, id_usuario, nombre_usuario, password, nombre_real,
                 estado_cuenta=True, puesto: str = "General"):
        super().__init__(id_usuario, nombre_usuario, password, nombre_real,
                         "empleado", estado_cuenta)
        self.puesto: str           = puesto   # "Vendedor" | "Cajero" | "Almacenista" | "Limpieza"
        self.horas_acumuladas: float = 0.0    # Horas trabajadas en el periodo
        self.pizarra_tareas: list   = []      # Lista de objetos Tarea asignados

    def marcar_asistencia(self, tipo: str = "entrada") -> str:
        """
        Registra la hora exacta de entrada o salida.
        Retorna la cadena formateada para mostrar en pantalla y para guardar en CSV.
        """
        marca = f"{tipo.upper()} — {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        return marca

    def consultar_pizarra_kanban(self, sistema_tareas) -> list:
        """
        Retorna las tareas propias ordenadas por prioridad (mayor primero).
        Si hay colisión horaria la tarea aparece marcada.
        """
        mis_tareas = [t for t in sistema_tareas.tareas
                      if t.asignado_a == self.nombre_usuario]
        return sorted(mis_tareas, key=lambda t: t.prioridad, reverse=True)

    def enviar_reporte_incidencia(self, nivel: str, desc: str,
                                   sistema_mensajes,
                                   supervisores: list,
                                   jefes: list) -> None:
        """
        Reporta un problema.
        Nivel "Grave" → llega al Jefe.  Nivel normal → llega al Supervisor.
        """
        if nivel == "Grave" and jefes:
            destino = jefes[0]
        elif supervisores:
            destino = supervisores[0]
        else:
            destino = "admin"

        sistema_mensajes.enviar_mensaje(
            remitente=self.nombre_usuario,
            destinatario=destino,
            asunto=f"[{nivel}] Incidencia de {self.puesto}",
            cuerpo=desc
        )

    def registrar_actividad_puesto(self, sistema_ventas=None,
                                    sistema_inventario=None) -> str:
        """
        Punto de entrada según el puesto del empleado.
        Un Vendedor puede registrar ventas; un Almacenista ajusta stock.
        Retorna el nombre del módulo que debe abrirse en la UI.
        """
        if self.puesto in ("Vendedor", "Cajero"):
            return "ventas"
        if self.puesto == "Almacenista":
            return "inventario"
        return "tareas"


# ─────────────────────────────────────────────────────────────────────────────

class Tarea:
    """
    Representa una actividad individual en la pizarra digital.
    Tiene un rango de tiempo para poder detectar colisiones horarias.
    """

    ESTADOS = ["Pendiente", "En curso", "Revisión", "Completado"]

    def __init__(self, id_tarea: str, titulo: str, descripcion: str,
                 prioridad: int, estado: str, asignado_a: str,
                 hora_inicio: str, hora_fin: str,
                 creada_por: str, fecha: str = ""):
        self.id_tarea    = id_tarea         # ID único (T_1, T_2, …)
        self.titulo      = titulo           # Nombre corto de la actividad
        self.descripcion = descripcion      # Instrucciones detalladas
        self.prioridad   = int(prioridad)   # 1 = baja … 5 = urgente
        self.estado      = estado           # Uno de los 4 ESTADOS
        self.asignado_a  = asignado_a       # Nombre de usuario del responsable
        self.hora_inicio = hora_inicio      # Formato "HH:MM"
        self.hora_fin    = hora_fin         # Formato "HH:MM"
        self.creada_por  = creada_por       # Quien la creó (supervisor/gerente)
        self.fecha       = fecha or datetime.now().strftime("%Y-%m-%d")

    def actualizar_progreso(self, nuevo_estado: str) -> None:
        """Cambia el estado sólo si el valor es válido."""
        if nuevo_estado in self.ESTADOS:
            self.estado = nuevo_estado

    def verificar_plazo(self) -> bool:
        """
        Comprueba si la tarea ya debería estar terminada según la hora_fin y la fecha.
        Retorna True si está vencida y aún no está Completada.
        """
        if self.estado == "Completado":
            return False
        try:
            limite = datetime.strptime(f"{self.fecha} {self.hora_fin}", "%Y-%m-%d %H:%M")
            return datetime.now() > limite
        except ValueError:
            return False


class CalendarioVisual:
    """
    Controlador de la pizarra de horarios.
    Detecta si dos tareas de un mismo empleado se sobreponen en tiempo.
    No guarda datos propios; trabaja sobre la lista de tareas del SistemaTareas.
    """

    @staticmethod
    def _a_minutos(hora_str: str) -> int:
        """Convierte 'HH:MM' a minutos desde medianoche para comparaciones numéricas."""
        try:
            h, m = hora_str.split(":")
            return int(h) * 60 + int(m)
        except (ValueError, AttributeError):
            return 0

    def detectar_colision_horaria(self, tareas: list) -> list[tuple]:
        """
        Recibe la lista completa de tareas.
        Retorna una lista de tuplas (tarea_a, tarea_b) donde hay solapamiento
        de horario para el mismo empleado en el mismo día.
        Útil para mostrar alertas visuales en la pizarra.
        """
        colisiones = []
        # Agrupamos por empleado y fecha para comparar sólo dentro del mismo grupo
        por_empleado: dict[str, list] = {}
        for t in tareas:
            clave = f"{t.asignado_a}|{t.fecha}"
            por_empleado.setdefault(clave, []).append(t)

        for grupo in por_empleado.values():
            for i in range(len(grupo)):
                for j in range(i + 1, len(grupo)):
                    a, b = grupo[i], grupo[j]
                    ini_a = self._a_minutos(a.hora_inicio)
                    fin_a = self._a_minutos(a.hora_fin)
                    ini_b = self._a_minutos(b.hora_inicio)
                    fin_b = self._a_minutos(b.hora_fin)
                    # Hay colisión si los rangos se solapan
                    if ini_a < fin_b and ini_b < fin_a:
                        colisiones.append((a, b))
        return colisiones


# ─────────────────────────────────────────────────────────────────────────────

class Producto:
    """Artículo del inventario. Controla el stock y emite alertas de reorden."""

    def __init__(self, id_producto: str, nombre: str, categoria: str,
                 costo_compra: float, precio_venta: float,
                 cantidad_stock: int, punto_reorden: int):
        self.id_producto    = id_producto
        self.nombre         = nombre
        self.categoria      = categoria
        self.costo_compra   = float(costo_compra)
        self.precio_venta   = float(precio_venta)
        self.cantidad_stock = int(cantidad_stock)
        self.punto_reorden  = int(punto_reorden)

    def ajustar_stock(self, cantidad: int) -> None:
        """Suma (si positivo) o resta (si negativo) unidades. El mínimo es 0."""
        self.cantidad_stock = max(0, self.cantidad_stock + int(cantidad))

    def verificar_disponibilidad(self) -> bool:
        """True si el stock supera el punto de reorden (nivel de seguridad)."""
        return self.cantidad_stock > self.punto_reorden

    def generar_alerta_reorden(self) -> str | None:
        """Si el stock es bajo, retorna un mensaje de alerta; si no, retorna None."""
        if self.cantidad_stock <= self.punto_reorden:
            return (f"⚠ STOCK BAJO — {self.nombre}: "
                    f"{self.cantidad_stock} uds. (mínimo: {self.punto_reorden})")
        return None


# ─────────────────────────────────────────────────────────────────────────────

class Movimiento:
    """
    Registro financiero: una venta, un gasto fijo o la compra de insumos.
    Cada fila del CSV de finanzas corresponde a un objeto Movimiento.
    """

    def __init__(self, id_trans: str, monto: float, categoria: str,
                 metodo_pago: str, descripcion: str,
                 fecha_hora: str, registrado_por: str, anulado: bool = False):
        self.id_trans       = id_trans
        self.monto          = float(monto)     # Positivo = ingreso, Negativo = gasto
        self.categoria      = categoria        # "Venta" | "Gasto Fijo" | "Insumos" | "Sueldos"
        self.metodo_pago    = metodo_pago      # "Efectivo" | "Tarjeta" | "Transferencia"
        self.descripcion    = descripcion
        self.fecha_hora     = fecha_hora
        self.registrado_por = registrado_por
        self.anulado        = anulado          # True = cancelado, no cuenta en estadísticas


# ─────────────────────────────────────────────────────────────────────────────

class VentaProducto:
    """
    Venta de uno o más productos registrada por un Vendedor o Cajero.
    Cada item del carrito puede identificarse por nombre O por código.
    """

    def __init__(self, id_venta: str, vendedor: str, items: list,
                 total: float, fecha_hora: str):
        self.id_venta  = id_venta    # VNT_1, VNT_2, …
        self.vendedor  = vendedor    # nombre_usuario del empleado
        # items: lista de dicts {"id_producto", "nombre", "cantidad", "subtotal"}
        self.items     = items
        self.total     = float(total)
        self.fecha_hora = fecha_hora


# ─────────────────────────────────────────────────────────────────────────────

class Mensaje:
    """Mensaje interno entre usuarios del sistema."""

    def __init__(self, id_mensaje: str, remitente: str, destinatario: str,
                 asunto: str, cuerpo: str, fecha_hora: str, leido: bool = False):
        self.id_mensaje   = id_mensaje
        self.remitente    = remitente
        self.destinatario = destinatario
        self.asunto       = asunto
        self.cuerpo       = cuerpo
        self.fecha_hora   = fecha_hora
        self.leido        = leido    # False = no leído (burbuja roja en bandeja)

    def marcar_como_leido(self) -> None:
        """Cambia el estado visual a leído."""
        self.leido = True


# ─────────────────────────────────────────────────────────────────────────────

class ReporteDesempeno:
    """
    Calcula métricas individuales de un empleado a partir de sus tareas.
    Clase del módulo de Control/Estadística.
    """

    def __init__(self, nombre_usuario: str):
        self.nombre_usuario        = nombre_usuario
        self.calificacion_promedio = 0.0   # Puntuación sobre 10
        self.porcentaje_eficiencia = 0.0   # % de tareas completadas

    def calcular(self, sistema_tareas) -> None:
        """Recorre las tareas del empleado y actualiza las métricas."""
        todas       = [t for t in sistema_tareas.tareas
                       if t.asignado_a == self.nombre_usuario]
        completadas = [t for t in todas if t.estado == "Completado"]

        total = len(todas)
        if total == 0:
            self.porcentaje_eficiencia = 0.0
            self.calificacion_promedio = 0.0
            return

        self.porcentaje_eficiencia = round(len(completadas) / total * 100, 1)
        # 10 puntos si no está vencida, 5 si llegó tarde
        puntos = sum(10 if not t.verificar_plazo() else 5 for t in completadas)
        self.calificacion_promedio = round(puntos / total, 1) if completadas else 0.0

    def generar_boleta_empleado(self, sistema_tareas) -> dict:
        """Genera un resumen completo listo para mostrarse en la interfaz."""
        self.calcular(sistema_tareas)
        todas       = [t for t in sistema_tareas.tareas
                       if t.asignado_a == self.nombre_usuario]
        completadas = [t for t in todas if t.estado == "Completado"]
        pendientes  = [t for t in todas if t.estado == "Pendiente"]
        en_curso    = [t for t in todas if t.estado == "En curso"]
        return {
            "empleado":      self.nombre_usuario,
            "total":         len(todas),
            "completadas":   len(completadas),
            "pendientes":    len(pendientes),
            "en_curso":      len(en_curso),
            "eficiencia_%":  self.porcentaje_eficiencia,
            "calificacion":  self.calificacion_promedio,
        }


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — SERVICIOS (clases que gestionan colecciones y persisten en CSV)
# ═════════════════════════════════════════════════════════════════════════════

class SistemaAutenticacion:
    """
    Gestiona TODOS los usuarios del sistema (jefes, gerentes, supervisores y empleados).
    Lee y escribe  usuarios.csv
    Columnas: id_usuario, nombre_usuario, password, nombre_real, rol, estado_cuenta, puesto
    """

    def __init__(self, archivo: str = "usuarios.csv"):
        self.archivo = os.path.join(RUTA_BASE, archivo)
        self.usuarios: dict[str, Usuario] = {}   # clave = nombre_usuario
        self._cargar()

    def _cargar(self) -> None:
        """Lee el CSV y construye el objeto correcto según el rol de cada fila."""
        if not os.path.exists(self.archivo):
            return
        with open(self.archivo, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rol    = row.get("rol", "empleado")
                activo = row.get("estado_cuenta", "True").lower() != "false"
                iid    = row.get("id_usuario", 0)
                nu     = row["nombre_usuario"]
                pw     = row["password"]
                nr     = row.get("nombre_real", "")
                puesto = row.get("puesto", "General")

                if rol == "jefe":
                    obj = Jefe(iid, nu, pw, nr, activo)
                elif rol == "gerente":
                    obj = Gerente(iid, nu, pw, nr, activo)
                elif rol == "supervisor":
                    obj = Supervisor(iid, nu, pw, nr, activo, puesto)
                else:
                    obj = Empleado(iid, nu, pw, nr, activo, puesto)
                self.usuarios[nu] = obj

    def _guardar_completo(self) -> None:
        """Reescribe el CSV completo con el estado actual del diccionario."""
        campos = ["id_usuario", "nombre_usuario", "password", "nombre_real",
                  "rol", "estado_cuenta", "puesto"]
        with open(self.archivo, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            for u in self.usuarios.values():
                w.writerow({
                    "id_usuario":    u.id_usuario,
                    "nombre_usuario":u.nombre_usuario,
                    "password":      u.password,
                    "nombre_real":   u.nombre_real,
                    "rol":           u.rol,
                    "estado_cuenta": u.estado_cuenta,
                    "puesto":        getattr(u, "puesto", getattr(u, "area_asignada", "")),
                })

    def _siguiente_id(self) -> int:
        """Genera el siguiente ID numérico disponible."""
        if not self.usuarios:
            return 1
        return max(u.id_usuario for u in self.usuarios.values()) + 1

    # ── Operaciones públicas ──────────────────────────────────────────────────

    def registrar_usuario(self, nombre_usuario: str, password: str, rol: str,
                           nombre_real: str = "", puesto: str = "General") -> None:
        """Crea un nuevo usuario en memoria y lo persiste en el CSV."""
        iid = self._siguiente_id()
        if rol == "jefe":
            obj = Jefe(iid, nombre_usuario, password, nombre_real)
        elif rol == "gerente":
            obj = Gerente(iid, nombre_usuario, password, nombre_real)
        elif rol == "supervisor":
            obj = Supervisor(iid, nombre_usuario, password, nombre_real,
                              area_asignada=puesto)
        else:
            obj = Empleado(iid, nombre_usuario, password, nombre_real,
                           puesto=puesto)
        self.usuarios[nombre_usuario] = obj
        self._guardar_completo()

    def eliminar_usuario(self, nombre_usuario: str) -> None:
        if nombre_usuario in self.usuarios:
            del self.usuarios[nombre_usuario]
            self._guardar_completo()

    def autenticar(self, nombre_usuario: str, password: str) -> str | None:
        """
        Verifica credenciales.
        Retorna el ROL si es correcto y la cuenta está activa, o None si falla.
        """
        u = self.usuarios.get(nombre_usuario)
        if u and u.password == password and u.estado_cuenta:
            return u.rol
        return None

    def por_rol(self, rol: str) -> list:
        """Retorna la lista de usuarios con el rol especificado."""
        return [u for u in self.usuarios.values() if u.rol == rol]


# ─────────────────────────────────────────────────────────────────────────────

class SistemaTareas:
    """
    Gestiona la pizarra digital de tareas.
    Lee y escribe  tareas.csv
    Columnas: id_tarea, titulo, descripcion, prioridad, estado,
              asignado_a, hora_inicio, hora_fin, creada_por, fecha
    """

    def __init__(self, archivo: str = "tareas.csv"):
        self.archivo  = os.path.join(RUTA_BASE, archivo)
        self.tareas: list[Tarea] = []
        self.calendario = CalendarioVisual()  # Para detectar colisiones
        self._cargar()

    def _cargar(self) -> None:
        if not os.path.exists(self.archivo):
            return
        with open(self.archivo, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                self.tareas.append(Tarea(
                    id_tarea    = row["id_tarea"],
                    titulo      = row["titulo"],
                    descripcion = row.get("descripcion", ""),
                    prioridad   = row.get("prioridad", 1),
                    estado      = row.get("estado", "Pendiente"),
                    asignado_a  = row.get("asignado_a", ""),
                    hora_inicio = row.get("hora_inicio", "08:00"),
                    hora_fin    = row.get("hora_fin", "09:00"),
                    creada_por  = row.get("creada_por", ""),
                    fecha       = row.get("fecha", ""),
                ))

    def _guardar_completo(self) -> None:
        campos = ["id_tarea", "titulo", "descripcion", "prioridad", "estado",
                  "asignado_a", "hora_inicio", "hora_fin", "creada_por", "fecha"]
        with open(self.archivo, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            for t in self.tareas:
                w.writerow({
                    "id_tarea":    t.id_tarea,
                    "titulo":      t.titulo,
                    "descripcion": t.descripcion,
                    "prioridad":   t.prioridad,
                    "estado":      t.estado,
                    "asignado_a":  t.asignado_a,
                    "hora_inicio": t.hora_inicio,
                    "hora_fin":    t.hora_fin,
                    "creada_por":  t.creada_por,
                    "fecha":       t.fecha,
                })

    def _generar_id(self) -> str:
        max_id = max((int(t.id_tarea.split("_")[1])
                      for t in self.tareas if t.id_tarea.startswith("T_")),
                     default=0)
        return f"T_{max_id + 1}"

    # ── Operaciones públicas ──────────────────────────────────────────────────

    def crear_tarea(self, titulo: str, descripcion: str, prioridad: int,
                    asignado_a: str, hora_inicio: str, hora_fin: str,
                    creada_por: str, fecha: str = "") -> tuple:
        """
        Crea una tarea nueva.
        Antes de guardar, verifica colisiones.
        Retorna (tarea, lista_colisiones).
        """
        nueva = Tarea(
            id_tarea    = self._generar_id(),
            titulo      = titulo,
            descripcion = descripcion,
            prioridad   = prioridad,
            estado      = "Pendiente",
            asignado_a  = asignado_a,
            hora_inicio = hora_inicio,
            hora_fin    = hora_fin,
            creada_por  = creada_por,
            fecha       = fecha or datetime.now().strftime("%Y-%m-%d"),
        )
        self.tareas.append(nueva)
        colisiones = self.calendario.detectar_colision_horaria(self.tareas)
        self._guardar_completo()
        return nueva, colisiones

    def actualizar_estado(self, id_tarea: str, nuevo_estado: str) -> bool:
        for t in self.tareas:
            if t.id_tarea == id_tarea:
                t.actualizar_progreso(nuevo_estado)
                self._guardar_completo()
                return True
        return False

    def eliminar_tarea(self, id_tarea: str) -> None:
        self.tareas = [t for t in self.tareas if t.id_tarea != id_tarea]
        self._guardar_completo()

    def tareas_de(self, nombre_usuario: str) -> list:
        """Retorna todas las tareas asignadas a un usuario específico."""
        return [t for t in self.tareas if t.asignado_a == nombre_usuario]

    def tareas_vencidas(self) -> list:
        """Tareas cuyo plazo ya pasó y no están completadas."""
        return [t for t in self.tareas if t.verificar_plazo()]

    def colisiones_activas(self) -> list:
        """Devuelve todos los choques de horario actuales (para la alerta del dashboard)."""
        return self.calendario.detectar_colision_horaria(self.tareas)


# ─────────────────────────────────────────────────────────────────────────────

class SistemaInventario:
    """
    Controla los productos del negocio.
    Lee y escribe  inventario.csv
    Columnas: id_producto, nombre, categoria, costo_compra,
              precio_venta, cantidad_stock, punto_reorden
    """

    def __init__(self, archivo: str = "inventario.csv"):
        self.archivo   = os.path.join(RUTA_BASE, archivo)
        self.productos: dict[str, Producto] = {}
        self._cargar()

    def _cargar(self) -> None:
        if not os.path.exists(self.archivo):
            return
        with open(self.archivo, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                p = Producto(
                    id_producto   = row["id_producto"],
                    nombre        = row["nombre"],
                    categoria     = row.get("categoria", "General"),
                    costo_compra  = row.get("costo_compra", 0),
                    precio_venta  = row.get("precio_venta", 0),
                    cantidad_stock= row.get("cantidad_stock", 0),
                    punto_reorden = row.get("punto_reorden", 5),
                )
                self.productos[p.id_producto] = p

    def _guardar_completo(self) -> None:
        campos = ["id_producto", "nombre", "categoria", "costo_compra",
                  "precio_venta", "cantidad_stock", "punto_reorden"]
        with open(self.archivo, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            for p in self.productos.values():
                w.writerow({
                    "id_producto":    p.id_producto,
                    "nombre":         p.nombre,
                    "categoria":      p.categoria,
                    "costo_compra":   p.costo_compra,
                    "precio_venta":   p.precio_venta,
                    "cantidad_stock": p.cantidad_stock,
                    "punto_reorden":  p.punto_reorden,
                })

    def _generar_id(self) -> str:
        max_id = max((int(p.id_producto.split("_")[1])
                      for p in self.productos.values()
                      if p.id_producto.startswith("INV_")),
                     default=0)
        return f"INV_{max_id + 1}"

    def registrar_producto(self, nombre: str, categoria: str,
                            costo_compra: float, precio_venta: float,
                            cantidad_stock: int, punto_reorden: int = 5) -> Producto:
        nuevo = Producto(self._generar_id(), nombre, categoria,
                         costo_compra, precio_venta, cantidad_stock, punto_reorden)
        self.productos[nuevo.id_producto] = nuevo
        self._guardar_completo()
        return nuevo

    def eliminar_producto(self, id_producto: str) -> None:
        if id_producto in self.productos:
            del self.productos[id_producto]
            self._guardar_completo()

    def descontar_stock(self, id_producto: str, cantidad: int) -> bool:
        """
        Resta unidades al stock cuando se registra una venta.
        Retorna True si había suficiente stock, False si no.
        """
        p = self.productos.get(id_producto)
        if p and p.cantidad_stock >= cantidad:
            p.ajustar_stock(-cantidad)
            self._guardar_completo()
            return True
        return False

    def buscar_por_nombre_o_codigo(self, termino: str) -> list:
        """
        Busca productos por nombre (parcial) o por ID exacto.
        Permite que los vendedores encuentren artículos rápidamente.
        """
        termino = termino.lower()
        return [p for p in self.productos.values()
                if termino in p.nombre.lower() or termino == p.id_producto.lower()]

    def generar_lista_compras(self) -> list:
        """Retorna los productos cuyo stock bajó del punto de reorden."""
        return [p for p in self.productos.values()
                if p.cantidad_stock <= p.punto_reorden]

    def alertas_stock(self) -> list[str]:
        """Lista de mensajes de alerta para mostrar en el dashboard."""
        return [p.generar_alerta_reorden() for p in self.productos.values()
                if p.generar_alerta_reorden()]


# ─────────────────────────────────────────────────────────────────────────────

class SistemaFinanzas:
    """
    Registra todos los movimientos de dinero.
    Lee y escribe  finanzas.csv
    Columnas: id_trans, monto, categoria, metodo_pago,
              descripcion, fecha_hora, registrado_por, anulado

    También provee los datos para las GRÁFICAS del dashboard:
      - grafica_pastel()   → distribución de gastos por categoría
      - grafica_barras()   → ventas diarias del mes
      - calcular_utilidad_neta()
    """

    def __init__(self, archivo: str = "finanzas.csv"):
        self.archivo     = os.path.join(RUTA_BASE, archivo)
        self.movimientos: list[Movimiento] = []
        self._cargar()

    def _cargar(self) -> None:
        if not os.path.exists(self.archivo):
            return
        with open(self.archivo, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                m = Movimiento(
                    id_trans      = row["id_trans"],
                    monto         = row["monto"],
                    categoria     = row.get("categoria", "Venta"),
                    metodo_pago   = row.get("metodo_pago", "Efectivo"),
                    descripcion   = row.get("descripcion", ""),
                    fecha_hora    = row.get("fecha_hora", ""),
                    registrado_por= row.get("registrado_por", ""),
                    anulado       = row.get("anulado", "False").lower() == "true",
                )
                self.movimientos.append(m)

    def _guardar_completo(self) -> None:
        campos = ["id_trans", "monto", "categoria", "metodo_pago",
                  "descripcion", "fecha_hora", "registrado_por", "anulado"]
        with open(self.archivo, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            for m in self.movimientos:
                w.writerow({
                    "id_trans":       m.id_trans,
                    "monto":          m.monto,
                    "categoria":      m.categoria,
                    "metodo_pago":    m.metodo_pago,
                    "descripcion":    m.descripcion,
                    "fecha_hora":     m.fecha_hora,
                    "registrado_por": m.registrado_por,
                    "anulado":        m.anulado,
                })

    def _generar_id(self) -> str:
        max_id = max((int(m.id_trans.split("_")[1])
                      for m in self.movimientos if m.id_trans.startswith("MOV_")),
                     default=0)
        return f"MOV_{max_id + 1}"

    # ── Operaciones públicas ──────────────────────────────────────────────────

    def registrar_movimiento(self, monto: float, categoria: str,
                              metodo_pago: str, descripcion: str,
                              registrado_por: str) -> Movimiento:
        """Crea y persiste un nuevo movimiento financiero."""
        nuevo = Movimiento(
            id_trans      = self._generar_id(),
            monto         = monto,
            categoria     = categoria,
            metodo_pago   = metodo_pago,
            descripcion   = descripcion,
            fecha_hora    = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            registrado_por= registrado_por,
        )
        self.movimientos.append(nuevo)
        self._guardar_completo()
        return nuevo

    def anular_transaccion(self, id_trans: str) -> bool:
        """Marca como anulada sin borrar del historial (para auditoría)."""
        for m in self.movimientos:
            if m.id_trans == id_trans:
                m.anulado = True
                self._guardar_completo()
                return True
        return False

    # ── Estadísticas para gráficas ────────────────────────────────────────────

    def obtener_total_ventas(self, periodo: str = "mensual") -> float:
        """
        Suma los ingresos activos del periodo indicado.
        periodo puede ser: "diario", "semanal" o "mensual"
        """
        ahora = datetime.now()
        total = 0.0
        for m in self.movimientos:
            if m.anulado or m.monto <= 0:
                continue
            try:
                fecha = datetime.strptime(m.fecha_hora, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            if periodo == "diario"  and fecha.date()  != ahora.date():       continue
            if periodo == "semanal" and (ahora - fecha).days > 7:             continue
            if periodo == "mensual" and (fecha.year, fecha.month) != (ahora.year, ahora.month): continue
            total += m.monto
        return round(total, 2)

    def calcular_utilidad_neta(self) -> float:
        """Ingresos totales menos egresos totales (sin anulados)."""
        ingresos = sum(m.monto for m in self.movimientos if not m.anulado and m.monto > 0)
        egresos  = sum(abs(m.monto) for m in self.movimientos if not m.anulado and m.monto < 0)
        return round(ingresos - egresos, 2)

    def datos_grafica_pastel(self) -> dict:
        """
        Agrupa el total ABSOLUTO de movimientos por categoría.
        Resultado: {"Venta": 15000, "Gasto Fijo": 4000, ...}
        Estos datos los usa matplotlib para la gráfica de pastel.
        """
        resumen: dict[str, float] = {}
        for m in self.movimientos:
            if m.anulado:
                continue
            resumen[m.categoria] = resumen.get(m.categoria, 0.0) + abs(m.monto)
        return resumen

    def datos_grafica_barras(self) -> dict:
        """
        Ventas diarias del mes actual.
        Resultado: {1: 500.0, 2: 320.0, ...}  (día → total ventas ese día)
        Estos datos los usa matplotlib para la gráfica de barras.
        """
        ahora   = datetime.now()
        por_dia: dict[int, float] = {}
        for m in self.movimientos:
            if m.anulado or m.monto <= 0:
                continue
            try:
                fecha = datetime.strptime(m.fecha_hora, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            if fecha.year == ahora.year and fecha.month == ahora.month:
                por_dia[fecha.day] = por_dia.get(fecha.day, 0.0) + m.monto
        return dict(sorted(por_dia.items()))

    def datos_grafica_metas(self, metas: dict) -> tuple:
        """
        Compara ventas reales del mes contra las metas del gerente.
        Retorna (categorias, reales, metas_lista) para la gráfica de barras comparativa.
        """
        reales = self.datos_grafica_pastel()
        cats   = list(metas.keys())
        vals_r = [reales.get(c, 0.0) for c in cats]
        vals_m = [metas.get(c, 0.0)  for c in cats]
        return cats, vals_r, vals_m


# ─────────────────────────────────────────────────────────────────────────────

class SistemaVentasProducto:
    """
    Registra ventas de productos físicos hechas por Vendedores o Cajeros.
    Lee y escribe  ventas_productos.csv
    Columnas: id_venta, vendedor, id_producto, nombre_producto,
              cantidad, subtotal, total, fecha_hora
    """

    def __init__(self, archivo: str = "ventas_productos.csv"):
        self.archivo = os.path.join(RUTA_BASE, archivo)
        self.ventas: list[VentaProducto] = []
        self._cargar()

    def _cargar(self) -> None:
        if not os.path.exists(self.archivo):
            return
        # Agrupamos filas por id_venta
        grupos: dict[str, dict] = {}
        with open(self.archivo, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                vid = row["id_venta"]
                if vid not in grupos:
                    grupos[vid] = {
                        "vendedor":   row["vendedor"],
                        "total":      row.get("total", 0),
                        "fecha_hora": row.get("fecha_hora", ""),
                        "items":      [],
                    }
                grupos[vid]["items"].append({
                    "id_producto": row["id_producto"],
                    "nombre":      row["nombre_producto"],
                    "cantidad":    int(row["cantidad"]),
                    "subtotal":    float(row["subtotal"]),
                })
        for vid, dat in grupos.items():
            self.ventas.append(VentaProducto(vid, dat["vendedor"],
                                              dat["items"], dat["total"],
                                              dat["fecha_hora"]))

    def _generar_id(self) -> str:
        max_id = max((int(v.id_venta.split("_")[1])
                      for v in self.ventas if v.id_venta.startswith("VNT_")),
                     default=0)
        return f"VNT_{max_id + 1}"

    def registrar_venta(self, vendedor: str, carrito: list,
                         sistema_inventario) -> VentaProducto:
        """
        Registra una venta completa.
        carrito = [{"id_producto": ..., "nombre": ..., "cantidad": ..., "subtotal": ...}]
        Descuenta el stock automáticamente usando sistema_inventario.
        """
        nuevo_id  = self._generar_id()
        total     = sum(it["subtotal"] for it in carrito)
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        nueva = VentaProducto(nuevo_id, vendedor, carrito, total, fecha_hora)
        self.ventas.append(nueva)

        # Descontar stock de cada producto vendido
        for it in carrito:
            sistema_inventario.descontar_stock(it["id_producto"], it["cantidad"])

        # Persistir una fila por producto en el CSV
        archivo_existe = os.path.exists(self.archivo)
        with open(self.archivo, "a", newline="", encoding="utf-8") as f:
            campos = ["id_venta", "vendedor", "id_producto", "nombre_producto",
                      "cantidad", "subtotal", "total", "fecha_hora"]
            writer = csv.DictWriter(f, fieldnames=campos)
            if not archivo_existe:
                writer.writeheader()
            for it in carrito:
                writer.writerow({
                    "id_venta":       nuevo_id,
                    "vendedor":       vendedor,
                    "id_producto":    it["id_producto"],
                    "nombre_producto":it["nombre"],
                    "cantidad":       it["cantidad"],
                    "subtotal":       it["subtotal"],
                    "total":          total,
                    "fecha_hora":     fecha_hora,
                })
        return nueva

    def ventas_de(self, nombre_usuario: str) -> list:
        """Retorna las ventas registradas por un vendedor específico."""
        return [v for v in self.ventas if v.vendedor == nombre_usuario]


# ─────────────────────────────────────────────────────────────────────────────

class SistemaMensajes:
    """
    Mensajería interna: empleados reportan al supervisor/jefe,
    el jefe envía comunicados.
    Lee y escribe  mensajes.csv
    Columnas: id_mensaje, remitente, destinatario, asunto, cuerpo, fecha_hora, leido
    """

    def __init__(self, archivo: str = "mensajes.csv"):
        self.archivo  = os.path.join(RUTA_BASE, archivo)
        self.mensajes: list[Mensaje] = []
        self._cargar()

    def _cargar(self) -> None:
        if not os.path.exists(self.archivo):
            return
        with open(self.archivo, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                self.mensajes.append(Mensaje(
                    id_mensaje   = row["id_mensaje"],
                    remitente    = row["remitente"],
                    destinatario = row["destinatario"],
                    asunto       = row["asunto"],
                    cuerpo       = row.get("cuerpo", ""),
                    fecha_hora   = row.get("fecha_hora", ""),
                    leido        = row.get("leido", "False").lower() == "true",
                ))

    def _guardar_completo(self) -> None:
        campos = ["id_mensaje", "remitente", "destinatario",
                  "asunto", "cuerpo", "fecha_hora", "leido"]
        with open(self.archivo, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            for m in self.mensajes:
                w.writerow({
                    "id_mensaje":   m.id_mensaje,
                    "remitente":    m.remitente,
                    "destinatario": m.destinatario,
                    "asunto":       m.asunto,
                    "cuerpo":       m.cuerpo,
                    "fecha_hora":   m.fecha_hora,
                    "leido":        m.leido,
                })

    def _generar_id(self) -> str:
        max_id = max((int(m.id_mensaje.split("_")[1])
                      for m in self.mensajes if m.id_mensaje.startswith("MSG_")),
                     default=0)
        return f"MSG_{max_id + 1}"

    def enviar_mensaje(self, remitente: str, destinatario: str,
                        asunto: str, cuerpo: str) -> Mensaje:
        """Crea y persiste un mensaje nuevo entre dos usuarios."""
        nuevo = Mensaje(
            id_mensaje   = self._generar_id(),
            remitente    = remitente,
            destinatario = destinatario,
            asunto       = asunto,
            cuerpo       = cuerpo,
            fecha_hora   = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.mensajes.append(nuevo)
        self._guardar_completo()
        return nuevo

    def enviar_a_todos(self, remitente: str, asunto: str,
                        cuerpo: str, excluir: str = "") -> None:
        """
        Envía el mismo mensaje a todos los usuarios registrados.
        Se usa para los comunicados generales del Jefe.
        """
        from backend import auth_sys   # Importación local para evitar circular
        for nombre in auth_sys.usuarios:
            if nombre != excluir:
                self.enviar_mensaje(remitente, nombre, asunto, cuerpo)

    def bandeja_de(self, destinatario: str) -> list:
        """Retorna los mensajes recibidos ordenados del más reciente al más antiguo."""
        return sorted(
            [m for m in self.mensajes if m.destinatario == destinatario],
            key=lambda x: x.fecha_hora, reverse=True
        )

    def no_leidos_de(self, destinatario: str) -> int:
        """Cuenta los mensajes sin leer para mostrar la burbuja de notificación."""
        return sum(1 for m in self.mensajes
                   if m.destinatario == destinatario and not m.leido)

    def marcar_leido(self, id_mensaje: str) -> None:
        for m in self.mensajes:
            if m.id_mensaje == id_mensaje:
                m.marcar_como_leido()
                self._guardar_completo()
                return


# ═════════════════════════════════════════════════════════════════════════════
# INSTANCIAS GLOBALES — se crean una sola vez al importar el módulo
# ═════════════════════════════════════════════════════════════════════════════

auth_sys       = SistemaAutenticacion("usuarios.csv")
tareas_sys     = SistemaTareas("tareas.csv")
inventario_sys = SistemaInventario("inventario.csv")
finanzas_sys   = SistemaFinanzas("finanzas.csv")
ventas_prod_sys= SistemaVentasProducto("ventas_productos.csv")
mensajes_sys   = SistemaMensajes("mensajes.csv")