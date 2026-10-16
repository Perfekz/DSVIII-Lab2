class Estudiante: 
    def __init__(self, cedula, nombre, parcial1, parcial2, proyecto):
        self.nombre = nombre
        self.cedula = cedula
        self.parcial1 = parcial1
        self.parcial2 = parcial2
        self.proyecto = proyecto
        self.notaFinal = 0.0
        self.clasificacion = ""
