import discord
from discord.ext import commands
from discord.ui import Button, View, Select
import json
import os
from datetime import datetime, timedelta

# ============ CONFIGURACIÓN DE MUROS ============
MUROS = {
    "muro": {
        1: {"nombre": "Muro de Madera", "piedra": 10, "madera": 20, "oro": 5, "hp": 50, "defensa": 10, "emoji": "🪵"},
        2: {"nombre": "Muro de Piedra", "piedra": 30, "madera": 10, "oro": 15, "hp": 100, "defensa": 25, "emoji": "🪨"},
        3: {"nombre": "Muro de Hierro", "piedra": 50, "madera": 5, "oro": 30, "hp": 200, "defensa": 50, "emoji": "⚙️"},
        4: {"nombre": "Muro de Obsidiana", "piedra": 100, "madera": 0, "oro": 50, "hp": 350, "defensa": 80, "emoji": "🔮"},
        5: {"nombre": "Muro Legendario", "piedra": 200, "madera": 0, "oro": 100, "hp": 500, "defensa": 120, "emoji": "⭐"}
    },
    "torre": {
        1: {"nombre": "Torre de Vigilancia", "piedra": 20, "madera": 15, "oro": 10, "hp": 30, "ataque": 15, "emoji": "🗼"},
        2: {"nombre": "Torre de Arqueros", "piedra": 40, "madera": 20, "oro": 25, "hp": 60, "ataque": 35, "emoji": "🏹"},
        3: {"nombre": "Torre de Magos", "piedra": 60, "madera": 10, "oro": 50, "hp": 100, "ataque": 70, "emoji": "🔮"},
        4: {"nombre": "Torre del Dragón", "piedra": 120, "madera": 0, "oro": 100, "hp": 200, "ataque": 120, "emoji": "🐉"}
    },
    "cuartel": {
        1: {"nombre": "Cuartel Pequeño", "piedra": 15, "madera": 25, "oro": 10, "soldados": 5, "emoji": "🏛️"},
        2: {"nombre": "Cuartel Medio", "piedra": 30, "madera": 30, "oro": 20, "soldados": 15, "emoji": "🏛️"},
        3: {"nombre": "Cuartel Grande", "piedra": 50, "madera": 40, "oro": 35, "soldados": 30, "emoji": "🏛️"},
        4: {"nombre": "Ciudadela", "piedra": 100, "madera": 60, "oro": 80, "soldados": 60, "emoji": "🏰"}
    }
}

# ============ CONFIGURACIÓN DE RECOMPENSAS SEMANALES ============
RECOMPENSAS_SEMANALES = {
    1: {"oro": 8000, "madera": 100, "piedra": 50, "nombre": "Novato"},
    2: {"oro": 12000, "madera": 200, "piedra": 100, "nombre": "Aprendiz"},
    3: {"oro": 18000, "madera": 350, "piedra": 200, "nombre": "Guerrero"},
    4: {"oro": 25000, "madera": 500, "piedra": 350, "nombre": "Señor"},
    5: {"oro": 35000, "madera": 750, "piedra": 500, "nombre": "Barón"},
    6: {"oro": 50000, "madera": 1000, "piedra": 750, "nombre": "Conde"}
}

