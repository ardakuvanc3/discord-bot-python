import discord
from discord.ext import commands
import random
import requests
import os
from googleapiclient.discovery import build
import youtube_dl

Bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

def create_image_folder():
    if not os.path.exists("images"):
        os.makedirs("images")

def get_random_image_url():
    response = requests.get("https://source.unsplash.com/random")
    if response.status_code == 200:
        return response.url
    return None

def get_random_youtube_video():
    # YouTube API'sini oluşturun ve API anahtarınızı ekleyin
    youtube = build("youtube", "v3", developerKey="YOUTUBE DEVELOPER APİ")

    # YouTube API'sini kullanarak aktif videoları çekin
    response = youtube.search().list(
        part="id",
        maxResults=50,  # İstediğiniz kadar sonuç alabilirsiniz, ancak birden çok sayfa için sayfaToken kullanmalısınız.
        type="video",
        eventType="live"
    ).execute()

    # Alınan videolar arasından rastgele bir video seçin
    video_id = random.choice(response["items"])["id"]["videoId"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    return video_url

@Bot.event
async def on_ready():
    print(f'We have logged in as {Bot.user}')

@Bot.command()
async def hoşgeldin(ctx, member: discord.Member):
    channel = discord.utils.get(ctx.guild.channels, name="hoşgeldiniz")
    if channel:
        await channel.send(f"Sunucumuza hoş geldin, {member.mention}!")

@Bot.command()
async def yardım(ctx):
    response = "Mevcut komutlar:\n" \
               "`!yardım`: Mevcut komutları listeler.\n" \
               "`!hoşgeldin @KullanıcıAdı`: Yeni üyelere hoş geldin mesajı gönderir.\n" \
               "`!şaka`: Rastgele bir şaka gönderir.\n" \
               "`!sunucu_bilgisi`: Sunucu hakkında bilgileri gösterir.\n" \
               "`!rastgele_goruntu`: Rastgele bir görüntü gönderir.\n" \
               "`!rastgele_video`: Rastgele bir video gönderir.\n" \
               "`!müzik_oynat`: Müzik çalmak için kullanılır.\n" \
               "`!müzik_durdur`: Müziği durdurmak için kullanılır.\n" \
               "`!temizle <mesaj_sayısı>`: Belirtilen miktarda mesaj silmek için kullanılır.\n" \
               "`!duyuru <metin>`: Duyuru yapmak için kullanılır."
    await ctx.send(response)

@Bot.command()
async def şaka(ctx):
    jokes = [
        "Neden tavuklar yolun karşısına geçer? Sen neden yolun karşısına geçersin?",
        "Geçen gün bir sinek öldürdüm. Cinayetimle hava yastığı arasında sıkıştı.",
        "Bir gizli ajanın favori süsü ne? Kamuflaj."
    ]
    joke = random.choice(jokes)
    await ctx.send(joke)

@Bot.command()
async def sunucu_bilgisi(ctx):
    guild = ctx.guild
    total_members = guild.member_count
    total_channels = len(guild.channels)
    created_at = guild.created_at.strftime("%Y-%m-%d %H:%M:%S")

    response = f"Sunucu Adı: {guild.name}\n" \
               f"Oluşturulma Tarihi: {created_at}\n" \
               f"Toplam Üye Sayısı: {total_members}\n" \
               f"Toplam Kanal Sayısı: {total_channels}\n"

    await ctx.send(response)

@Bot.command()
async def rastgele_goruntu(ctx):
    create_image_folder()
    image_url = get_random_image_url()
    if image_url:
        await ctx.send(image_url)
    else:
        await ctx.send("Üzgünüm, rastgele bir görüntü alınamadı.")

@Bot.command()
async def rastgele_video(ctx):
    video_url = get_random_youtube_video()
    if video_url:
        await ctx.send(video_url)
    else:
        await ctx.send("Üzgünüm, rastgele bir video alınamadı.")

# Müzik Botu Özellikleri
@Bot.command()
async def müzik_oynat(ctx, *, url):
    if not ctx.message.author.voice:
        await ctx.send("Önce bir ses kanalına katılmalısınız.")
        return

    channel = ctx.message.author.voice.channel
    voice_client = discord.utils.get(Bot.voice_clients, guild=ctx.guild)

    if voice_client and voice_client.is_connected():
        await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',  # 'mp3' yerine 'opus' kullanıyoruz.
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']

    voice_client.play(discord.FFmpegPCMAudio(url2))

@Bot.command()
async def müzik_durdur(ctx):
    voice_client = discord.utils.get(Bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()

# Moderasyon Komutları
@Bot.command()
async def temizle(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)

# Duyuru Sistemi
@Bot.command()
async def duyuru(ctx, *, message):
    await ctx.send("@everyone\n" + message)

@Bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Böyle bir komut bulunamadı. Yardım için `!yardım` komutunu kullanabilirsiniz.")
    else:
        print(f"Command Error: {error}")

Bot.run("YOUR DİSCORD BOT APİ")
