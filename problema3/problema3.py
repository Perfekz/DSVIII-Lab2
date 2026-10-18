from utilidades.controlMedicion import ControlMedicion

control = ControlMedicion(
    archivoEntrada="sensores.csv",
    archivoAlertas="alertas.json",
    archivoResumen="resumen_sensores.csv",
    archivoSProcesados="sensores_procesados.json",
)

    # 1. Leer el CSV y guardar las mediciones en una lista de objetos Medicion
control.leer_mediciones()

    # 2. Validar con Polars (identificadores, humedad 0-100, registros incompletos)
control.validar_mediciones()

    # 3. Calcular estado, alertas y resumen
control.procesar()

    # 4. Exportar alertas.json, resumen_sensores.csv y sensores_procesados.json
control.exportar()

    # Reporte en consola
print(
    f"Leídas: {len(control.mediciones)} | válidas: {control.validas.height} "
    f"| rechazadas: {control.invalidos.height}"
)
if control.invalidos.height:
    print("\nRegistros rechazados:")
    print(control.invalidos)
print("\nResumen por sensor:")
print(control.resumen)
print(f"\nAlertas: {control.alertas.height}")
