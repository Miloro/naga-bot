import os
import discord
from discord import app_commands
import yt_dlp
import asyncio
from collections import deque
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}


class Song:
    def __init__(self, title: str, webpage_url: str, audio_url: str = None):
        self.title = title
        self.webpage_url = webpage_url
        self.audio_url = audio_url


async def _in_executor(func):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func)


def _get_spotify_client():
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    if not client_id or not client_secret:
        return None
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    ))


async def spotify_to_songs(url: str) -> list[Song]:
    def _extract():
        sp = _get_spotify_client()
        if not sp:
            return []

        songs = []

        if '/track/' in url:
            track_id = url.split('/track/')[1].split('?')[0]
            track = sp.track(track_id)
            artist = track['artists'][0]['name']
            title = track['name']
            songs.append(Song(
                title=f"{artist} - {title}",
                webpage_url=f"ytsearch1:{artist} - {title}"
            ))

        elif '/playlist/' in url:
            playlist_id = url.split('/playlist/')[1].split('?')[0]
            results = sp.playlist_tracks(playlist_id)
            while results:
                for item in results['items']:
                    track = item.get('track')
                    if not track:
                        continue
                    artist = track['artists'][0]['name']
                    title = track['name']
                    songs.append(Song(
                        title=f"{artist} - {title}",
                        webpage_url=f"ytsearch1:{artist} - {title}"
                    ))
                results = sp.next(results) if results.get('next') else None

        elif '/album/' in url:
            album_id = url.split('/album/')[1].split('?')[0]
            results = sp.album(album_id)['tracks']
            while results:
                for track in results['items']:
                    artist = track['artists'][0]['name']
                    title = track['name']
                    songs.append(Song(
                        title=f"{artist} - {title}",
                        webpage_url=f"ytsearch1:{artist} - {title}"
                    ))
                results = sp.next(results) if results.get('next') else None

        return songs

    return await _in_executor(_extract)


async def extract_songs(query: str) -> list[Song]:
    if 'open.spotify.com' in query:
        return await spotify_to_songs(query)

    is_url = query.startswith(('http://', 'https://'))
    search_query = query if is_url else f"ytsearch:{query}"

    def _extract():
        opts = {**YTDL_OPTIONS, 'extract_flat': 'in_playlist', 'noplaylist': False}
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(search_query, download=False)

    try:
        info = await _in_executor(_extract)
    except yt_dlp.utils.DownloadError:
        return []

    if not info:
        return []

    if 'entries' in info:
        songs = []
        for entry in info['entries']:
            if not entry:
                continue
            vid_id = entry.get('id')
            webpage = f"https://www.youtube.com/watch?v={vid_id}" if vid_id else entry.get('url', '')
            songs.append(Song(title=entry.get('title', 'Unknown'), webpage_url=webpage))
        return songs

    return [Song(
        title=info.get('title', 'Unknown'),
        webpage_url=info.get('webpage_url', query),
        audio_url=info.get('url'),
    )]


async def resolve_song(song: Song) -> bool:
    if song.audio_url:
        return True

    def _extract():
        with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
            return ydl.extract_info(song.webpage_url, download=False)

    try:
        info = await _in_executor(_extract)
        # ytsearch puede devolver una estructura con entries
        if info and 'entries' in info:
            info = info['entries'][0] if info['entries'] else None
        if info and 'url' in info:
            song.audio_url = info['url']
            song.title = info.get('title', song.title)
            return True
    except Exception:
        pass
    return False


