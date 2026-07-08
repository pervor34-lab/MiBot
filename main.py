import discord
from discord.ext import commands
import os 
import web_server
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='f.', intents=intents)

@bot.command()
async def test(ctx, *args):
    respuesta = ' '.join(args) if args else "Bot activo de momento"
    await ctx.send(respuesta)

@bot.event
async def on_ready():
    print(f" Bot conectado como {bot.user}")
    
    # Cargar módulos
    modulos = [ 'interaccion','dado','reino']  
    
    for modulo in modulos:
        try:
            await bot.load_extension(modulo)
            print(f"✅ {modulo}.py cargado")
        except Exception as e:
            print(f"❌ Error al cargar {modulo}.py: {e}")
    
    print("\n📋 Comandos disponibles:")
    for cmd in bot.commands:
        print(f"  f.{cmd.name}")
web_server.keep_alive()
bot.run(DISCORD_TOKEN)