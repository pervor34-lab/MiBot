import discord
from discord.ext import commands
import json
import os
from datetime import datetime

class SistemaReinos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Ruta para guardar los datos
        self.archivo_datos = "datos/reinos_data.json"
        self.cargar_datos()
    
    def cargar_datos(self):
        """Carga los datos del archivo JSON"""
        # Crear carpeta si no existe
        os.makedirs("datos", exist_ok=True)
        
        try:
            with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                self.datos = json.load(f)
        except FileNotFoundError:
            # Si no existe el archivo, crear datos por defecto
            self.datos = {
                "usuarios": {},
                "estadisticas": {
                    "total_registrados": 0
                }
            }
            self.guardar_datos()
    
    def guardar_datos(self):
        """Guarda los datos en el archivo JSON"""
        with open(self.archivo_datos, 'w', encoding='utf-8') as f:
            json.dump(self.datos, f, indent=4, ensure_ascii=False)
    
    def usuario_registrado(self, user_id):
        """Verifica si un usuario está registrado"""
        return str(user_id) in self.datos["usuarios"]
    
    def obtener_usuario(self, user_id):
        """Obtiene los datos de un usuario"""
        return self.datos["usuarios"].get(str(user_id))
    
    def registrar_usuario(self, user_id, nombre):
        """Registra un nuevo usuario"""
        user_id_str = str(user_id)
        if user_id_str in self.datos["usuarios"]:
            return False, "Ya estás registrado en el sistema de reinos."
        
        # Crear datos del nuevo usuario
        self.datos["usuarios"][user_id_str] = {
            "nombre": nombre,
            "fecha_registro": datetime.now().isoformat(),
            "nivel": 1,
            "estadisticas": {
                "hp": 100,
                "oro": 0,
                "madera": 0,
                "piedra": 0,
                "poblacion": 0,
                "soldados": 0
            },
            "edificaciones": {
                "casa": 0,
                "muralia": 0,
                "cuartel": 0
            },
            "experiencia": 0
        }
        
        self.datos["estadisticas"]["total_registrados"] += 1
        self.guardar_datos()
        return True, "¡Registro exitoso! Ahora eres parte del sistema de reinos."

    @commands.command(name='registrar')
    async def registrar(self, ctx):
        """Registra a un usuario en el sistema de reinos"""
        usuario_id = ctx.author.id
        
        if self.usuario_registrado(usuario_id):
            await ctx.send(f"❌ {ctx.author.mention} ¡Ya estás registrado en el sistema de reinos!")
            return
        
        exito, mensaje = self.registrar_usuario(usuario_id, ctx.author.display_name)
        
        if exito:
            embed = discord.Embed(
                title="🏰 ¡BIENVENIDO AL SISTEMA DE REINOS!",
                description=f"{ctx.author.mention} {mensaje}",
                color=discord.Color.green()
            )
            
            datos_usuario = self.obtener_usuario(usuario_id)
            
            embed.add_field(
                name="📊 Tus estadísticas iniciales",
                value=f"**Nivel:** {datos_usuario['nivel']}\n"
                      f"**HP:** ❤️ {datos_usuario['estadisticas']['hp']}\n"
                      f"**Oro:** 🪙 {datos_usuario['estadisticas']['oro']}\n"
                      f"**Fecha de registro:** {datos_usuario['fecha_registro'][:10]}",
                inline=False
            )
            
            # Intentar agregar imagen
            try:
                archivo = discord.File("imagen/Reino/reino default.jpg", filename="fondo.jpg")
                embed.set_image(url="attachment://fondo.jpg")
                embed.set_footer(text="¡Usa f.stat para ver tus estadísticas completas!")
                await ctx.send(file=archivo, embed=embed)
            except:
                embed.set_footer(text="¡Usa f.stat para ver tus estadísticas completas!")
                await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Error al registrar: {mensaje}")

    @commands.command(name='stat')
    async def stat(self, ctx):
        """Muestra las estadísticas del personaje"""
        usuario_id = ctx.author.id
        
        if not self.usuario_registrado(usuario_id):
            embed = discord.Embed(
                title="❌ NO REGISTRADO",
                description=f"{ctx.author.mention} No estás registrado en el sistema de reinos.\n"
                            f"Usa `f.registrar` para unirte al sistema.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        datos_usuario = self.obtener_usuario(usuario_id)
        
        embed = discord.Embed(
            title=f"📊 STATUS DEL PERSONAJE",
            description=f"Información de {ctx.author.display_name}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="**Información Básica**",
            value=f"**Dueño**: {ctx.author.mention}\n"
                  f"**Nivel**: {datos_usuario['nivel']}\n"
                  ,
            inline=False
        )
        
        stats = datos_usuario['estadisticas']
        embed.add_field(
            name="**Estadísticas**",
            value=f"**HP**: ❤️ {stats['hp']}\n"
                  f"**Oro**: 🪙 {stats['oro']}\n"
                  f"**Madera**: 🪵 {stats['madera']}\n"
                  f"**Piedra**: 🪨 {stats['piedra']}\n"
                  f"**Población**: 👥 {stats['poblacion']}\n"
                  f"**Soldados**: ⚔️ {stats['soldados']}",
            inline=False
        )
        
        edificios = datos_usuario['edificaciones']
        edificios_texto = ""
        for nombre, cantidad in edificios.items():
            if cantidad > 0:
                emoji = "🏠" if nombre == "casa" else "🏰" if nombre == "muralia" else "⚔️"
                edificios_texto += f"{emoji} {nombre.capitalize()}: {cantidad}\n"
        
        if not edificios_texto:
            edificios_texto = "No tienes edificaciones aún"
        
        embed.add_field(
            name="**Edificaciones**",
            value=edificios_texto,
            inline=False
        )
        
        try:
            archivo = discord.File("imagen/Reino/reino default.jpg", filename="fondo.jpg")
            embed.set_image(url="attachment://fondo.jpg")
            embed.set_footer(text=f"ID: {usuario_id}")
            await ctx.send(file=archivo, embed=embed)
        except:
            embed.set_footer(text=f"ID: {usuario_id}")
            await ctx.send(embed=embed)

    @commands.command(name='addoro')
    @commands.has_permissions(administrator=True)
    async def agregar_oro(self, ctx, miembro: discord.Member, cantidad: int):
        """Agrega oro a un usuario (solo admin)"""
        usuario_id = str(miembro.id)
        
        if not self.usuario_registrado(usuario_id):
            await ctx.send(f"❌ {miembro.mention} no está registrado en el sistema.")
            return
        
        self.datos["usuarios"][usuario_id]["estadisticas"]["oro"] += cantidad
        self.guardar_datos()
        
        await ctx.send(f"✅ Se agregaron **{cantidad}** 🪙 de oro a {miembro.mention}")

    @commands.command(name='top')
    async def top(self, ctx):
        """Muestra el top de jugadores por oro"""
        usuarios = self.datos["usuarios"]
        
        if not usuarios:
            await ctx.send("❌ No hay usuarios registrados aún.")
            return
        
        top_usuarios = sorted(
            usuarios.items(),
            key=lambda x: x[1]["estadisticas"]["oro"],
            reverse=True
        )[:10]
        
        embed = discord.Embed(
            title="🏆 TOP 10 JUGADORES POR ORO",
            color=discord.Color.gold()
        )
        
        for i, (user_id, datos) in enumerate(top_usuarios, 1):
            try:
                usuario = await self.bot.fetch_user(int(user_id))
                nombre = usuario.display_name
            except:
                nombre = datos["nombre"]
            
            medalla = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            embed.add_field(
                name=f"{medalla} {nombre}",
                value=f"🪙 {datos['estadisticas']['oro']} oro | Nv. {datos['nivel']}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='borrarusuario')
    @commands.has_permissions(administrator=True)
    async def borrar_usuario(self, ctx, miembro: discord.Member):
        """Borra a un usuario del sistema (solo admin)"""
        usuario_id = str(miembro.id)
        
        if not self.usuario_registrado(usuario_id):
            await ctx.send(f"❌ {miembro.mention} no está registrado en el sistema.")
            return
        
        del self.datos["usuarios"][usuario_id]
        self.datos["estadisticas"]["total_registrados"] -= 1
        self.guardar_datos()
        
        await ctx.send(f"✅ {miembro.mention} ha sido eliminado del sistema de reinos.")

    @commands.command(name='setoro')
    @commands.has_permissions(administrator=True)
    async def set_oro(self, ctx, miembro: discord.Member, cantidad: int):
        """Dar oro a usuarios: f.setoro @usuario 500"""
        usuario_id = str(miembro.id)
        
        if not self.usuario_registrado(usuario_id):
            await ctx.send(f"❌ {miembro.mention} no está registrado.")
            return
        
        if cantidad < 0:
            await ctx.send(f"❌ La cantidad no puede ser negativa.")
            return
        
        self.datos["usuarios"][usuario_id]["estadisticas"]["oro"] = cantidad
        self.guardar_datos()
        
        embed = discord.Embed(
            title="💰 ORO ACTUALIZADO",
            description=f"El oro de {miembro.mention} ahora es **{cantidad}** 🪙",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @commands.command(name='setmadera')
    @commands.has_permissions(administrator=True)
    async def set_madera(self, ctx, miembro: discord.Member, cantidad: int):
        """Dar madera a usuarios f.setmadera @usuario 500"""
        usuario_id = str(miembro.id)
        
        if not self.usuario_registrado(usuario_id):
            await ctx.send(f"❌ {miembro.mention} no está registrado.")
            return
        
        if cantidad < 0:
            await ctx.send(f"❌ La cantidad no puede ser negativa.")
            return
        
        self.datos["usuarios"][usuario_id]["estadisticas"]["madera"] = cantidad
        self.guardar_datos()
        
        await ctx.send(f"✅ La madera de {miembro.mention} ahora es **{cantidad}** 🪵")

    @commands.command(name='setpiedra')
    @commands.has_permissions(administrator=True)
    async def set_piedra(self, ctx, miembro: discord.Member, cantidad: int):
        """Establece la cantidad exacta de piedra de un usuario (solo admin)"""
        usuario_id = str(miembro.id)
        
        if not self.usuario_registrado(usuario_id):
            await ctx.send(f"❌ {miembro.mention} no está registrado.")
            return
        
        if cantidad < 0:
            await ctx.send(f"❌ La cantidad no puede ser negativa.")
            return
        
        self.datos["usuarios"][usuario_id]["estadisticas"]["piedra"] = cantidad
        self.guardar_datos()
        
        await ctx.send(f"✅ La piedra de {miembro.mention} ahora es **{cantidad}** 🪨")

    @commands.command(name='sethp')
    @commands.has_permissions(administrator=True)
    async def set_hp(self, ctx, miembro: discord.Member, cantidad: int):
        """Establece el HP de un usuario """
        usuario_id = str(miembro.id)
        
        if not self.usuario_registrado(usuario_id):
            await ctx.send(f"❌ {miembro.mention} no está registrado.")
            return
        
        if cantidad < 0:
            await ctx.send(f"❌ La cantidad no puede ser negativa.")
            return
        
        self.datos["usuarios"][usuario_id]["estadisticas"]["hp"] = cantidad
        self.guardar_datos()
        
        await ctx.send(f"✅ El HP de {miembro.mention} ahora es **{cantidad}** ❤️")

async def setup(bot):
    await bot.add_cog(SistemaReinos(bot))