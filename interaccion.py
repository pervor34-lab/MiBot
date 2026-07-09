import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='f.', intents=intents)


class InteraccionesCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Diccionario con las rutas de tus GIFs
        self.gifs = {
            "hug": [
                "gif/hug/hug1.gif",
                "gif/hug/hug2.gif"
            ],
            "pat":[
                "gif/pat/pat1.gif",
                "gif/pat/pat2.gif"
            ],
            "lick":[
                "gif/lick/lick1.gif",
                "gif/lick/lick2.gif",
                "gif/lick/lick3.gif",
                "gif/lick/lick4.gif"
            ],
            "disgust":[
                "gif/disgust/disgust_bot.gif"
            ]
        }
    
    # SOLO PARA HUG
    @commands.command(name='hug')
    async def hug(self, ctx, miembro: discord.Member = None):
        # Caso 1: Sin mención - el bot abraza al usuario
        if miembro is None:
            miembro = ctx.guild.me
        
            gif_path = random.choice(self.gifs["hug"])
            file = discord.File(gif_path, filename="hug.gif")
            
            embed = discord.Embed(
                description=f"**aww ven aqui!~ {ctx.author.mention}** 🤗",
                color=discord.Color.pink()
            )
            embed.set_image(url="attachment://hug.gif")
            
            await ctx.send(file=file, embed=embed)
            return  # ✅ IMPORTANTE: Detener la ejecución aquí
        
        # Caso 2: Te abrazas a ti mismo
        if miembro.id == ctx.author.id:
            await ctx.send("Te abrazaste a ti mismo... vaya")
            return  # ✅ IMPORTANTE: Detener la ejecución aquí
        
        # Caso 3: Abrazas al bot
        if miembro.id == self.bot.user.id:
            gif_path = random.choice(self.gifs["hug"])
            file = discord.File(gif_path, filename="hug.gif")
            
            embed = discord.Embed(
                description=f"**{ctx.author.mention}** me abrazó! 🤗 ¡Gracias! ❤️",
                color=discord.Color.pink()
            )
            embed.set_image(url="attachment://hug.gif")
            
            await ctx.send(file=file, embed=embed)
            return  # ✅ IMPORTANTE: Detener la ejecución aquí
        
        # Caso 4: Abrazo normal entre usuarios
        gif_path = random.choice(self.gifs["hug"])
        file = discord.File(gif_path, filename="hug.gif")
        
        embed = discord.Embed(
            description=f"**{ctx.author.mention}** abrazó a **{miembro.mention}** 🤗",
            color=discord.Color.pink()
        )
        embed.set_image(url="attachment://hug.gif")
        
        await ctx.send(file=file, embed=embed)
        # No es necesario return aquí porque ya es el final

    # SOLO PARA PAT
    @commands.command(name='pat')
    async def pat(self, ctx, miembro: discord.Member = None):
        # Caso 1: Sin mención - el bot da palmaditas
        if miembro is None:
            miembro = ctx.guild.me
        
            gif_path = random.choice(self.gifs["pat"])
            file = discord.File(gif_path, filename="pat.gif")
            
            embed = discord.Embed(
                description=f"**buen chic@ buen chic@! {ctx.author.mention}** 🤗",
                color=discord.Color.pink()
            )
            embed.set_image(url="attachment://pat.gif")
            
            await ctx.send(file=file, embed=embed)
            return  # ✅ IMPORTANTE: Detener la ejecución aquí
        
        # Caso 2: Te das palmaditas a ti mismo
        if miembro.id == ctx.author.id:
            await ctx.send("Te acariciaste a ti mismo... vaya")
            return  # ✅ IMPORTANTE: Detener la ejecución aquí
        
        # Caso 3: Das palmaditas al bot
        if miembro.id == self.bot.user.id:
            gif_path = random.choice(self.gifs["pat"])
            file = discord.File(gif_path, filename="pat.gif")
            
            embed = discord.Embed(
                description=f"**{ctx.author.mention}** Gracias por eso",
                color=discord.Color.pink()
            )
            embed.set_image(url="attachment://pat.gif")
            
            await ctx.send(file=file, embed=embed)
            return  # ✅ IMPORTANTE: Detener la ejecución aquí
        
        # Caso 4: Palmadita normal entre usuarios
        gif_path = random.choice(self.gifs["pat"])
        file = discord.File(gif_path, filename="pat.gif")
        
        embed = discord.Embed(
            description=f"**{ctx.author.mention}** le dio caricias a **{miembro.mention}** ",
            color=discord.Color.green()
        )
        embed.set_image(url="attachment://pat.gif")
        
        await ctx.send(file=file, embed=embed)
        # No es necesario return aquí porque ya es el final

    #PARA LICK
    @commands.command(name='lick')
    async def lick(self, ctx, miembro: discord.Member = None):
        # Caso 1: Sin mención - el bot da lick
        if miembro is None:
            miembro = ctx.guild.me
        
            gif_path = random.choice(self.gifs["lick"])
            file = discord.File(gif_path, filename="lick.gif")
            
            embed = discord.Embed(
                description=f"**quieres que te lama?... bien.. toma~  {ctx.author.mention}** ",
                color=discord.Color.pink()
            )
            embed.set_image(url="attachment://lick.gif")
            
            await ctx.send(file=file, embed=embed)
            return  # ✅ IMPORTANTE: Detener la ejecución aquí
        
        # Caso 2: Te das lick a ti mismo
        if miembro.id == ctx.author.id:
            await ctx.send("no te lamas a ti mismo... raro..")
            return  # ✅ IMPORTANTE: Detener la ejecución aquí
        
        # Caso 3: Das lick al bot
        if miembro.id == self.bot.user.id:
            gif_path = random.choice(self.gifs["disgust"])
            file = discord.File(gif_path, filename="disgust_bot.gif")
            
            embed = discord.Embed(
                description=f"**{ctx.author.mention}** No me toques... asqueroso",
                color=discord.Color.pink()
            )
            embed.set_image(url="attachment://disgust_bot.gif")
            
            await ctx.send(file=file, embed=embed)
            return  # ✅ IMPORTANTE: Detener la ejecución aquí
        
        # Caso 4: lick normal entre usuarios
        gif_path = random.choice(self.gifs["lick"])
        file = discord.File(gif_path, filename="lick.gif")
        
        embed = discord.Embed(
            description=f"**{ctx.author.mention}** lamiste a  **{miembro.mention}** ",
            color=discord.Color.green()
        )
        embed.set_image(url="attachment://lick.gif")
        
        await ctx.send(file=file, embed=embed)
        # No es necesario return aquí porque ya es el final

async def setup(bot):
    await bot.add_cog(InteraccionesCommands(bot))