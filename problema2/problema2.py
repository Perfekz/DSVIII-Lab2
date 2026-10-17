import csv
import json
import os

# funciones de respaldo

def leerJson(archivo):
    with open(archivo, "r") as archivo_json:
        inventario = json.load(archivo_json)
    return inventario 

def guardarJson(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def iniciar_inventario():

    if not os.path.exists(ARCHIVO_INVENTARIO):
        raise FileNotFoundError(f"No existe {ARCHIVO_INVENTARIO}")

    if not os.path.exists(ARCHIVO_ACTUALIZADO) or os.path.getsize(ARCHIVO_ACTUALIZADO) == 0:
        datos_originales = leerJson(ARCHIVO_INVENTARIO)
        guardarJson(ARCHIVO_ACTUALIZADO, datos_originales)

    return leerJson(ARCHIVO_ACTUALIZADO)
    
def capturar_movimiento(movimientos, codigo, cantidad, tipo, existencia_final=None):
    """Agrega un movimiento ('entrada' o 'salida') a la lista compartida."""
    if tipo not in ("entrada", "salida"):
        raise ValueError("El tipo debe ser 'entrada' o 'salida'")
    movimientos.append({"codigo": codigo, "cantidad": cantidad, "tipo": tipo, "existencia final": existencia_final})


def exportar_movimientos(movimientos, archivo_csv):
  
    with open(archivo_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["codigo", "tipo", "cantidad", "existencia final"])
        for m in movimientos:
            writer.writerow([m["codigo"], m["tipo"], m["cantidad"], m["existencia final"]])

def exportar_invAc_como_csv(inventario, archivo_csv):
    with open(archivo_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["codigo", "producto", "cantidad", "precio"])
        for producto in inventario:
            writer.writerow([producto["codigo"], producto["producto"], producto["cantidad"], producto["precio"]])

# utilidad

def listar_productos(inventario):
    print("Listado de productos:")
    for producto in inventario:
        print(f"Código: {producto['codigo']}, producto: {producto['producto']}, cantidad: {producto['cantidad']}, Precio: {producto['precio']}")

def obtenerProductoPorCodigo(inventario, codigo):
    for producto in inventario:
        if producto['codigo'] == codigo:
            return producto
    return None

def registrar_entrada(inventario, codigo, cantidad):
    producto = obtenerProductoPorCodigo(inventario, codigo)
    cantidadActual = producto['cantidad'] if producto else 0
    if producto:
        if cantidad < 0:
            print("Error: La cantidad de entrada no puede ser negativa.")
            return
        producto['cantidad'] += cantidad
        print(f"\nEntrada registrada: {producto['producto']}, Cantidad: {cantidad}, Existencia actual: {cantidadActual + cantidad}")
        capturar_movimiento(movimientos, codigo, cantidad, "entrada", cantidadActual + cantidad)
    else:
        print("Producto no encontrado.")

def registrar_salida(inventario, codigo, cantidad):
    if cantidad < 0:
        print("Error: La cantidad de salida no puede ser negativa.")
        return
    producto = obtenerProductoPorCodigo(inventario, codigo)
    cantidadActual = producto['cantidad'] if producto else 0
    if producto:    
        if producto['cantidad'] >= cantidad:
            producto['cantidad'] -= cantidad
            print(f"\nSalida registrada: {producto['producto']}, Cantidad: {cantidad}, Existencia actual: {cantidadActual - cantidad}")
            capturar_movimiento(movimientos, codigo, cantidad, "salida", cantidadActual - cantidad)
        else:
            print("Error: No hay suficiente stock para realizar la salida.")
    else:
        print("Producto no encontrado.")

def calcular_total_inventario(inventario):
    total = sum(producto['cantidad'] * producto['precio'] for producto in inventario)
    return total

def calcular_productos_bajos_stock(inventario, umbral=15):
    productos_bajos = [producto for producto in inventario if producto['cantidad'] < umbral]
    return productos_bajos


ARCHIVO_INVENTARIO = "problema2/inventario.json"
ARCHIVO_ACTUALIZADO = "problema2/inventario_actualizado.json"
ARCHIVO_CSV = "problema2/inventario.csv"
ARCHIVO_MOVIMIENTOS = "problema2/movimientos.csv"
movimientos = []

try:
    inventario = iniciar_inventario()
except FileNotFoundError:
    print(f"Error al leer los archivos {ARCHIVO_INVENTARIO} o {ARCHIVO_ACTUALIZADO}. Asegúrese de que existan.")


print("Bienvenido al sistema de inventario de la tienda\n.")
while True:
    print(
        "\nSeleccione una de las siguientes opciones:\n"
        "1. Listar productos\n"
        "2. Buscar producto por código\n"
        "3. Registrar entrada de productos\n"
        "4. Registrar salida de productos\n"
        "5. Mostrar Cálculos (Total de Inventario, Productos con menos de 15 unidades)\n"
        "6. Exportar Movimientos\n"
        "7. Guardar y Salir del sistema de inventario"
    )

    opcion = input("Ingrese el número de la opción deseada: ")

    match opcion:
        case "1":
            listar_productos(inventario)
        case "2":
            producto = obtenerProductoPorCodigo(
                inventario,
                input("Ingrese el código del producto a buscar: ")
            )
            if producto:
                print(
                    f"Producto encontrado: {producto['producto']}, "
                    f"Cantidad: {producto['cantidad']}, Precio: {producto['precio']}"
                )
            else:
                print("Producto no encontrado.")
        case "3":
            registrar_entrada(
                inventario,
                input("Ingrese el código del producto: "),
                int(input("Ingrese la cantidad a registrar: "))
            )
        case "4":
            registrar_salida(
                inventario,
                input("Ingrese el código del producto: "),
                int(input("Ingrese la cantidad a registrar: "))
            )
        case "5":
            total_inventario = calcular_total_inventario(inventario)
            productos_bajos_stock = calcular_productos_bajos_stock(inventario)
            print(f"Total de inventario: {total_inventario}")
            print("Productos con menos de 15 unidades:\n")
            for producto in productos_bajos_stock:
                print(f"- {producto['producto']}: {producto['cantidad']} unidades")
        
        case "6":
            exportar_movimientos(movimientos, ARCHIVO_MOVIMIENTOS)
            print("exportando movimientos a CSV...")

        case "7":
            print("\nGuardando cambios en inventario.csv...")
            exportar_invAc_como_csv(inventario, ARCHIVO_CSV)
            print(f"Inventario guardado en {ARCHIVO_CSV}.\n")

            print("\nGuardando cambios en inventario.json...")
            guardarJson(ARCHIVO_INVENTARIO, inventario)
            print(f"Inventario guardado en {ARCHIVO_INVENTARIO}.")

            if os.path.exists(ARCHIVO_ACTUALIZADO):
                os.remove(ARCHIVO_ACTUALIZADO)
                print(f"Archivo temporal eliminado: {ARCHIVO_ACTUALIZADO}.")

            print("Saliendo del sistema de inventario. ¡Hasta luego!")

            break
        case _:
            print("Opción no válida. Seleccione una opción del 1 al 8.")
