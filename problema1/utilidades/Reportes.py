import json

class Reportes:
    def __init__(self, control, archivoSalidaJson, archivoSalidaTxt):
        self.control = control
        self.archivoSalidaJson = archivoSalidaJson
        self.archivoSalidaTxt = archivoSalidaTxt

    #Genera un archivo JSON con los registros, nota final y condición de los estudiantes.
    def generarEstudiantes(self):
        datos = []
        for estudiante in self.control.estudiantes:
            registro = {
                "cedula": estudiante.cedula,
                "nombre": estudiante.nombre,
                "parcial1": estudiante.parcial1,
                "parcial2": estudiante.parcial2,
                "proyecto": estudiante.proyecto,
                "notaFinal": estudiante.notaFinal,
                "clasificacion": estudiante.clasificacion
            }
            datos.append(registro)
        with open(self.archivoSalidaJson, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

    #Genera un archivo txt con los indicadores del grupo.
    def generarResumen(self):
        promedio = self.control.calcularPromedioGeneral()
        mayor = self.control.determinarMayorNota()
        menor = self.control.determinarMenorNota()
        aprobados, reprobados = self.control.contarClasificados()
        with open(self.archivoSalidaTxt, 'w', encoding='utf-8') as archivo:
            archivo.write(f"Resumen de Estudiantes\n")
            archivo.write(f"---------------------\n")
            archivo.write(f"Promedio General: {promedio:.2f}\n")
            archivo.write(f"Mayor Nota Final: {mayor:.2f}\n")
            archivo.write(f"Menor Nota Final: {menor:.2f}\n")
            archivo.write(f"Cantidad de Aprobados: {aprobados}\n")
            archivo.write(f"Cantidad de Reprobados: {reprobados}\n")
