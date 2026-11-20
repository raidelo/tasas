"""Show elTOQUE informal exchange rates (GET /v1/trmi) in a table."""

from datetime import datetime, timedelta
from typing import Annotated, NoReturn

import httpx
import typer
from rich.console import Console
from rich.table import Table

from tasas.constants import BASE_URL, DATE_FMT, TOKEN_ENV

app = typer.Typer(add_completion=False, help="Tasas de elTOQUE en una tabla.")
console = Console()
err = Console(stderr=True)


def fail(msg: str) -> NoReturn:
    err.print(f"[red]Error:[/red] {msg}")
    raise typer.Exit(1)


def validate_range(date_from: datetime | None, date_to: datetime | None) -> None:
    if (date_from is None) != (date_to is None):
        raise typer.BadParameter("--from y --to deben usarse juntos")
    if date_from and date_to:
        if date_to <= date_from:
            raise typer.BadParameter("--to debe ser posterior a --from")
        if date_to - date_from > timedelta(hours=24):
            raise typer.BadParameter("el intervalo no puede superar 24 horas")


def fetch(
    token: str, date_from: datetime | None, date_to: datetime | None, timeout: float
) -> dict:
    params = {}
    if date_from and date_to:
        params = {
            "date_from": date_from.strftime(DATE_FMT),
            "date_to": date_to.strftime(DATE_FMT),
        }
    try:
        r = httpx.get(
            f"{BASE_URL}/v1/trmi",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=timeout,
        )
    except httpx.HTTPError as e:
        fail(f"no se pudo conectar: {e}")

    match r.status_code:
        case 200:
            return r.json()
        case 400:
            fail("intervalo de tiempo inválido (debe ser < 24 h)")
        case 401:
            fail("token incorrecto o expirado")
        case 422:
            fail("entidad no procesable: revisa el token")
        case 429:
            wait = r.headers.get("Retry-After", "?")
            fail(f"límite de peticiones superado, reintenta en {wait}s")
        case _:
            fail(f"respuesta inesperada {r.status_code}: {r.text[:200]}")


@app.command()
def _main(
    token: Annotated[
        str,
        typer.Option("--token", "-t", envvar=TOKEN_ENV, help="Token Bearer de la API."),
    ],
    date_from: Annotated[
        datetime | None,
        typer.Option(
            "--from", formats=[DATE_FMT], help=f"Inicio ({DATE_FMT.replace('%', '')})."
        ),
    ] = None,
    date_to: Annotated[
        datetime | None,
        typer.Option("--to", formats=[DATE_FMT], help="Fin del intervalo."),
    ] = None,
    timeout: Annotated[
        float, typer.Option(min=1, max=60, help="Timeout en segundos.")
    ] = 10,
    raw: Annotated[
        bool, typer.Option("--raw", help="Imprime el JSON sin formato.")
    ] = False,
) -> None:
    validate_range(date_from, date_to)
    data = fetch(token, date_from, date_to, timeout)

    if raw:
        console.print_json(data=data)
        raise typer.Exit()

    # Response schema is not in the spec; handle {"tasas": {...}} or a flat dict.
    rates = data.get("tasas", data) if isinstance(data, dict) else {}
    rates = {k: v for k, v in rates.items() if isinstance(v, (int, float))}
    if not rates:
        fail("no pude interpretar la respuesta; prueba con --raw")

    table = Table(title="Tasas de cambio (mercado informal)", caption="Fuente: elTOQUE")
    table.add_column("Moneda", style="cyan")
    table.add_column("Tasa (CUP)", justify="right", style="green")
    for cur, value in sorted(rates.items()):
        table.add_row(cur, f"{value:,.2f}")
    console.print(table)

    if isinstance(data, dict) and (d := data.get("date")):
        console.print(f"[dim]Fecha: {d}[/dim]")


def main() -> None:
    app()
