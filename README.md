# tasas

CLI en Python para consultar las tasas de cambio del mercado informal cubano y mostrarlas en una tabla en la terminal. Usa la [API de elTOQUE](https://eltoque.com).

```
        Tasas de cambio (mercado informal)
┏━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Moneda   ┃ Tasa (CUP) ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━┩
│ ...      │        ... │
└──────────┴────────────┘
              Fuente: elTOQUE
```

## Características

- Tabla legible en la terminal con [Rich](https://github.com/Textualize/rich).
- Validación de argumentos con [Typer](https://typer.tiangolo.com/): formato de fechas, rango máximo de 24 h y token obligatorio.
- Mensajes de error claros para los códigos `400`, `401`, `422` y `429` (incluye el `Retry-After`).
- Salida en JSON crudo con `--raw`.

## Requisitos

- Python 3.11 o superior
- Un token de la API (solicítalo en <https://tasas-token.eltoque.com/>)

## Instalación

Con [uv](https://docs.astral.sh/uv/) (recomendado), instala `tasas` como herramienta global:

```bash
uv tool install git+<url-del-repositorio>
```

O desde una copia local:

```bash
git clone <url-del-repositorio>
cd tasas
uv tool install .
```

También funciona con pip:

```bash
pip install .
```

Para desarrollo, sin instalar:

```bash
uv run tasas --help
```

## Uso

Guarda tu token en una variable de entorno:

```bash
export ELTOQUE_TOKEN="<tu_token>"
```

Tasas de las últimas 24 horas:

```bash
tasas
```

Tasas de un intervalo concreto (máximo 24 horas):

```bash
tasas --from "2022-10-27 00:00:01" --to "2022-10-27 23:59:01"
```

Ver la respuesta sin formato:

```bash
tasas --raw
```

### Opciones

| Opción          | Descripción                                                   |
| --------------- | ------------------------------------------------------------- |
| `--token`, `-t` | Token Bearer. Por defecto se lee de `ELTOQUE_TOKEN`.          |
| `--from`        | Inicio del intervalo, formato `YYYY-MM-DD HH:MM:SS`.          |
| `--to`          | Fin del intervalo. Debe usarse junto con `--from`.            |
| `--timeout`     | Tiempo máximo de espera en segundos (1 a 60, por defecto 10). |
| `--raw`         | Imprime el JSON sin formato.                                  |
| `--help`        | Muestra la ayuda.                                             |

## Errores

| Código | Significado                                                |
| ------ | ---------------------------------------------------------- |
| `400`  | El intervalo de tiempo supera las 24 horas.                |
| `401`  | Token incorrecto o expirado.                               |
| `422`  | Entidad no procesable: revisa el token.                    |
| `429`  | Límite de peticiones superado (60 por minuto por defecto). |

## Límites de uso

La API limita las peticiones por token: 60 por minuto y un máximo de 10 por segundo. Las tasas se calculan sobre ventanas de 24 horas, así que no hace falta consultarlas con más frecuencia.

## Aviso y términos de uso

- Los datos pertenecen a [elTOQUE](https://eltoque.com), que debe citarse como fuente.
- Las tasas son **referenciales**: se calculan a partir de las medianas de ofertas de compra y venta en grupos de Telegram, WhatsApp y sitios de clasificados.
- No compartas tu token con terceros ni modifiques los datos obtenidos.
- Lee los [términos y condiciones completos](https://eltoque.com/api-tasas-de-eltoque-terminos-y-condiciones-de-uso).

Este proyecto es independiente y no está afiliado a elTOQUE.

## Licencia

MIT
