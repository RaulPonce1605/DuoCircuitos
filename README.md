# Circuitos

App de aprendizaje gamificado de circuitos eléctricos para web, iOS y Android: un camino de lecciones cortas con ejercicios teóricos y de cálculo, tutor con IA, EXP, rachas y ligas.

> Proyecto en preparación: los frameworks aún no están inicializados. La guía completa del producto, el stack y las reglas está en [`CLAUDE.md`](CLAUDE.md).

## Organización del repo

| Carpeta | Qué contiene | Guía |
|---|---|---|
| `app/` | App Expo (React Native + Expo Router, TypeScript) | [`app/CLAUDE.md`](app/CLAUDE.md) |
| `backend/` | API FastAPI + PostgreSQL | [`backend/CLAUDE.md`](backend/CLAUDE.md) |
| `contenido/` | Temario: lecciones y ejercicios en Markdown | [`contenido/README.md`](contenido/README.md) |
| `docs/referencias/` | Capturas de referencia (solo local, no se versionan) | — |

## Flujo de trabajo

1. Actualiza `main`: `git switch main && git pull`.
2. Crea tu rama: `git switch -c feature/<descripcion-corta>`.
3. Commits convencionales: `feat(backend): ...`, `fix(app): ...`, `feat(contenido): ...`.
4. Pasa lint y pruebas del módulo.
5. Sube la rama y abre un PR a `main`. Otro integrante lo revisa y lo aprueba.

Nunca se hace commit directo a `main`.

## Instalación del entorno

### 1. Qué hay que instalar

Cada integrante necesita 6 herramientas. Python 3.12 no se instala por separado: lo instala uv.

| Herramienta | Versión mínima | Para qué sirve |
|---|---|---|
| Git | 2.40 | Control de versiones, ramas `feature/*` y PRs |
| GitHub CLI (`gh`) | 2.40 | Clonar, abrir y revisar PRs desde la terminal |
| Node.js (LTS) | 20 | Correr Expo y la app (incluye `npm`) |
| uv | 0.5 | Manejar Python 3.12 y las dependencias del backend |
| Docker Desktop | 4.30 (Compose v2) | Levantar PostgreSQL y el backend con `docker compose` |
| VS Code | reciente | Editor del equipo, con Claude Code |

Para probar en el teléfono: la app **Expo Go** (App Store / Google Play). Los emuladores (Android Studio, Xcode) son opcionales.

### 2. Requisitos del sistema

| Sistema | Versión | Requisito extra |
|---|---|---|
| Windows | 10 22H2 u 11, 64 bits | WSL 2 y virtualización activada en BIOS (para Docker) |
| macOS | 13 Ventura o superior | Homebrew instalado |
| Linux | Ubuntu 22.04+ o equivalente | `curl` y permisos de `sudo` |

Mínimo 8 GB de RAM y 15 GB libres: Docker y el bundler de Expo consumen bastante.

Antes de instalar, revisa qué tienes ya. Si una herramienta responde con una versión igual o mayor a la mínima, sáltate su paso:

```
git --version
gh --version
node --version
npm --version
uv --version
docker --version
docker compose version
code --version
```

### 3. Instalación paso a paso

Instala solo lo que te falte. Al terminar, **cierra y vuelve a abrir la terminal** para que se actualice el PATH.

#### Windows (PowerShell)

1. Activa WSL 2 (requerido por Docker). Abre PowerShell **como administrador**, ejecuta esto y reinicia:

   ```
   wsl --install
   ```

2. Instala las herramientas con winget (PowerShell normal):

   ```
   winget install -e --id Git.Git
   winget install -e --id GitHub.cli
   winget install -e --id OpenJS.NodeJS.LTS
   winget install -e --id astral-sh.uv
   winget install -e --id Docker.DockerDesktop
   winget install -e --id Microsoft.VisualStudioCode
   ```

3. Abre Docker Desktop una vez, acepta los términos y espera a que diga *Engine running*.

#### macOS (Terminal)

```
brew install git gh node uv
brew install --cask docker visual-studio-code
```

Abre Docker Desktop una vez desde Aplicaciones y espera a que arranque.

#### Linux (Ubuntu / Debian)

