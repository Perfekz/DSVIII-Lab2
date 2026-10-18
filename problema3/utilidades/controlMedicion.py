import json
from pathlib import Path

import polars as pl

from modelos.medicion import Medicion


class ControlMedicion:
    COLUMNAS_REQUERIDAS = ("sensor", "ubicacion", "fecha", "hora", "temperatura", "humedad")
    PATRON_SENSOR = r"^S\d{2}$"  # S01, S02, ... S99
    HUM_MIN, HUM_MAX = 0.0, 100.0
    TEMP_ALERTA = 32.0  # ALERTA si temperatura > 32.0 °C
    HUM_ALERTA = 80.0   # ALERTA si humedad > 80 %

    def __init__(self, archivoEntrada, archivoAlertas, archivoResumen, archivoSProcesados):
        self.archivoEntrada = archivoEntrada
        self.archivoAlertas = archivoAlertas
        self.archivoResumen = archivoResumen
        self.archivoSProcesados = archivoSProcesados
        self.mediciones = []    # lista de objetos Medicion
        self.validas = None     # DataFrame con los registros que pasaron la validación
        self.invalidos = None   # DataFrame con los rechazados y su motivo
        self.procesados = None  # validas + columna estado
        self.alertas = None     # solo ALERTA, con columna motivo
        self.resumen = None     # estadísticas por sensor

    # 1. Lectura: CSV -> lista de Medicion (sin validar)
    @staticmethod
    def _limpiar(valor):
        """Quita espacios; un texto vacío se considera dato faltante (None)."""
        if valor is None:
            return None
        valor = valor.strip()
        return valor if valor else None

    def leer_mediciones(self):
        if not Path(self.archivoEntrada).exists():
            raise FileNotFoundError(f"No existe el archivo: {self.archivoEntrada}")

        # lectura con Polars: infer_schema=False para que no intente convertir tipos automáticamente
        df = pl.read_csv(self.archivoEntrada, infer_schema=False)
        
        faltantes = set(self.COLUMNAS_REQUERIDAS) - set(df.columns)
        if faltantes:
            raise ValueError(f"Faltan columnas en el CSV: {sorted(faltantes)}")

        self.mediciones = []  # evita duplicados si se llama más de una vez
        # start=2: la línea 1 del archivo es el encabezado
        for numero_linea, row in enumerate(df.iter_rows(named=True), start=2):
            self.mediciones.append(
                Medicion(
                    sensor=self._limpiar(row["sensor"]),
                    ubicacion=self._limpiar(row["ubicacion"]),
                    fecha=self._limpiar(row["fecha"]),
                    hora=self._limpiar(row["hora"]),
                    temperatura=self._limpiar(row["temperatura"]),
                    humedad=self._limpiar(row["humedad"]),
                    linea=numero_linea,
                )
            )
        return self.mediciones

    # 2. Validación: lista de Medicion -> DataFrame -> expresiones de Polars
    def validar_mediciones(self):
        cols = list(self.COLUMNAS_REQUERIDAS)

        esquema = {"linea": pl.Int64, **{c: pl.Utf8 for c in cols}}
        crudo = pl.DataFrame([m.to_dict() for m in self.mediciones], schema=esquema)

        # Conversión de tipos: lo que no se pueda convertir queda en null (strict=False)
        parseado = crudo.with_columns(
            pl.col("temperatura").cast(pl.Float64, strict=False).alias("temp"),
            pl.col("humedad").cast(pl.Float64, strict=False).alias("hum"),
            pl.col("fecha").str.to_date("%Y-%m-%d", strict=False).alias("fecha_dt"),
            pl.col("hora").str.to_time("%H:%M", strict=False).alias("hora_t"),
        )

        temp_ok = pl.col("temp").is_finite().fill_null(False)
        hum_ok = pl.col("hum").is_finite().fill_null(False)

        # Cada expresión devuelve un mensaje de error o null si la regla se cumple
        reglas = [
            pl.when(pl.col(c).is_null()).then(pl.lit(f"campo vacío: {c}")) for c in cols
        ] + [
            pl.when(~pl.col("sensor").str.contains(self.PATRON_SENSOR))
            .then(pl.lit("identificador de sensor inválido")),
            pl.when(pl.col("fecha").is_not_null() & pl.col("fecha_dt").is_null())
            .then(pl.lit("fecha inválida")),
            pl.when(pl.col("hora").is_not_null() & pl.col("hora_t").is_null())
            .then(pl.lit("hora inválida")),
            pl.when(pl.col("temperatura").is_not_null() & ~temp_ok)
            .then(pl.lit("temperatura no numérica")),
            pl.when(pl.col("humedad").is_not_null() & ~hum_ok)
            .then(pl.lit("humedad no numérica")),
            pl.when(
                hum_ok & ((pl.col("hum") < self.HUM_MIN) | (pl.col("hum") > self.HUM_MAX))
            ).then(pl.lit(f"humedad fuera de rango ({self.HUM_MIN:g} a {self.HUM_MAX:g})")),
        ]

        con_errores = parseado.with_columns(
            pl.concat_list(reglas).list.drop_nulls().alias("errores")
        )

        self.invalidos = con_errores.filter(pl.col("errores").list.len() > 0).select(
            "linea",
            *cols,
            pl.col("errores").list.join(" | ").alias("errores"),
        )

        self.validas = con_errores.filter(pl.col("errores").list.len() == 0).select(
            "sensor",
            "ubicacion",
            pl.col("fecha_dt").alias("fecha"),
            pl.col("hora_t").alias("hora"),
            pl.col("temp").alias("temperatura"),
            pl.col("hum").alias("humedad"),
        )

    # 3. Procesamiento: estado, alertas y resumen
    def procesar(self):
        # Columna estado
        self.procesados = self.validas.with_columns(
            pl.when(
                (pl.col("temperatura") > self.TEMP_ALERTA)
                | (pl.col("humedad") > self.HUM_ALERTA)
            )
            .then(pl.lit("ALERTA"))
            .otherwise(pl.lit("NORMAL"))
            .alias("estado")
        )

        # Filtrar alertas e indicar qué las activó
        self.alertas = self.procesados.filter(pl.col("estado") == "ALERTA").with_columns(
            pl.concat_list(
                pl.when(pl.col("temperatura") > self.TEMP_ALERTA).then(
                    pl.format(
                        f"Temperatura {{}} °C supera {self.TEMP_ALERTA} °C",
                        pl.col("temperatura"),
                    )
                ),
                pl.when(pl.col("humedad") > self.HUM_ALERTA).then(
                    pl.format(
                        f"Humedad {{}} % supera {self.HUM_ALERTA:g} %",
                        pl.col("humedad"),
                    )
                ),
            )
            .list.drop_nulls()
            .list.join(" y ")
            .alias("motivo")
        )

        # Cantidad y temperatura promedio/máxima/mínima por sensor
        por_sensor = self.procesados.group_by("sensor").agg(
            pl.len().alias("cantidad_mediciones"),
            pl.col("temperatura").mean().round(2).alias("temperatura_promedio"),
            pl.col("temperatura").max().alias("temperatura_maxima"),
            pl.col("temperatura").min().alias("temperatura_minima"),
        )

        # Humedad promedio por sensor y ubicación
        humedad = self.procesados.group_by("sensor", "ubicacion").agg(
            pl.col("humedad").mean().round(2).alias("humedad_promedio")
        )

        self.resumen = (
            por_sensor.join(humedad, on="sensor", how="left")
            .select(
                "sensor",
                "ubicacion",
                "cantidad_mediciones",
                "temperatura_promedio",
                "temperatura_maxima",
                "temperatura_minima",
                "humedad_promedio",
            )
            .sort("sensor", "ubicacion")
        )

    # 4. Exportación
    @staticmethod
    def _guardar_json(df, ruta):
        filas = df.with_columns(
            pl.col("fecha").dt.strftime("%Y-%m-%d"),
            pl.col("hora").dt.strftime("%H:%M"),
        ).to_dicts()
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(filas, f, ensure_ascii=False, indent=2)

    def exportar(self):
        self._guardar_json(self.alertas, self.archivoAlertas)
        self._guardar_json(self.procesados, self.archivoSProcesados)
        self.resumen.write_csv(self.archivoResumen)