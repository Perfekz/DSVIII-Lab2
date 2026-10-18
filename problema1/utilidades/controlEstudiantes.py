import csv
from modelos.estudiantes import Estudiante

class ControlEstudiante:
    def __init__(self, archivoEntrada):
        self.archivoEntrada = archivoEntrada
        self.estudiantes = []
        self.cedulas = []

    def leerArchivo(self):
        with open(self.archivoEntrada, 'r', encoding='utf-8', newline='') as archivo:
            lector = csv.reader(archivo)
            next(lector, None) #Omite el encabezado del archivo CSV

            for datos in lector:
                if len(datos) == 5:
                    cedula, nombre, parcial1, parcial2, proyecto = datos
                    #Valida que las notas sean números enteros
                    try:
                        parcial1 = int(parcial1)
                        parcial2 = int(parcial2)
                        proyecto = int(proyecto)
                    except ValueError:
                        raise ValueError("Las notas deben ser números enteros.")
                    
                    notas = [parcial1, parcial2, proyecto]
                    self.validarNota(notas)
                    self.validarCedula(cedula)
                    self.cedulas.append(cedula)
                    self.estudiantes.append(Estudiante(cedula, nombre, parcial1, parcial2, proyecto))
                else:
                    raise ValueError("Un registro no contiene cinco campos.")
        
    def validarNota(self, notas):
        for nota in notas:
            if nota < 0 or nota > 100:
                raise ValueError("La nota debe estar entre 0 y 100.")

    #Valida que la cédula sea única, tenga dos guiones y entre 7 y 11 dígitos
    def validarCedula(self, cedula):
        if cedula in self.cedulas:
            raise ValueError("La cédula ya ha sido registrada.")
        if cedula.count('-') != 2:
            raise ValueError("La cédula debe contener dos guiones.")

        cantidad = 0
        for caracter in cedula:
            if caracter.isdigit():
                cantidad += 1
        if cantidad < 7 or cantidad > 11:
            raise ValueError("La cédula debe tener entre 7 y 11 dígitos.")

    def calcularNotaFinal(self, estudiante):
        estudiante.notaFinal = ((estudiante.parcial1 * 0.30) + (estudiante.parcial2 * 0.30) + (estudiante.proyecto * 0.40))
        return estudiante.notaFinal

    def clasificarEstudiante(self, estudiante):
        if estudiante.notaFinal >= 71:
            estudiante.clasificacion = "APROBADO"
        else:
            estudiante.clasificacion = "REPROBADO"

    def contarClasificados(self):
        aprobados = 0
        reprobados = 0
        for estudiante in self.estudiantes:
            if estudiante.clasificacion == "APROBADO":
                aprobados += 1
            elif estudiante.clasificacion == "REPROBADO":
                reprobados += 1
        return aprobados, reprobados

    def calcularPromedioGeneral(self):
        suma = 0
        for estudiante in self.estudiantes:
            suma += estudiante.notaFinal
        if len(self.estudiantes) > 0:
            promedio = suma / len(self.estudiantes)
            return promedio
        return 0

    def determinarMayorNota(self):
        if not self.estudiantes:
            return 0
        
        mayor = self.estudiantes[0].notaFinal 
        for estudiante in self.estudiantes:
            if estudiante.notaFinal > mayor:
                mayor = estudiante.notaFinal
        return mayor

    def determinarMenorNota(self):
        if not self.estudiantes:
            return 0
        
        menor = self.estudiantes[0].notaFinal 
        for estudiante in self.estudiantes:
            if estudiante.notaFinal < menor:
                menor = estudiante.notaFinal
        return menor


