import discord
from discord.ext import commands
import random

class DadoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='dado', aliases=['dice', 'roll'])
    async def dado(self, ctx, cantidad: int = 1, caras: int = 6):
        """
        Lanza uno o más dados.
        Uso: f.dado [caras] [cantidad]
        Ejemplos:
        - f.dado       -> Lanza 1d6
        - f.dado 20    -> Lanza 1d20
        - f.dado 6 3   -> Lanza 3d6
        """
        # Validar que los números sean válidos
        if caras < 2:
            await ctx.send("❌ Un dado debe tener al menos 2 caras.")
            return
        
        if cantidad < 1:
            await ctx.send("❌ Debes lanzar al menos 1 dado.")
            return
        
        if cantidad > 100:
            await ctx.send("❌ No puedes lanzar más de 100 dados a la vez.")
            return
        
        # Limitar caras para evitar números absurdos
        if caras > 1000000:
            await ctx.send("❌ Un dado no puede tener más de 1,000,000 de caras.")
            return
        
        # Lanzar los dados
        resultados = []
        for _ in range(cantidad):
            resultado = random.randint(1, caras)
            resultados.append(resultado)
        
        # Calcular total
        total = sum(resultados)
        
        # Crear embed con los resultados
        embed = discord.Embed(
            title="🎲 Resultado de los dados",
            color=discord.Color.blue()
        )
        
        # Información del lanzamiento
        embed.add_field(
            name="**Información**",
            value=f"**Dados:** {cantidad}d{caras}\n**Total:** {total}",
            inline=False
        )
        
        # Mostrar resultados individuales (si no son muchos)
        if cantidad <= 20:
            resultados_str = ", ".join(str(r) for r in resultados)
            embed.add_field(
                name="**Resultados**",
                value=resultados_str,
                inline=False
            )
        else:
            # Si son muchos dados, mostrar solo el total
            embed.add_field(
                name="**Resultados**",
                value=f"Demasiados dados para mostrar individualmente. Total: {total}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    
    @commands.command(name='dadoespecial', aliases=['de'])
    async def dado_especial(self, ctx, *args):
        """
        Sistema de dados con modificadores.
        Uso: f.dadoespecial [cantidad]d[caras] [+modificador]
        Ejemplos:
        - f.dadoespecial 2d6     -> Lanza 2d6
        - f.dadoespecial 1d20+5  -> Lanza 1d20 y suma 5
        - f.dadoespecial 3d10-2  -> Lanza 3d10 y resta 2
        """
        if not args:
            await ctx.send("❌ Usa: `f.dadoespecial [cantidad]d[caras] [+modificador]`\nEjemplo: `f.dadoespecial 2d6+3`")
            return
        
        texto = "".join(args).lower().replace(" ", "")
        modificador = 0
        operador = "+"
        
        # Buscar modificador
        if "+" in texto:
            partes = texto.split("+")
            texto_dados = partes[0]
            modificador = int(partes[1]) if len(partes) > 1 else 0
        elif "-" in texto:
            partes = texto.split("-")
            texto_dados = partes[0]
            modificador = -int(partes[1]) if len(partes) > 1 else 0
        else:
            texto_dados = texto
        
        # Parsear "cantidaddcaras"
        if "d" not in texto_dados:
            await ctx.send("❌ Formato incorrecto. Usa: `cantidaddcaras`\nEjemplo: `2d6`")
            return
        
        partes = texto_dados.split("d")
        try:
            cantidad = int(partes[0]) if partes[0] else 1
            caras = int(partes[1])
        except ValueError:
            await ctx.send("❌ Formato incorrecto. Usa números: `2d6`")
            return
        
        # Validaciones
        if cantidad < 1 or cantidad > 100:
            await ctx.send("❌ La cantidad debe ser entre 1 y 100.")
            return
        
        if caras < 2 or caras > 1000:
            await ctx.send("❌ El número de caras debe ser entre 2 y 1000.")
            return
        
        # Lanzar dados
        resultados = [random.randint(1, caras) for _ in range(cantidad)]
        total_sin_mod = sum(resultados)
        total = total_sin_mod + modificador
        
        # Crear embed
        embed = discord.Embed(
            title="🎲 Tirada especial",
            color=discord.Color.purple()
        )
        
        texto_desc = f"**Dados:** {cantidad}d{caras}\n"
        if modificador != 0:
            texto_desc += f"**Modificador:** {modificador:+d}\n"
        texto_desc += f"**Total:** {total}"
        
        embed.description = texto_desc
        
        # Mostrar resultados individuales
        if cantidad <= 10:
            if modificador != 0:
                resultados_str = " + ".join(str(r) for r in resultados)
                embed.add_field(
                    name="**Detalle**",
                    value=f"{resultados_str} = {total_sin_mod} {operador} {abs(modificador)} = **{total}**",
                    inline=False
                )
            else:
                resultados_str = ", ".join(str(r) for r in resultados)
                embed.add_field(
                    name="**Resultados**",
                    value=resultados_str,
                    inline=False
                )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DadoCommands(bot))