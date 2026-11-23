import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.usefixtures("syllabus")


async def test_get_path(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.get("/path", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    first_unit = data["stages"][0]["sections"][0]["units"][0]
    assert first_unit["slug"] == "u01-ley-de-ohm"
    first = first_unit["nodes"][0]
    assert first == {
        "key": "ohm-01",
        "type": "lesson",
        "status": "available",
        "is_current": True,
        "lesson": {"slug": "ohm-01", "title": "Voltaje, corriente y resistencia"},
    }
    # Nada de la solución ni del contenido de los ejercicios viaja en el camino.
    assert "correcta" not in response.text and "solucion" not in response.text


async def test_get_path_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/path")

    assert response.status_code == 401
    assert response.json() == {"code": "invalid_token"}
