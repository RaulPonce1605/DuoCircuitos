"""`uv run python -m app.content_import [RUTA]`: valida e importa el temario a la base."""

import asyncio
import io
import sys
from pathlib import Path

from app.content_import.importer import SyllabusInvalidError, import_syllabus
from app.content_import.validate import DEFAULT_SYLLABUS_DIR
from app.core.db import get_engine, get_session_factory


async def _run(root: Path) -> int:
    try:
        async with get_session_factory()() as db:
            summary = await import_syllabus(db, root)
    except SyllabusInvalidError as exc:
        print(f"No se importó nada: el temario en {root} tiene errores:")
        for error in exc.errors:
            print(f"  - {error}")
        return 1
    finally:
        await get_engine().dispose()

    if not summary.changed:
        print("Temario importado: sin cambios.")
        return 0
    print("Temario importado:")
    for label, bucket in (
        ("nuevos", summary.created),
        ("actualizados", summary.updated),
        ("archivados", summary.archived),
    ):
        if bucket:
            detail = ", ".join(f"{table}: {count}" for table, count in sorted(bucket.items()))
            print(f"  {label}: {detail}")
    return 0


def main() -> int:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows no usa UTF-8
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SYLLABUS_DIR
    return asyncio.run(_run(root))


if __name__ == "__main__":
    sys.exit(main())
