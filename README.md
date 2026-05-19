# 👔 Jefe en Línea
Sistema de administración de negocios para PyMEs desarrollado en Python.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-darkblue)
![Matplotlib](https://img.shields.io/badge/Graphs-Matplotlib-orange)

---

## ¿Qué es?

Aplicación de escritorio que centraliza la gestión de un negocio: personal, tareas, inventario, finanzas y mensajería interna, todo organizado por niveles de acceso.

---

## Roles del sistema

| Rol | Acceso |
|---|---|
| **Jefe** | Dashboard con gráficas, finanzas, gestión de personal |
| **Gerente** | Tareas, inventario, promociones, dashboard operativo |
| **Supervisor** | Pizarra Kanban con detección de colisiones horarias |
| **Empleado** | Mis tareas, asistencia, ventas (Vendedor/Cajero), reportes |

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/jefe-en-linea.git
cd jefe-en-linea

# 2. Instalar dependencias
pip install customtkinter matplotlib pillow

# 3. Ejecutar
python frontend.py
```

**Usuarios de prueba:**

| Usuario | Contraseña | Rol |
|---|---|---|
| `Administrador` | `1234` | Jefe |
| `Gerente` | `2345` | Gerente |
| `Supervisor 1` | `3456` | Supervisor |
| `Empleado 1` | `6789` | Empleado |

---

## Tecnologías

- **Python 3.10+**
- **CustomTkinter** — interfaz gráfica modo oscuro
- **Matplotlib** — gráficas de pastel y barras integradas en la UI
- **CSV** — persistencia de datos sin base de datos externa

---

## Autores

Desarrollado para la materia de **Programación Avanzada** — FCC, BUAP.

| Nombre | Matrícula |
|---|---|
| Fuentes Sánchez Amy | 202538755 |
| Serrano Avilés Marco Antonio | 202533372 |

**Profesor:** Ing. Romero Sierra Jaime Alejandro