```
sudo apt update && sudo apt install -y git gh
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

Cierra sesión y vuelve a entrar para usar `docker` sin `sudo`. VS Code se instala desde [code.visualstudio.com](https://code.visualstudio.com/).

#### Todos los sistemas: Python, Git y GitHub

```
uv python install 3.12
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@ejemplo.com"
gh auth login
```

En `gh auth login` elige *GitHub.com*, *HTTPS* y *Login with a web browser*. El correo de Git debe ser el mismo de tu cuenta de GitHub para que tus commits aparezcan a tu nombre.

### 4. VS Code y Claude Code

```
code --install-extension anthropic.claude-code
code --install-extension ms-python.python
code --install-extension charliermarsh.ruff
code --install-extension ms-python.mypy-type-checker
code --install-extension dbaeumer.vscode-eslint
code --install-extension expo.vscode-expo-tools
code --install-extension ms-azuretools.vscode-docker
code --install-extension redhat.vscode-yaml
```

| Extensión | Para qué |
|---|---|
| Claude Code | Programar con Claude guiado por los `CLAUDE.md` |
| Python, Ruff, Mypy | Backend: autocompletado, lint y tipos |
| ESLint, Expo Tools | App: lint y autocompletado de `app.json` |
| Docker | Ver y controlar los contenedores |
| YAML | Validar `camino.yaml` y el frontmatter de lecciones |

Si también quieres Claude Code en la terminal:

- Windows (PowerShell): `irm https://claude.ai/install.ps1 | iex`
- macOS / Linux: `curl -fsSL https://claude.ai/install.sh | bash`

Abre **la carpeta raíz** `proyectofinalcircuitos` en VS Code (no `app/` ni `backend/` sueltas). Así Claude lee el `CLAUDE.md` raíz y el del módulo en el que trabajes, y aplica los permisos de `.claude/settings.json`. Pídele las tareas usando los checklists de cada módulo ("nuevo endpoint", "nueva pantalla", "nuevo tipo de ejercicio", "nueva lección de contenido").

### 5. Preparar el proyecto

Los pasos 3 a 5 funcionan cuando ya existan `backend/pyproject.toml`, `app/package.json` y `docker-compose.yml`. Hoy el repo solo tiene la estructura y las guías.

1. Clona el repo ([github.com/RaulPonce1605/DuoCircuitos](https://github.com/RaulPonce1605/DuoCircuitos)) en una carpeta llamada `proyectofinalcircuitos` y entra a ella:

   ```
   gh repo clone RaulPonce1605/DuoCircuitos proyectofinalcircuitos
   cd proyectofinalcircuitos
   ```

2. Crea tu `.env` a partir del ejemplo y pide los valores secretos al equipo (nunca por el repo):

   ```
   cp backend/.env.example backend/.env
   ```

   En PowerShell: `Copy-Item backend/.env.example backend/.env`

3. Base de datos y backend:

   ```
   docker compose up -d db
   cd backend
   uv sync
   uv run alembic upgrade head
   uv run fastapi dev app/main.py
   ```

4. App (en otra terminal):

   ```
   cd app
   npm install
   npx expo start
   ```

   Presiona `w` para abrir en el navegador o escanea el QR con Expo Go. El teléfono y la computadora deben estar en la misma red Wi-Fi.

5. Todo con Docker (alternativa al paso 3): `docker compose up -d`

### 6. Verificación

- [ ] `uv python find 3.12` devuelve una ruta
- [ ] `docker run --rm hello-world` imprime *Hello from Docker!*
- [ ] `gh auth status` dice *Logged in*
- [ ] `node --version` es 20 o mayor
- [ ] VS Code abre la carpeta raíz y Claude Code responde

### 7. Problemas comunes

| Síntoma | Solución |
|---|---|
| `uv` o `node` *no se reconoce como comando* | Cierra y abre la terminal (o VS Code completo) para recargar el PATH |
| Docker: *WSL 2 installation is incomplete* | `wsl --update` como administrador y reinicia |
| Docker: *virtualization not enabled* | Activa VT-x / AMD-V (SVM) en la BIOS |
| PowerShell: *la ejecución de scripts está deshabilitada* | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Expo Go no conecta con la PC | Misma Wi-Fi; si no, `npx expo start --tunnel` |
| Puerto 5432 ocupado | Hay otro PostgreSQL corriendo: deténlo o cambia el puerto en `docker-compose.yml` |
| Commits sin tu foto en GitHub | El `user.email` de Git no coincide con tu cuenta de GitHub |
