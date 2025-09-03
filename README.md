# Naga Bot

[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Discord](https://img.shields.io/badge/Discord_Bot-5865F2?logo=discord&logoColor=white)](https://discord.com/developers/docs/intro)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

🌐 Languages:  
[![Español](https://img.shields.io/badge/🇪🇸-Español-red)](#-español)  
[![English](https://img.shields.io/badge/🇺🇸-English-blue)](#-english)


---

# 🇪🇸 Español

## 📋 Requerimientos
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 🚀 Cómo iniciar

1. **Clonar el proyecto**
   ```bash
   git clone https://github.com/Miloro/naga-bot
   cd naga-bot
   ```

2. **Configurar credenciales**
   - Dentro de la carpeta `bot`, crear una carpeta llamada `credentials`.
   - Colocar dentro el archivo `credentials.json` que te proporciona la API de Google Drive.
   - También en la carpeta `credentials` crear un archivo `config.py` con el siguiente contenido:

   ```python
   TOKEN = "YOUR_DISCORD_BOT_TOKEN"

   id_excel = "ID_DE_TU_EXCEL_GOOGLE_DRIVE"
   hoja_excel = "NOMBRE_DE_LA_HOJA"
   ```

3. **Construir e iniciar los contenedores**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

---

## 📜 Logs del bot
Si deseas visualizar los logs en tiempo real:

```bash
docker-compose logs -f
```

---

## ✨ Notas
- Asegúrate de tener permisos en la API de Google Drive para que el bot pueda acceder a tu hoja de cálculo.
- Los archivos `credentials.json` y `credentials`  **no debe compartirse públicamente**.

---

# 🇺🇸 English

## 📋 Requirements
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 🚀 How to start

1. **Clone the project**
   ```bash
   git clone https://github.com/Miloro/naga-bot
   cd naga-bot
   ```

2. **Set up credentials**
   - Inside the `bot` folder, create a folder named `credentials`.  
   - Place the `credentials.json` file (provided by the Google Drive API) inside it.  
   - Also in the `credentials` folder, create a file `config.py` with the following content:  

   ```python
   TOKEN = "YOUR_DISCORD_BOT_TOKEN"

   id_excel = "YOUR_GOOGLE_DRIVE_EXCEL_ID"
   hoja_excel = "SHEET_NAME"
   ```

3. **Build and start containers**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

---

## 📜 Bot logs
If you want to view logs in real time:

```bash
docker-compose logs -f
```

---

## ✨ Notes
- Make sure you have the proper Google Drive API permissions so the bot can access your spreadsheet.  
- The `credentials.json` and `credentials` files **must never be shared publicly**.  
