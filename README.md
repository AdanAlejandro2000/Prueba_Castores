Prueba_Castores Control de inventario Sistema de Inventario _ Flask + SQL Server

Este proyecto es un sistema de control de inventario con roles de usuario (Administrador y Almacenista), gestión de productos, control de existencias bitácora de movimientos de entrada y salida. Construido con Flask, HTML/CSS, SQL Server y manejo de sesiones para control de permisos.

python --version 3.11.9 Microsoft SQL Server Developer (64-bit) -- 15.0.2000.5 Visual Studio Code -- 15.0.2000.5

Sistema de Usuarios

Registro e inicio de sesión.

Manejo de sesiones en Flask.

Roles:

Administrador: Control total del sistema.
Almacenista: Solo control de inventario. Gestión de Productos
Agregar productos.

Subir imagen.

Activar / desactivar productos.

Ver inventario.

Entradas y Salidas

Genera movimientos con: - Producto\

Tipo de movimiento\
Cantidad\
Usuario\
Fecha y hora
Historial de Movimientos

Filtro por tipo: Entrada / Salida.
Ordenado por fecha.
Estructura del Proyecto

/static
/templates
app.py
db.py
README.md
Base de Datos prueba_Castores

Usuarios

IdUsuario, NombreUsuario, Correo, Password, IdRol, estatus
Productos

IdProducto, Nombre, CantidadActual, Estatus, ImagenRuta
Movimientos

IdMovimiento, IdProducto, TipoMovimiento, Cantidad, FechaHora, IdUsuario
Instalación

git clone https://github.com/AdanAlejandro2000/Prueba_Castores.git
pip install flask pyodbc
python app.py
Roles

Función Admin Almacenista

Agregar productos si no Aumentar stock si no Restar stock no si Ver movimientos si no

