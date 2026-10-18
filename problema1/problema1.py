from utilidades.controlEstudiantes import ControlEstudiante
from utilidades.Reportes import Reportes

archivoEntrada = 'problema1/estudiantes.csv'
archivoSalidaJson = 'problema1/estudiantes.json'
archivoSalidaTxt = 'problema1/resumen.txt'
control = ControlEstudiante(archivoEntrada)

try:
    control.leerArchivo()

    for estudiante in control.estudiantes:
        control.calcularNotaFinal(estudiante)
        control.clasificarEstudiante(estudiante)

    reporte = Reportes(
        control, archivoSalidaJson, archivoSalidaTxt
    )

    reporte.generarEstudiantes()
    reporte.generarResumen()

    print("Archivos de estudiantes generados exitosamente.")

except FileNotFoundError:
    print(f"Error: no se encontró el archivo {archivoEntrada}.")

except Exception as e:
    print(f"Error en la ejecución => {e}")



