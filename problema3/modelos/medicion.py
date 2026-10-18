class Medicion:
    def __init__(self, sensor, ubicacion, fecha, hora, temperatura, humedad, linea=None):
        self.sensor = sensor
        self.ubicacion = ubicacion
        self.fecha = fecha
        self.hora = hora
        self.temperatura = temperatura
        self.humedad = humedad
        self.linea = linea  # número de línea en el CSV, para reportar errores

    def to_dict(self):
        return {
            "linea": self.linea,
            "sensor": self.sensor,
            "ubicacion": self.ubicacion,
            "fecha": self.fecha,
            "hora": self.hora,
            "temperatura": self.temperatura,
            "humedad": self.humedad,
        }

    def __repr__(self):
        return (
            f"Medicion({self.sensor}, {self.ubicacion}, {self.fecha} {self.hora}, "
            f"temp={self.temperatura}, hum={self.humedad})"
        )