import os

# Valores de prueba: el CI y los integrantes no necesitan un .env para correr pytest.
os.environ.setdefault("POSTGRES_USER", "circuitos")
os.environ.setdefault("POSTGRES_PASSWORD", "circuitos")
os.environ.setdefault("POSTGRES_DB", "circuitos_test")
os.environ.setdefault("JWT_SECRET", "solo-para-pruebas")
