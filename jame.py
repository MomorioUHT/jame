import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN not found in environment variables")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

ytdl = yt_dlp.YoutubeDL({
    "format": "bestaudio/best",
    "quiet": True
})
ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"เจมออนไลน์แล้ว {bot.user}")


# Helper
async def get_audio_source(url: str):
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(
        None, lambda: ytdl.extract_info(url, download=False)
    )
    return data["url"], data["title"]


# Command Here
@bot.tree.command(name="play", description="เจม เปิดเพลงยูทูปให้ฟังหน่อยดิ")
async def play(interaction: discord.Interaction, url: str):

    if not interaction.user.voice:
        await interaction.response.send_message("เจม: เข้าห้องเสียงยัง??")
        return

    await interaction.response.send_message("เจม: แป๊บนึงๆๆๆ")

    voice_channel = interaction.user.voice.channel

    if interaction.guild.voice_client:
        vc = interaction.guild.voice_client
    else:
        vc = await voice_channel.connect()

    try:
        stream_url, title = await get_audio_source(url)
        vc.stop()

        audio = discord.FFmpegOpusAudio(stream_url, **ffmpeg_options)
        vc.play(audio)

        await interaction.followup.send(f"เจมกำลังเล่นเพลง: {title}")

    except Exception as e:
        await interaction.followup.send("เจมพัง! บอกไอท้อปซ่อมด่วน")
        print(e)


@bot.tree.command(name="stop", description="ไล่เจม")
async def stop(interaction: discord.Interaction):

    vc = interaction.guild.voice_client

    if not vc:
        await interaction.response.send_message("เจม: เข้าห้องเสียงยัง??")
        return

    vc.stop()
    await vc.disconnect()
    await interaction.response.send_message("เจม: หยุดเพลงให้แล้ว")


bot.run(TOKEN)