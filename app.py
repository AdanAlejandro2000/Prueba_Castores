from flask import Flask, render_template, request, redirect, session, flash
from db import get_connection
from functools import wraps
import os


app = Flask(__name__)
app.secret_key = "adan1234"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

#   DECORADORES DE PERMISOS


def login_requerido(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "id_usuario" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrap


def solo_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get("rol") != 1:
            return redirect("/home")
        return f(*args, **kwargs)
    return wrap


def solo_almacenista(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get("rol") != 2:
            return redirect("/home")
        return f(*args, **kwargs)
    return wrap



@app.route('/', methods=['GET'])
def index():
    return redirect("/login")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        con = get_connection()
        cur = con.cursor()
        cur.execute("""
            SELECT IdUsuario, NombreUsuario, Correo, IdRol
            FROM Usuarios 
            WHERE Correo=? AND Password=? AND estatus=1
        """, (correo, password))

        user = cur.fetchone()

        if user:
            # Guardar datos en sesión
            session["id_usuario"] = user.IdUsuario
            session["nombre"] = user.NombreUsuario
            session["rol"] = user.IdRol

            # Redirección según el rol
            if user.IdRol == 1:  # Administrador
                return redirect("/productos")
            else:  # Almacenista
                return redirect("/productos_almacenista")

        return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['usuario']
        correo = request.form['correo']
        password = request.form['password']
        rol = request.form['rol']

        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            INSERT INTO Usuarios (NombreUsuario, Correo, Password, IdRol, estatus)
            VALUES (?, ?, ?, ?, 1)
        """, (nombre, correo, password, rol))

        con.commit()
        return redirect("/login")

    return render_template("registro.html")


@app.route('/home')
@login_requerido
def home():
    return render_template("home.html")

@app.route("/productos/agregar", methods=["GET", "POST"])
@login_requerido
@solo_admin
def agregar_producto():
    if request.method == "POST":
        nombre = request.form["name_product"]
        cantidad = request.form["qty"]
        imagen = request.files["img"]

        # Guardar archivo
        nombre_archivo = imagen.filename
        ruta_guardado = os.path.join(app.config["UPLOAD_FOLDER"], nombre_archivo)
        imagen.save(ruta_guardado)

        ruta_db = f"/static/uploads/{nombre_archivo}"

        con = get_connection()
        cur = con.cursor()
        cur.execute("""
            INSERT INTO Productos_01 (Nombre, CantidadActual, Estatus, ImagenRuta)
            VALUES (?, ?, 1, ?)
        """, (nombre, cantidad, ruta_db))
        con.commit()
        flash("Producto agregado correctamente", "success")
        return redirect("/productos")  

    return render_template("addProducto.html")  



@app.route("/productos")
@login_requerido
@solo_admin
def productos():
    con = get_connection()
    cur = con.cursor()
    
    cur.execute("""
        SELECT IdProducto, Nombre, CantidadActual, Estatus, ImagenRuta
        FROM Productos_01
    """)
    
    productos = cur.fetchall()  # lista de registros
    return render_template("producto_admin.html", productos=productos)


@app.route("/productos_almacenista")
@login_requerido
def productos_almacenista():
    con = get_connection()
    cur = con.cursor()
    
    cur.execute("""
        SELECT IdProducto, Nombre, CantidadActual, Estatus, ImagenRuta
        FROM Productos_01
    """)
    
    productos = cur.fetchall()  # lista de registros
    return render_template("producto_almacenista.html", productos=productos)


@app.route("/admin_panel")
@login_requerido
@solo_admin
def admin_panel():
    # Traer productos
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT IdProducto, Nombre, CantidadActual, Estatus, ImagenRuta
        FROM Productos_01
    """)
    productos = cur.fetchall()

    return render_template("admin_panel.html", productos=productos)


@app.route("/producto/entrada/<int:id_prod>", methods=["POST"])
@login_requerido
@solo_admin
def entrada_inventario(id_prod):
    cantidad = int(request.form["cantidad"])
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        UPDATE Productos_01
        SET CantidadActual = CantidadActual + ?
        WHERE IdProducto = ?
    """, (cantidad, id_prod))

    cur.execute("""
    INSERT INTO Movimientos (IdProducto, TipoMovimiento, Cantidad, IdUsuario)
    VALUES (?, 'Entrada', ?, ?)
""", (id_prod, cantidad, session["id_usuario"]))


    con.commit()
    flash("Inventario aumentado", "success")
    return redirect("/admin_panel")


@app.route("/producto/baja/<int:id_prod>")
@login_requerido
@solo_admin
def baja_producto(id_prod):

    con = get_connection()
    cur = con.cursor()
    
    cur.execute("""
        UPDATE Productos_01
        SET Estatus = 0
        WHERE IdProducto = ?
    """, (id_prod, ))

    con.commit()
    flash("Producto dado de baja", "warning")
    return redirect("/admin_panel")



@app.route("/producto/activar/<int:id_prod>")
@login_requerido
@solo_admin
def activar_producto(id_prod):

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        UPDATE Productos_01
        SET Estatus = 1
        WHERE IdProducto = ?
    """, (id_prod, ))

    con.commit()
    flash("Producto activado", "success")
    return redirect("/admin_panel")

@app.route("/almacenista_panel")
@login_requerido
@solo_almacenista
def almacenista_panel():
    # Traer productos
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT IdProducto, Nombre, CantidadActual, Estatus, ImagenRuta
        FROM Productos_01
    """)
    productos = cur.fetchall()

    return render_template("almacenista_panel.html", productos=productos)


@app.route("/producto/salida/<int:id_prod>", methods=["POST"])
@login_requerido
@solo_almacenista
def salida_inventario(id_prod):
    cantidad = int(request.form["cantidad"])
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        UPDATE Productos_01
        SET CantidadActual = CantidadActual - ?
        WHERE IdProducto = ?
    """, (cantidad, id_prod))
    
    cur.execute("""
    INSERT INTO Movimientos (IdProducto, TipoMovimiento, Cantidad, IdUsuario)
    VALUES (?, 'Salida', ?, ?)
""", (id_prod, cantidad, session["id_usuario"]))



    con.commit()
    flash("Inventario restado", "warning")
    return redirect("/almacenista_panel")

@app.route("/movimientos")
@login_requerido
@solo_admin
def movimientos():
    tipo = request.args.get("tipo")  # None, 'Entrada', 'Salida'

    con = get_connection()
    cur = con.cursor()

    query = """
        SELECT M.IdMovimiento,
        P.Nombre AS Producto,
        M.TipoMovimiento,
        M.Cantidad,
        M.FechaHora,
        U.IdUsuario AS Usuario
        FROM Movimientos M
        JOIN Productos_01 P ON M.IdProducto = P.IdProducto
        JOIN Usuarios U ON M.IdUsuario = U.IdUsuario
    """

    params = []
    if tipo:
        query += " WHERE M.TipoMovimiento = ?"
        params.append(tipo)

    query += " ORDER BY M.FechaHora DESC"

    cur.execute(query, params)
    movimientos = cur.fetchall()

    return render_template("movimientos.html", movimientos=movimientos, tipo=tipo)


# ==============================================
#   EJECUTAR APP
# ==============================================

if __name__ == '__main__':
    app.run(debug=True)
