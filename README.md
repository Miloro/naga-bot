# Naga Bot

[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Discord](https://img.shields.io/badge/Discord_Bot-5865F2?logo=discord&logoColor=white)](https://discord.com/developers/docs/intro)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Google Sheets](https://img.shields.io/badge/Google_Sheets-0F9D58?logo=google-sheets&logoColor=white)](https://www.google.com/sheets/about/)

🌐 Languages:  
[![Español](https://img.shields.io/badge/🇪🇸-Español-red)](#-español)  
[![English](https://img.shields.io/badge/🇺🇸-English-blue)](#-english)

---

# 🇪🇸 Español

## 📋 Requerimientos

- [Docker](https://docs.docker.com/get-docker/)
- Docker Compose V2 — incluido en Docker Desktop (Windows/Mac) y como plugin en Linux/Raspberry Pi

> **Raspberry Pi:** asegurate de tener Docker Compose V2 instalado (no la versión vieja `docker-compose` del sistema). Ver la sección [Raspberry Pi](#-raspberry-pi) más abajo.

---

## 🚀 Cómo iniciar

### 1. Clonar el proyecto

```bash
git clone https://github.com/Miloro/naga-bot
cd naga-bot
```

### 2. Configurar credenciales

Crear el archivo `.env` en la raíz del proyecto:

```bash
TOKEN=tu_token_de_discord
ID_EXCEL=id_de_tu_hoja_de_google_sheets
HOJA_EXCEL=nombre_de_la_hoja
```

Dentro de la carpeta `bot/credentials/`, colocar el archivo `credentials.json` que otorga la API de Google.

```
naga-bot/
├── .env                          ← variables de entorno
└── bot/
    └── credentials/
        └── credentials.json      ← credenciales de Google API
```

### 3. Construir e iniciar

```bash
docker compose up --build -d
```

---

## 🤖 Comandos disponibles

### 🏆 Premios
| Comando | Descripción |
|---------|-------------|
| `/lider` | Muestra qué equipo va primero en la tabla |
| `/podio` | Muestra el podio de las casas con imágenes |

### ⚔️ Duelo a muerte
| Comando | Descripción |
|---------|-------------|
| `/duelo <monto>` | Inicia un duelo a muerte apostando NA'GA puntos |

### 🎵 Música
| Comando | Descripción |
|---------|-------------|
| `/play <url o búsqueda>` | Reproduce audio de YouTube. Acepta URL directa, URL de playlist o texto de búsqueda |
| `/stop` | Detiene la reproducción y desconecta el bot del canal de voz |

El reproductor incluye una botonera con controles: ⏮ anterior · ⏸ pausa · ▶ play · ⏭ siguiente · 🔁 bucle

---

## 📜 Logs

```bash
docker compose logs -f
```

---

## 🔄 Reiniciar / detener

```bash
# Detener
docker compose down

# Reiniciar con cambios
docker compose up --build -d
```

---

## 🍓 Raspberry Pi

La Raspberry usa arquitectura ARM, por lo que algunas librerías deben compilarse desde código fuente. El `Dockerfile` ya incluye todas las dependencias necesarias (`gcc`, `make`, `libffi-dev`, etc.), no hace falta instalar nada extra.

Lo único importante es usar **Docker Compose V2** (el comando es `docker compose` con espacio, no `docker-compose` con guión).

### Instalar Docker Compose V2 en Raspberry Pi

```bash
sudo apt-get update && sudo apt-get install -y docker-compose-plugin
```

Verificar que funciona:

```bash
docker compose version
```

### Primera vez

```bash
git clone https://github.com/Miloro/naga-bot
cd naga-bot
# Crear .env y colocar credentials.json (ver paso 2 más arriba)
docker compose up --build -d
```

El build tarda más que en x86 porque compila librerías nativas para ARM. Es normal.

### Ver logs

```bash
docker compose logs -f
```

### Autoarranque al reiniciar la Raspberry

El `docker-compose.yml` ya tiene `restart: unless-stopped`, así que el bot se reinicia automáticamente si la Raspberry se reinicia o si el bot crashea. Solo se detiene si lo parás manualmente con `docker compose down`.

---

## ✨ Notas

- Compartí la hoja de Google Sheets con el email de la cuenta de servicio (`...@....iam.gserviceaccount.com`) para que el bot tenga acceso.
- Los archivos `.env` y `credentials.json` **nunca deben subirse al repositorio** (ya están en `.gitignore`).

---

# 🇺🇸 English

## 📋 Requirements

- [Docker](https://docs.docker.com/get-docker/)
- Docker Compose V2 — included in Docker Desktop (Windows/Mac) and as a plugin on Linux/Raspberry Pi

> **Raspberry Pi:** make sure Docker Compose V2 is installed (not the old system `docker-compose`). See the [Raspberry Pi](#-raspberry-pi-1) section below.

---

## 🚀 How to start

### 1. Clone the project

```bash
git clone https://github.com/Miloro/naga-bot
cd naga-bot
```

### 2. Set up credentials

Create the `.env` file in the project root:

```bash
TOKEN=your_discord_bot_token
ID_EXCEL=your_google_sheets_id
HOJA_EXCEL=sheet_name
```

Place the `credentials.json` file (provided by the Google API) inside `bot/credentials/`.

```
naga-bot/
├── .env                          ← environment variables
└── bot/
    └── credentials/
        └── credentials.json      ← Google API credentials
```

### 3. Build and start

```bash
docker compose up --build -d
```

---

## 🤖 Available commands

### 🏆 Awards
| Command | Description |
|---------|-------------|
| `/lider` | Shows which team is leading the table |
| `/podio` | Shows the house podium with images |

### ⚔️ Duel to the death
| Command | Description |
|---------|-------------|
| `/duelo <amount>` | Starts a duel betting NA'GA points |

### 🎵 Music
| Command | Description |
|---------|-------------|
| `/play <url or search>` | Plays YouTube audio. Accepts direct URL, playlist URL, or search text |
| `/stop` | Stops playback and disconnects the bot from the voice channel |

The player includes a control panel: ⏮ previous · ⏸ pause · ▶ play · ⏭ next · 🔁 loop

---

## 📜 Logs

```bash
docker compose logs -f
```

---

## 🔄 Restart / stop

```bash
# Stop
docker compose down

# Restart with changes
docker compose up --build -d
```

---

## 🍓 Raspberry Pi

The Raspberry Pi uses ARM architecture, so some libraries need to be compiled from source. The `Dockerfile` already includes all required dependencies (`gcc`, `make`, `libffi-dev`, etc.) — no extra setup needed.

The only important thing is to use **Docker Compose V2** (the command is `docker compose` with a space, not `docker-compose` with a hyphen).

### Install Docker Compose V2 on Raspberry Pi

```bash
sudo apt-get update && sudo apt-get install -y docker-compose-plugin
```

Verify it works:

```bash
docker compose version
```

### First time setup

```bash
git clone https://github.com/Miloro/naga-bot
cd naga-bot
# Create .env and place credentials.json (see step 2 above)
docker compose up --build -d
```

The build takes longer than on x86 because it compiles native ARM libraries. This is expected.

### Logs

```bash
docker compose logs -f
```

### Auto-start on reboot

The `docker-compose.yml` already includes `restart: unless-stopped`, so the bot automatically restarts if the Raspberry Pi reboots or if the bot crashes. It only stops if you manually run `docker compose down`.

---

## ✨ Notes

- Share the Google Sheet with the service account email (`...@....iam.gserviceaccount.com`) so the bot can access it.
- The `.env` and `credentials.json` files **must never be committed to the repository** (already in `.gitignore`).
