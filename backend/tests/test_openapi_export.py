from app.openapi_export import OUTPUT, render


def test_committed_openapi_is_up_to_date() -> None:
    committed = OUTPUT.read_text(encoding="utf-8").replace("\r\n", "\n")

    assert committed == render(), (
        "backend/openapi.json está desactualizado: corre `uv run python -m app.openapi_export` "
        "y luego `npm run api:generate` en app/."
    )


def test_every_route_has_operation_id_and_tags() -> None:
    from app.main import app

    for path, methods in app.openapi()["paths"].items():
        for method, operation in methods.items():
            assert operation.get("operationId"), f"{method.upper()} {path} sin operation_id"
            assert operation.get("tags"), f"{method.upper()} {path} sin tags"