class PlayerControls(discord.ui.View):
    def __init__(self, player: 'MusicPlayer'):
        super().__init__(timeout=None)
        self.player = player
        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.label == 'Bucle':
                child.style = discord.ButtonStyle.success if player.loop_current else discord.ButtonStyle.secondary

    @discord.ui.button(emoji="⏮", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.player.go_previous()

    @discord.ui.button(emoji="⏸", label="Pausa", style=discord.ButtonStyle.primary)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.pause()
        await interaction.response.defer()

    @discord.ui.button(emoji="▶", label="Play", style=discord.ButtonStyle.success)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.resume()
        await interaction.response.defer()

    @discord.ui.button(emoji="⏭", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.player.skip()

    @discord.ui.button(emoji="🔁", label="Bucle", style=discord.ButtonStyle.secondary)
    async def loop_toggle(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.loop_current = not self.player.loop_current
        button.style = discord.ButtonStyle.success if self.player.loop_current else discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)


class MusicPlayer:
    def __init__(self, vc: discord.VoiceClient, loop: asyncio.AbstractEventLoop):
        self.vc = vc
        self.loop = loop
        self.queue: deque[Song] = deque()
        self.history: deque[Song] = deque(maxlen=20)
        self.current: Song | None = None
        self.message: discord.Message | None = None
        self.stopped = False
        self.loop_current = False

    def _after(self, error):
        if not self.stopped:
            asyncio.run_coroutine_threadsafe(self.play_next(), self.loop)

    async def play_next(self):
        if self.stopped:
            return

        if self.loop_current and self.current:
            self.queue.appendleft(self.current)
        elif self.current:
            self.history.append(self.current)

        if not self.queue:
            self.current = None
            if self.message:
                try:
                    await self.message.edit(content="Cola vacía. Reproducción terminada.", view=None)
                except Exception:
                    pass
            return

        song = self.queue.popleft()

        if not await resolve_song(song):
            await self.play_next()
            return

        self.current = song
        source = discord.FFmpegPCMAudio(song.audio_url, **FFMPEG_OPTIONS)
        self.vc.play(source, after=self._after)

        if self.message:
            try:
                await self._update_message()
            except Exception:
                pass

    async def _update_message(self):
        if not self.message or not self.current:
            return
        content = f"Reproduciendo: **{self.current.title}**"
        upcoming = list(self.queue)[:5]
        if upcoming:
            content += "\n\nPróximos en cola:"
            for i, s in enumerate(upcoming, 1):
                content += f"\n{i}. {s.title}"
        await self.message.edit(content=content, view=PlayerControls(self))

    async def skip(self):
        if self.vc.is_playing() or self.vc.is_paused():
            self.vc.stop()

    async def go_previous(self):
        if not self.history:
            return
        prev = self.history.pop()
        if self.current:
            self.queue.appendleft(self.current)
        self.queue.appendleft(prev)
        self.current = None
        if self.vc.is_playing() or self.vc.is_paused():
            self.vc.stop()
        else:
            await self.play_next()

    def pause(self):
        if self.vc.is_playing():
            self.vc.pause()

    def resume(self):
        if self.vc.is_paused():
            self.vc.resume()


players: dict[int, MusicPlayer] = {}


async def play(interaction: discord.Interaction, url: str):
    if not interaction.user.voice:
        await interaction.response.send_message("No estás en ningún canal de voz.", ephemeral=True)
        return

    if 'open.spotify.com' in url and not (os.getenv('SPOTIFY_CLIENT_ID') and os.getenv('SPOTIFY_CLIENT_SECRET')):
        await interaction.response.send_message(
            "Faltan las credenciales de Spotify. Configurá `SPOTIFY_CLIENT_ID` y `SPOTIFY_CLIENT_SECRET` en el `.env`.",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    songs = await extract_songs(url)
    if not songs:
        await interaction.followup.send("No se encontraron resultados.")
        return

    guild_id = interaction.guild.id
    voice_channel = interaction.user.voice.channel

    if guild_id in players and players[guild_id].vc.is_connected():
        player = players[guild_id]
        await player.vc.move_to(voice_channel)
    else:
        vc = await voice_channel.connect()
        player = MusicPlayer(vc, asyncio.get_running_loop())
        players[guild_id] = player

    currently_active = player.current is not None or player.vc.is_playing() or player.vc.is_paused()
    player.queue.extend(songs)

    if not currently_active:
        msg = await interaction.followup.send("Cargando...")
        player.message = msg
        await player.play_next()
    else:
        label = f"**{songs[0].title}**" if len(songs) == 1 else f"**{len(songs)} temas**"
        await interaction.followup.send(f"Agregado a la cola: {label}")
        await player._update_message()


async def stop(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    if guild_id not in players or not players[guild_id].vc.is_connected():
        await interaction.response.send_message("No hay nada reproduciéndose.", ephemeral=True)
        return

    player = players[guild_id]
    player.stopped = True
    player.queue.clear()
    player.vc.stop()
    await player.vc.disconnect()
    if player.message:
        try:
            await player.message.edit(content="Reproducción detenida.", view=None)
        except Exception:
            pass
    del players[guild_id]
    await interaction.response.send_message("Reproducción detenida.")


def setup(bot):
    bot.tree.add_command(app_commands.Command(
        name="play",
        description="Reproduce audio de YouTube o Spotify. Acepta URL o texto de búsqueda.",
        callback=play
    ))
    bot.tree.add_command(app_commands.Command(
        name="stop",
        description="Detiene la reproducción y desconecta el bot",
        callback=stop
    ))