# ============ CLASES DE VISTAS (FUERA DE LA CLASE COG) ============
class SeleccionEstructura(discord.ui.View):
    def __init__(self, cog, usuario_id):
        super().__init__(timeout=60)
        self.cog = cog
        self.usuario_id = usuario_id
        self.tipo_seleccionado = None
        self.nivel_seleccionado = None
    
    @discord.ui.select(
        placeholder="🏗️ Selecciona el tipo de estructura",
        options=[
            discord.SelectOption(label="Muro", value="muro", emoji="🧱", description="Defensa de tu reino"),
            discord.SelectOption(label="Torre", value="torre", emoji="🗼", description="Ataca a los enemigos"),
            discord.SelectOption(label="Cuartel", value="cuartel", emoji="🏛️", description="Entrena soldados")
        ]
    )
    async def select_tipo(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Este menú no es para ti.", ephemeral=True)
            return
        
        self.tipo_seleccionado = select.values[0]
        
        view = SeleccionNivel(self.cog, self.usuario_id, self.tipo_seleccionado)
        await interaction.response.edit_message(
            content=f"✅ Has seleccionado **{select.values[0].capitalize()}**. Ahora elige el nivel:",
            view=view,
            embed=None
        )

class SeleccionNivel(discord.ui.View):
    def __init__(self, cog, usuario_id, tipo):
        super().__init__(timeout=60)
        self.cog = cog
        self.usuario_id = usuario_id
        self.tipo = tipo
        
        tipo_data = MUROS[tipo]
        opciones = []
        
        for nivel, datos in tipo_data.items():
            emoji = datos.get('emoji', '📊')
            opciones.append(
                discord.SelectOption(
                    label=f"Nivel {nivel} - {datos['nombre']}",
                    value=str(nivel),
                    emoji=emoji,
                    description=f"🏗️ {datos['nombre']}"
                )
            )
        
        self.add_item(NivelSelect(cog, usuario_id, tipo, opciones))

class NivelSelect(discord.ui.Select):
    def __init__(self, cog, usuario_id, tipo, opciones):
        self.cog = cog
        self.usuario_id = usuario_id
        self.tipo = tipo
        super().__init__(placeholder="📊 Selecciona el nivel", options=opciones)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Este menú no es para ti.", ephemeral=True)
            return
        
        nivel = int(self.values[0])
        datos = MUROS[self.tipo][nivel]
        
        embed = discord.Embed(
            title=f"🏗️ {datos['nombre']} (Nivel {nivel})",
            color=discord.Color.blue()
        )
        
        info_texto = ""
        for key, value in datos.items():
            if key not in ['nombre', 'emoji']:
                emoji = "❤️" if key == "hp" else "🛡️" if key == "defensa" else "⚔️" if key == "ataque" else "👥" if key == "soldados" else "📊"
                info_texto += f"{emoji} {key.capitalize()}: {value}\n"
        
        embed.add_field(name="📊 Estadísticas", value=info_texto, inline=False)
        embed.add_field(
            name="💰 Recursos necesarios",
            value=f"🪨 Piedra: {datos.get('piedra', 0)}\n🪵 Madera: {datos.get('madera', 0)}\n🪙 Oro: {datos.get('oro', 0)}",
            inline=False
        )
        
        usuario_data = self.cog.obtener_usuario(self.usuario_id)
        tiene_estructura = False
        nivel_actual = 0
        
        if 'estructuras' in usuario_data and self.tipo in usuario_data['estructuras']:
            tiene_estructura = True
            nivel_actual = usuario_data['estructuras'][self.tipo]['nivel']
            if nivel_actual >= nivel:
                await interaction.response.send_message(
                    f"⚠️ Ya tienes un {datos['nombre']} (Nivel {nivel_actual}). No puedes construir uno de nivel inferior.",
                    ephemeral=True
                )
                return
        
        view = View()
        
        if tiene_estructura and nivel_actual < nivel:
            mejorar_btn = Button(label=f"⬆️ Mejorar a Nv.{nivel}", style=discord.ButtonStyle.green, emoji="⬆️")
            mejorar_btn.callback = lambda i: self.cog.construir_estructura_interactivo(i, self.tipo, nivel, "mejorar")
            view.add_item(mejorar_btn)
        elif not tiene_estructura:
            construir_btn = Button(label=f"🏗️ Construir {datos['nombre']}", style=discord.ButtonStyle.green, emoji="🏗️")
            construir_btn.callback = lambda i: self.cog.construir_estructura_interactivo(i, self.tipo, nivel, "construir")
            view.add_item(construir_btn)
        else:
            await interaction.response.send_message(
                f"⚠️ Ya tienes esta estructura (Nivel {nivel_actual}). Usa `f.mejorar {self.tipo}` para mejorarla.",
                ephemeral=True
            )
            return
        
        cancelar_btn = Button(label="❌ Cancelar", style=discord.ButtonStyle.red, emoji="❌")
        cancelar_btn.callback = lambda i: self.cog.cancelar_construccion(i)
        view.add_item(cancelar_btn)
        
        await interaction.response.edit_message(
            content=f"📋 **{datos['nombre']}** (Nivel {nivel}) - ¿Qué deseas hacer?",
            embed=embed,
            view=view
        )

# ============ CLASE PRINCIPAL DEL COG ============
class SistemaReinos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.archivo_datos = "datos/reinos_data.json"
        self.cargar_datos()
    
    def cargar_datos(self):
        """Carga los datos del archivo JSON"""
        os.makedirs("datos", exist_ok=True)
        try:
            with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                self.datos = json.load(f)
        except FileNotFoundError:
            self.datos = {
                "usuarios": {},
                "estadisticas": {"total_registrados": 0}
            }
            self.guardar_datos()
    
    def guardar_datos(self):
        """Guarda los datos en el archivo JSON"""
        with open(self.archivo_datos, 'w', encoding='utf-8') as f:
            json.dump(self.datos, f, indent=4, ensure_ascii=False)
    
    def usuario_registrado(self, user_id):
        return str(user_id) in self.datos["usuarios"]
    
    def obtener_usuario(self, user_id):
        return self.datos["usuarios"].get(str(user_id))
    
    def registrar_usuario(self, user_id, nombre):
        user_id_str = str(user_id)
        if user_id_str in self.datos["usuarios"]:
            return False, "Ya estás registrado en el sistema de reinos."
        
        self.datos["usuarios"][user_id_str] = {
            "nombre": nombre,
            "fecha_registro": datetime.now().isoformat(),
            "nivel": 1,
            "experiencia": 0,
            "estadisticas": {
                "hp": 100,
                "oro": 0,
                "madera": 0,
                "piedra": 0,
                "poblacion": 0,
                "soldados": 0
            },
            "edificaciones": {"casa": 0, "muralia": 0, "cuartel": 0},
            "estructuras": {},
            "recompensa_semanal": {
                "ultima_vez": None,
                "dias_restantes": 7
            }
        }
        
        self.datos["estadisticas"]["total_registrados"] += 1
        self.guardar_datos()
        return True, "¡Registro exitoso! Ahora eres parte del sistema de reinos."

    # ============ COMANDOS DE USUARIO ============
    
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
                  f"**Nivel**: {datos_usuario['nivel']}\n",
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
        
        # Mostrar estructuras
        estructuras_texto = ""
        if 'estructuras' in datos_usuario and datos_usuario['estructuras']:
            for tipo, info in datos_usuario['estructuras'].items():
                nivel = info['nivel']
                datos_est = MUROS.get(tipo, {}).get(nivel, {})
                nombre = datos_est.get('nombre', f"{tipo.capitalize()} Nv.{nivel}")
                emojis = {"muro": "🧱", "torre": "🗼", "cuartel": "🏛️"}
                emoji = emojis.get(tipo, "🏗️")
                estructuras_texto += f"{emoji} {nombre}\n"
        else:
            estructuras_texto = "No tienes estructuras aún"
        
        embed.add_field(
            name="**Estructuras**",
            value=estructuras_texto,
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

    # ============ COMANDOS DE RECOMPENSAS SEMANALES ============
    
    @commands.command(name='reclamar')
    async def reclamar_recompensa(self, ctx):
        """Reclama tu recompensa semanal basada en tu nivel"""
        usuario_id = str(ctx.author.id)
        
        if not self.usuario_registrado(usuario_id):
            embed = discord.Embed(
                title="❌ NO REGISTRADO",
                description=f"{ctx.author.mention} No estás registrado. Usa `f.registrar`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        datos_usuario = self.obtener_usuario(usuario_id)
        nivel = datos_usuario['nivel']
        
        # Verificar el nivel máximo disponible
        nivel_maximo = max(RECOMPENSAS_SEMANALES.keys())
        if nivel > nivel_maximo:
            nivel = nivel_maximo
        
        # Obtener la recompensa según el nivel
        recompensa = RECOMPENSAS_SEMANALES.get(nivel, RECOMPENSAS_SEMANALES[1])
        
        # Verificar si ya reclamó esta semana
        ultima_vez = datos_usuario.get('recompensa_semanal', {}).get('ultima_vez')
        hoy = datetime.now()
        
        if ultima_vez:
            try:
                ultima_fecha = datetime.fromisoformat(ultima_vez)
                dias_pasados = (hoy - ultima_fecha).days
                
                if dias_pasados < 7:
                    dias_restantes = 7 - dias_pasados
                    proxima = ultima_fecha + timedelta(days=7)
                    
                    embed = discord.Embed(
                        title="⏳ YA RECLAMASTE TU RECOMPENSA",
                        description=f"{ctx.author.mention} Ya reclamaste tu recompensa esta semana.",
                        color=discord.Color.orange()
                    )
                    embed.add_field(
                        name="📅 Próxima recompensa disponible",
                        value=f"⏰ **{dias_restantes} días** restantes\n"
                              f"📆 {proxima.strftime('%d/%m/%Y')}",
                        inline=False
                    )
                    embed.add_field(
                        name="💰 Recompensa para tu nivel",
                        value=f"**Nivel {nivel}** - {recompensa['nombre']}\n"
                              f"🪙 Oro: {recompensa['oro']}\n"
                              f"🪵 Madera: {recompensa['madera']}\n"
                              f"🪨 Piedra: {recompensa['piedra']}",
                        inline=False
                    )
                    embed.set_footer(text="¡Vuelve la próxima semana!")
                    await ctx.send(embed=embed)
                    return
            except:
                pass
        
        # ============ ENTREGAR RECOMPENSA ============
        stats = datos_usuario['estadisticas']
        
        # Agregar recursos
        stats['oro'] += recompensa['oro']
        stats['madera'] += recompensa['madera']
        stats['piedra'] += recompensa['piedra']
        
        # Actualizar última recompensa
        if 'recompensa_semanal' not in datos_usuario:
            datos_usuario['recompensa_semanal'] = {}
        
        datos_usuario['recompensa_semanal']['ultima_vez'] = hoy.isoformat()
        self.guardar_datos()
        
        # Embed de confirmación
        embed = discord.Embed(
            title="🎉 ¡RECOMPENSA SEMANAL RECLAMADA!",
            description=f"{ctx.author.mention} Has reclamado tu recompensa de esta semana.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📊 Recompensa recibida",
            value=f"**Nivel {nivel}** - {recompensa['nombre']}\n"
                  f"🪙 **+{recompensa['oro']}** Oro\n"
                  f"🪵 **+{recompensa['madera']}** Madera\n"
                  f"🪨 **+{recompensa['piedra']}** Piedra",
            inline=False
        )
        
        embed.add_field(
            name="💰 Tus recursos actuales",
            value=f"🪙 **{stats['oro']}** Oro\n"
                  f"🪵 **{stats['madera']}** Madera\n"
                  f"🪨 **{stats['piedra']}** Piedra",
            inline=False
        )
        
        proxima_recompensa = hoy + timedelta(days=7)
        embed.add_field(
            name="📅 Próxima recompensa",
            value=f"📆 Disponible el: {proxima_recompensa.strftime('%d/%m/%Y')}\n"
                  f"⏰ En 7 días",
            inline=False
        )
        
        embed.set_footer(text="¡Vuelve la próxima semana por más recompensas!")
        await ctx.send(embed=embed)

    @commands.command(name='recompensa')
    async def ver_recompensa(self, ctx):
        """Muestra el estado de tu recompensa semanal"""
        usuario_id = str(ctx.author.id)
        
        if not self.usuario_registrado(usuario_id):
            await ctx.send(f"❌ {ctx.author.mention} No estás registrado. Usa `f.registrar`")
            return
        
        datos_usuario = self.obtener_usuario(usuario_id)
        nivel = datos_usuario['nivel']
        nivel_maximo = max(RECOMPENSAS_SEMANALES.keys())
        
        if nivel > nivel_maximo:
            nivel = nivel_maximo
        
        recompensa = RECOMPENSAS_SEMANALES.get(nivel, RECOMPENSAS_SEMANALES[1])
        
        embed = discord.Embed(
            title="📊 ESTADO DE RECOMPENSA SEMANAL",
            description=f"Información para {ctx.author.display_name}",
            color=discord.Color.blue()
        )
        
        # Nivel actual
        embed.add_field(
            name="📈 Tu nivel",
            value=f"**Nivel {nivel}** - {recompensa['nombre']}",
            inline=False
        )
        
        # Recompensa disponible
        embed.add_field(
            name="💰 Recompensa disponible",
            value=f"🪙 **{recompensa['oro']}** Oro\n"
                  f"🪵 **{recompensa['madera']}** Madera\n"
                  f"🪨 **{recompensa['piedra']}** Piedra",
            inline=False
        )
        
        # Verificar si ya reclamó
        ultima_vez = datos_usuario.get('recompensa_semanal', {}).get('ultima_vez')
        hoy = datetime.now()
        
        if ultima_vez:
            try:
                ultima_fecha = datetime.fromisoformat(ultima_vez)
                dias_pasados = (hoy - ultima_fecha).days
                
                if dias_pasados < 7:
                    dias_restantes = 7 - dias_pasados
                    embed.add_field(
                        name="⏳ Estado",
                        value=f"❌ **Ya reclamaste** esta semana\n"
                              f"⏰ Próxima en: **{dias_restantes} días**",
                        inline=False
                    )
                    embed.color = discord.Color.orange()
                else:
                    embed.add_field(
                        name="✅ Estado",
                        value=f"🎉 **¡Recompensa disponible!**\n"
                              f"Usa `f.reclamar` para recibirla",
                        inline=False
                    )
                    embed.color = discord.Color.green()
            except:
                embed.add_field(
                    name="✅ Estado",
                    value=f"🎉 **¡Recompensa disponible!**\n"
                          f"Usa `f.reclamar` para recibirla",
                    inline=False
                )
                embed.color = discord.Color.green()
        else:
            embed.add_field(
                name="✅ Estado",
                value=f"🎉 **¡Recompensa disponible!**\n"
                      f"Usa `f.reclamar` para recibirla",
                inline=False
            )
            embed.color = discord.Color.green()
        
        # Mostrar todas las recompensas por nivel
        embed.add_field(
            name="📊 Recompensas por nivel",
            value="`Nivel 1` - 8,000 🪙\n"
                  "`Nivel 2` - 12,000 🪙\n"
                  "`Nivel 3` - 18,000 🪙\n"
                  "`Nivel 4` - 25,000 🪙\n"
                  "`Nivel 5` - 35,000 🪙\n"
                  "`Nivel 6` - 50,000 🪙\n"
                  "_Sube de nivel para mejorar tus recompensas_",
            inline=False
        )
        
        embed.set_footer(text="¡Reclama tu recompensa cada semana!")
        await ctx.send(embed=embed)

    # ============ COMANDOS DE ADMINISTRACIÓN ============
    
    @commands.command(name='subirnivel')
    @commands.has_permissions(administrator=True)
    async def subir_nivel(self, ctx, miembro: discord.Member, nuevo_nivel: int = None):
        """Sube de nivel a un usuario (solo admin)"""
        usuario_id = str(miembro.id)
        
        if not self.usuario_registrado(usuario_id):
            await ctx.send(f"❌ {miembro.mention} no está registrado.")
            return
        
        datos_usuario = self.obtener_usuario(usuario_id)
        
        if nuevo_nivel is None:
            # Subir 1 nivel
            nuevo_nivel = datos_usuario['nivel'] + 1
        else:
            if nuevo_nivel < 1:
                await ctx.send(f"❌ El nivel no puede ser menor a 1.")
                return
        
        nivel_maximo = max(RECOMPENSAS_SEMANALES.keys())
        if nuevo_nivel > nivel_maximo:
            await ctx.send(f"⚠️ El nivel máximo es {nivel_maximo}.")
            return
        
        # Actualizar nivel
        nivel_anterior = datos_usuario['nivel']
        datos_usuario['nivel'] = nuevo_nivel
        self.guardar_datos()
        
        embed = discord.Embed(
            title="⬆️ ¡NIVEL ACTUALIZADO!",
            description=f"{miembro.mention} ha subido de nivel",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="📊 Progreso",
            value=f"**Nivel anterior:** {nivel_anterior}\n"
                  f"**Nuevo nivel:** {nuevo_nivel}",
            inline=False
        )
        
        # Mostrar nueva recompensa
        if nuevo_nivel in RECOMPENSAS_SEMANALES:
            recompensa = RECOMPENSAS_SEMANALES[nuevo_nivel]
            embed.add_field(
                name="💰 Nueva recompensa semanal",
                value=f"**{recompensa['nombre']}**\n"
                      f"🪙 {recompensa['oro']} Oro\n"
                      f"🪵 {recompensa['madera']} Madera\n"
                      f"🪨 {recompensa['piedra']} Piedra",
                inline=False
            )
        
        await ctx.send(embed=embed)

    # ============ COMANDOS DE CONSTRUCCIÓN ============
    
    @commands.command(name='construir')
    async def construir(self, ctx):
        """Abre un menú interactivo para construir estructuras"""
        usuario_id = ctx.author.id
        
        if not self.usuario_registrado(usuario_id):
            await ctx.send(f"❌ {ctx.author.mention} No estás registrado. Usa `f.registrar`")
            return
        
        embed = discord.Embed(
            title="🏗️ SISTEMA DE CONSTRUCCIÓN",
            description="Selecciona el tipo de estructura que deseas construir:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📋 Tipos disponibles",
            value="🧱 **Muro** - Defensa de tu reino\n"
                  "🗼 **Torre** - Ataca a los enemigos\n"
                  "🏛️ **Cuartel** - Entrena soldados",
            inline=False
        )
        
        embed.set_footer(text="Selecciona una opción en el menú desplegable")
        
        view = SeleccionEstructura(self, usuario_id)
        await ctx.send(embed=embed, view=view)

    @commands.command(name='muros')
    async def ver_muros_interactivo(self, ctx, miembro: discord.Member = None):
        """Muestra todas las estructuras de un usuario"""
        
        if miembro is None:
            miembro = ctx.author
        
        usuario_id = str(miembro.id)
        
        if not self.usuario_registrado(usuario_id):
            await ctx.send(f"❌ {miembro.mention} no está registrado.")
            return
        
        datos_usuario = self.obtener_usuario(usuario_id)
        
        embed = discord.Embed(
            title=f"🏗️ ESTRUCTURAS DE {miembro.display_name}",
            color=discord.Color.blue()
        )
        
        if 'estructuras' not in datos_usuario or not datos_usuario['estructuras']:
            embed.description = "❌ No tiene estructuras construidas aún"
            await ctx.send(embed=embed)
            return
        
        for tipo, info in datos_usuario['estructuras'].items():
            nivel = info['nivel']
            datos = MUROS.get(tipo, {}).get(nivel, {})
            nombre = datos.get('nombre', f"{tipo.capitalize()} Nv.{nivel}")
            
            emojis = {"muro": "🧱", "torre": "🗼", "cuartel": "🏛️"}
            emoji = emojis.get(tipo, "🏗️")
            
            info_texto = f"**Nivel:** {nivel}\n"
            info_texto += f"**Construido:** {info.get('construido', 'Desconocido')[:10]}\n"
            
            for key, value in datos.items():
                if key not in ['nombre', 'emoji']:
                    emoji_stat = "❤️" if key == "hp" else "🛡️" if key == "defensa" else "⚔️" if key == "ataque" else "👥" if key == "soldados" else "📊"
                    info_texto += f"{emoji_stat} {key.capitalize()}: {value}\n"
            
            embed.add_field(name=f"{emoji} {nombre}", value=info_texto, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name='mejorar')
    async def mejorar_interactivo(self, ctx, tipo: str = None):
        """Mejora una estructura al siguiente nivel"""
        usuario_id = ctx.author.id
        
        if not self.usuario_registrado(usuario_id):
            await ctx.send(f"❌ {ctx.author.mention} No estás registrado.")
            return
        
        if tipo is None:
            datos_usuario = self.obtener_usuario(usuario_id)
            if 'estructuras' not in datos_usuario or not datos_usuario['estructuras']:
                await ctx.send("❌ No tienes estructuras para mejorar.")
                return
            
            embed = discord.Embed(
                title="⬆️ MEJORAR ESTRUCTURA",
                description="Selecciona la estructura a mejorar:",
                color=discord.Color.gold()
            )
            await ctx.send(embed=embed)
            
            view = View()
            for tipo_est in datos_usuario['estructuras'].keys():
                btn = Button(
                    label=tipo_est.capitalize(),
                    emoji="🧱" if tipo_est == "muro" else "🗼" if tipo_est == "torre" else "🏛️",
                    style=discord.ButtonStyle.primary
                )
                btn.callback = lambda i, t=tipo_est: self.mostrar_mejora(i, t)
                view.add_item(btn)
            
            cancelar_btn = Button(label="❌ Cancelar", style=discord.ButtonStyle.red, emoji="❌")
            cancelar_btn.callback = lambda i: self.cancelar_construccion(i)
            view.add_item(cancelar_btn)
            
            await ctx.send("Selecciona la estructura a mejorar:", view=view)
            return
        
        await self.procesar_mejora(ctx, tipo.lower())

    # ============ MÉTODOS AUXILIARES PARA CONSTRUCCIÓN ============
    
    async def mostrar_mejora(self, interaction, tipo):
        """Muestra la información de mejora"""
        usuario_id = str(interaction.user.id)
        datos_usuario = self.obtener_usuario(usuario_id)
        
        if tipo not in datos_usuario['estructuras']:
            await interaction.response.send_message(f"❌ No tienes un {tipo}.", ephemeral=True)
            return
        
        nivel_actual = datos_usuario['estructuras'][tipo]['nivel']
        nivel_siguiente = nivel_actual + 1
        
        if nivel_siguiente not in MUROS[tipo]:
            await interaction.response.send_message(f"⚠️ Ya tienes el nivel máximo para {tipo}.", ephemeral=True)
            return
        
        datos = MUROS[tipo][nivel_siguiente]
        
        embed = discord.Embed(
            title=f"⬆️ MEJORAR {datos['nombre']}",
            description=f"Nivel actual: **{nivel_actual}** → Nivel siguiente: **{nivel_siguiente}**",
            color=discord.Color.gold()
        )
        
        info_texto = ""
        for key, value in datos.items():
            if key not in ['nombre', 'emoji']:
                emoji = "❤️" if key == "hp" else "🛡️" if key == "defensa" else "⚔️" if key == "ataque" else "👥" if key == "soldados" else "📊"
                info_texto += f"{emoji} {key.capitalize()}: {value}\n"
        
        embed.add_field(name="📊 Nuevas estadísticas", value=info_texto, inline=False)
        embed.add_field(
            name="💰 Recursos necesarios",
            value=f"🪨 Piedra: {datos.get('piedra', 0)}\n🪵 Madera: {datos.get('madera', 0)}\n🪙 Oro: {datos.get('oro', 0)}",
            inline=False
        )
        
        view = View()
        mejorar_btn = Button(label="✅ Confirmar Mejora", style=discord.ButtonStyle.green, emoji="✅")
        mejorar_btn.callback = lambda i: self.construir_estructura_interactivo(i, tipo, nivel_siguiente, "mejorar")
        view.add_item(mejorar_btn)
        
        cancelar_btn = Button(label="❌ Cancelar", style=discord.ButtonStyle.red, emoji="❌")
        cancelar_btn.callback = lambda i: self.cancelar_construccion(i)
        view.add_item(cancelar_btn)
        
        await interaction.response.edit_message(content="📋 Información de la mejora:", embed=embed, view=view)

    async def construir_estructura_interactivo(self, interaction, tipo, nivel, accion):
        """Construye o mejora una estructura"""
        usuario_id = str(interaction.user.id)
        datos_usuario = self.obtener_usuario(usuario_id)
        stats = datos_usuario['estadisticas']
        
        datos = MUROS[tipo][nivel]
        
        # Verificar recursos
        errores = []
        if stats['piedra'] < datos.get('piedra', 0):
            errores.append(f"🪨 Piedra: {stats['piedra']}/{datos.get('piedra', 0)}")
        if stats['madera'] < datos.get('madera', 0):
            errores.append(f"🪵 Madera: {stats['madera']}/{datos.get('madera', 0)}")
        if stats['oro'] < datos.get('oro', 0):
            errores.append(f"🪙 Oro: {stats['oro']}/{datos.get('oro', 0)}")
        
        if errores:
            embed = discord.Embed(
                title="❌ RECURSOS INSUFICIENTES",
                color=discord.Color.red()
            )
            embed.add_field(name="📊 Recursos necesarios:", value="\n".join(errores), inline=False)
            await interaction.response.edit_message(content="❌ No tienes suficientes recursos.", embed=embed, view=None)
            return
        
        # Quitar recursos
        stats['piedra'] -= datos.get('piedra', 0)
        stats['madera'] -= datos.get('madera', 0)
        stats['oro'] -= datos.get('oro', 0)
        
        # Guardar estructura
        if 'estructuras' not in datos_usuario:
            datos_usuario['estructuras'] = {}
        
        datos_usuario['estructuras'][tipo] = {
            'nivel': nivel,
            'construido': datetime.now().isoformat()
        }
        
        self.guardar_datos()
        
        embed = discord.Embed(
            title=f"✅ ¡{'MEJORA' if accion == 'mejorar' else 'CONSTRUCCIÓN'} COMPLETADA!",
            description=f"Has {'mejorado a' if accion == 'mejorar' else 'construido'} un **{datos['nombre']}** (Nivel {nivel})",
            color=discord.Color.green()
        )
        
        info_texto = ""
        for key, value in datos.items():
            if key not in ['nombre', 'emoji']:
                emoji = "❤️" if key == "hp" else "🛡️" if key == "defensa" else "⚔️" if key == "ataque" else "👥" if key == "soldados" else "📊"
                info_texto += f"{emoji} {key.capitalize()}: {value}\n"
        
        embed.add_field(name="📊 Estadísticas", value=info_texto, inline=False)
        embed.add_field(
            name="💰 Recursos restantes",
            value=f"🪙 Oro: {stats['oro']}\n🪵 Madera: {stats['madera']}\n🪨 Piedra: {stats['piedra']}",
            inline=False
        )
        
        view = View()
        ver_btn = Button(label="🏗️ Ver Mis Estructuras", style=discord.ButtonStyle.primary, emoji="🏗️")
        ver_btn.callback = lambda i: self.ver_mis_estructuras(i)
        view.add_item(ver_btn)
        
        await interaction.response.edit_message(content="✅ ¡Construcción completada!", embed=embed, view=view)

    async def ver_mis_estructuras(self, interaction):
        """Muestra las estructuras del usuario"""
        usuario_id = str(interaction.user.id)
        datos_usuario = self.obtener_usuario(usuario_id)
        
        embed = discord.Embed(
            title=f"🏗️ TUS ESTRUCTURAS",
            color=discord.Color.blue()
        )
        
        if 'estructuras' not in datos_usuario or not datos_usuario['estructuras']:
            embed.description = "❌ No tienes estructuras construidas"
            await interaction.response.edit_message(content="📋", embed=embed, view=None)
            return
        
        for tipo, info in datos_usuario['estructuras'].items():
            nivel = info['nivel']
            datos = MUROS.get(tipo, {}).get(nivel, {})
            nombre = datos.get('nombre', f"{tipo.capitalize()} Nv.{nivel}")
            
            emojis = {"muro": "🧱", "torre": "🗼", "cuartel": "🏛️"}
            emoji = emojis.get(tipo, "🏗️")
            
            embed.add_field(
                name=f"{emoji} {nombre}",
                value=f"📊 Nivel: {nivel}\n📅 Construido: {info.get('construido', '')[:10]}",
                inline=False
            )
        
        await interaction.response.edit_message(content="📋", embed=embed, view=None)

    async def cancelar_construccion(self, interaction):
        """Cancela la construcción"""
        await interaction.response.edit_message(
            content="❌ Construcción cancelada.",
            embed=None,
            view=None
        )

    async def procesar_mejora(self, ctx, tipo):
        """Procesa la mejora de una estructura"""
        usuario_id = str(ctx.author.id)
        datos_usuario = self.obtener_usuario(usuario_id)
        
        if tipo not in datos_usuario['estructuras']:
            await ctx.send(f"❌ No tienes un {tipo}.")
            return
        
        nivel_actual = datos_usuario['estructuras'][tipo]['nivel']
        nivel_siguiente = nivel_actual + 1
        
        if nivel_siguiente not in MUROS[tipo]:
            await ctx.send(f"⚠️ Ya tienes el nivel máximo para {tipo}.")
            return
        
        datos = MUROS[tipo][nivel_siguiente]
        stats = datos_usuario['estadisticas']
        
        if stats['piedra'] < datos.get('piedra', 0) or \
           stats['madera'] < datos.get('madera', 0) or \
           stats['oro'] < datos.get('oro', 0):
            await ctx.send(f"❌ No tienes suficientes recursos para mejorar a **{datos['nombre']}**")
            return
        
        stats['piedra'] -= datos.get('piedra', 0)
        stats['madera'] -= datos.get('madera', 0)
        stats['oro'] -= datos.get('oro', 0)
        
        datos_usuario['estructuras'][tipo]['nivel'] = nivel_siguiente
        datos_usuario['estructuras'][tipo]['construido'] = datetime.now().isoformat()
        self.guardar_datos()
        
        await ctx.send(f"✅ ¡Has mejorado tu **{datos['nombre']}** al Nivel {nivel_siguiente}!")

    # ============ COMANDOS DE ADMINISTRACIÓN DE RECURSOS ============
    
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

    @commands.command(name='setoro')
    @commands.has_permissions(administrator=True)
    async def set_oro(self, ctx, miembro: discord.Member, cantidad: int):
        """Establece el oro de un usuario (solo admin)"""
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
        """Establece la madera de un usuario (solo admin)"""
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
        """Establece la piedra de un usuario (solo admin)"""
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
        """Establece el HP de un usuario (solo admin)"""
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

# ============ SETUP ============
async def setup(bot):
    await bot.add_cog(SistemaReinos(bot))