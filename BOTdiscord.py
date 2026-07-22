import discord
from discord.ext import commands
import random
import yt_dlp

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="*", #prefixo do bot
    intents=intents
)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"BOT ONLINE: {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.event
async def on_member_join(member):
    canal = discord.utils.get(
        member.guild.text_channels,
        name="geral"
    )

    if canal:
        await canal.send(
            f"🎉 Bem-vindo {member.mention}!"
        )


jogos_forca = {}
paineis_cargos = {}

categorias = {
    "animais": [
        ("galinha", "Ave que bota ovos"),
        ("cobra", "Réptil sem pernas"),
        ("elefante", "Animal grande com tromba"),
        ("papagaio", "Ave que imita sons"),
        ("cachorro", "Melhor amigo do homem"),
        ("gato", "Animal que mia"),
        ("macaco", "Animal que gosta de bananas")
    ],

    "objetos": [
        ("martelo", "Usado para bater pregos"),
        ("paralelepipedo", "Bloco usado em ruas"),
        ("computador", "Máquina usada para programar"),
        ("cadeira", "Objeto usado para sentar"),
        ("telefone", "Usado para fazer ligações"),
        ("garrafa", "Usada para líquidos")
    ],

    "comidas": [
        ("ketchup", "Molho vermelho"),
        ("limao", "Fruta cítrica"),
        ("banana", "Fruta amarela"),
        ("hamburguer", "Pão com carne"),
        ("pizza", "Comida redonda famosa"),
        ("chocolate", "Doce de cacau")
    ],

    "palavras": [
        ("efervescencia", "Formação de bolhas"),
        ("citrico", "Relacionado ao limão"),
        ("programacao", "Criação de códigos"),
        ("discord", "Aplicativo de comunidades"),
        ("servidor", "Lugar onde ficam comunidades")
    ]
}

@bot.command()
async def categoriasforca(ctx): 
    lista = "\n".join(
        f"• {categoria}"
        for categoria in categorias.keys()
    )

    await ctx.send(
        f"📚 Categorias disponíveis:\n\n{lista}"
    )

@bot.command()
async def forca(ctx, categoria=None):
    if categoria is None:
        await ctx.send(
            "Escolha uma categoria.\n"
            "Use `*categoriasforca`."
        )
        return

    categoria = categoria.lower()

    if categoria not in categorias:
        await ctx.send("Categoria inválida.")
        return

    palavra, dica = random.choice(
        categorias[categoria]
    )

    jogos_forca[ctx.channel.id] = {
        "palavra": palavra,
        "dica": dica,
        "categoria": categoria,
        "letras_usadas": [],
        "erros": 0
    }

    palavra_escondida = " ".join(
        "_" for _ in palavra
    )

    await ctx.send(
        f"🎮 Forca iniciada!\n\n"
        f"📚 Categoria: `{categoria}`\n"
        f"💡 Dica: `{dica}`\n"
        f"📝 Palavra: `{palavra_escondida}`\n\n"
        f"Digite letras no chat."
    )

@bot.command()
async def reiniciarforca(ctx):
    jogo = jogos_forca.get(ctx.channel.id)

    if jogo is None:
        await ctx.send("Nenhum jogo ativo.")
        return

    categoria = jogo["categoria"]

    palavra, dica = random.choice(
        categorias[categoria]
    )

    jogos_forca[ctx.channel.id] = {
        "palavra": palavra,
        "dica": dica,
        "categoria": categoria,
        "letras_usadas": [],
        "erros": 0
    }

    palavra_escondida = " ".join(
        "_" for _ in palavra
    )

    await ctx.send(
        f"🔄 Jogo reiniciado!\n\n"
        f"📚 Categoria: `{categoria}`\n"
        f"💡 Dica: `{dica}`\n"
        f"📝 Palavra: `{palavra_escondida}`"
    )

@bot.command()
async def pararforca(ctx):
    if ctx.channel.id in jogos_forca:
        del jogos_forca[ctx.channel.id]
        await ctx.send("🛑 Jogo encerrado.")
    else:
        await ctx.send("Nenhum jogo ativo.")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    jogo = jogos_forca.get(
        message.channel.id
    )

    if jogo:
        letra = message.content.lower().strip()

        if len(letra) == 1 and letra.isalpha():
            if letra in jogo["letras_usadas"]:
                await message.channel.send(
                    "⚠️ Essa letra já foi usada."
                )
                return

            jogo["letras_usadas"].append(letra)

            if letra not in jogo["palavra"]:
                jogo["erros"] += 1

            palavra_mostrada = " ".join(
                caractere
                if caractere in jogo["letras_usadas"]
                else "_"
                for caractere in jogo["palavra"]
            )

            await message.channel.send(
                f"📝 Palavra: `{palavra_mostrada}`\n"
                f"💡 Dica: `{jogo['dica']}`\n"
                f"❌ Erros: `{jogo['erros']}/6`\n"
                f"🔤 Letras usadas: "
                f"`{', '.join(jogo['letras_usadas'])}`"
            )

            if "_" not in palavra_mostrada:
                await message.channel.send(
                    f"🎉 Vocês venceram!\n"
                    f"A palavra era: `{jogo['palavra']}`"
                )

                del jogos_forca[
                    message.channel.id
                ]

            elif jogo["erros"] >= 6:
                await message.channel.send(
                    f"💀 Vocês perderam!\n"
                    f"A palavra era: `{jogo['palavra']}`"
                )

                del jogos_forca[
                    message.channel.id
                ]

            return

    await bot.process_commands(message)


@bot.tree.command( 
    name="embed",
    description="Criar uma embed"
)
async def embed(
    interaction: discord.Interaction,
    titulo: str,
    descricao: str
):
    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=discord.Color.purple() 
    )

    embed.set_footer(
        text=f"Enviado por {interaction.user.name}"
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.tree.command( 
    name="painel_cargos",
    description="Cria um painel de cargos por reação"
)
async def painel_cargos(
    interaction: discord.Interaction,
    titulo: str,
    descricao: str,
    emoji_1: str,
    cargo_1: discord.Role,
    texto_1: str,
    emoji_2: str,
    cargo_2: discord.Role,
    texto_2: str,
    emoji_3: str = None,
    cargo_3: discord.Role = None,
    texto_3: str = None,
    emoji_4: str = None,
    cargo_4: discord.Role = None,
    texto_4: str = None,
    emoji_5: str = None,
    cargo_5: discord.Role = None,
    texto_5: str = None
):
    opcoes = [
        (emoji_1, cargo_1, texto_1),
        (emoji_2, cargo_2, texto_2),
        (emoji_3, cargo_3, texto_3),
        (emoji_4, cargo_4, texto_4),
        (emoji_5, cargo_5, texto_5)
    ]

    opcoes_validas = []

    for emoji, cargo, texto in opcoes:
        if emoji and cargo and texto:
            opcoes_validas.append(
                (emoji, cargo, texto)
            )

    descricao_embed = descricao + "\n\n"

    for emoji, cargo, texto in opcoes_validas:
        descricao_embed += f"{emoji} {texto} — {cargo.mention}\n"

    embed = discord.Embed(
        title=titulo,
        description=descricao_embed,
        color=discord.Color.purple()
    )

    await interaction.response.send_message(
        embed=embed
    )

    mensagem = await interaction.original_response()

    paineis_cargos[mensagem.id] = {}

    for emoji, cargo, texto in opcoes_validas:
        await mensagem.add_reaction(emoji)
        paineis_cargos[mensagem.id][emoji] = cargo.id

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member is None:
        return

    if payload.member.bot:
        return

    if payload.message_id not in paineis_cargos:
        return

    emoji = str(payload.emoji)

    if emoji not in paineis_cargos[payload.message_id]:
        return

    guild = bot.get_guild(payload.guild_id)
    cargo_id = paineis_cargos[payload.message_id][emoji]
    cargo = guild.get_role(cargo_id)

    if cargo:
        await payload.member.add_roles(cargo)

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id not in paineis_cargos:
        return

    emoji = str(payload.emoji)

    if emoji not in paineis_cargos[payload.message_id]:
        return

    guild = bot.get_guild(payload.guild_id)
    membro = guild.get_member(payload.user_id)
    cargo_id = paineis_cargos[payload.message_id][emoji]
    cargo = guild.get_role(cargo_id)

    if membro and cargo:
        await membro.remove_roles(cargo)


@bot.command() 
async def tocar(ctx, *, busca):
    if ctx.author.voice is None:
        await ctx.send("Entre em uma call primeiro.")
        return

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "default_search": "ytsearch",
        "noplaylist": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(busca, download=False)

            if "entries" in info:
                info = info["entries"][0]

            url = info["url"]
            titulo = info["title"]

    except Exception as erro:
        await ctx.send("❌ Não consegui encontrar ou carregar essa música.")
        print(f"Erro no yt-dlp: {erro}")
        return

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    ffmpeg_options = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn"
    }

    try:
        audio = discord.FFmpegPCMAudio(
            url,
            **ffmpeg_options
        )

        def depois(error):
            if error:
                print(f"Erro ao tocar música: {error}")

        ctx.voice_client.play(audio, after=depois)

        await ctx.send(f"🎵 Tocando agora: `{titulo}`")

    except Exception as erro:
        await ctx.send("❌ Deu erro ao tentar tocar a música.")
        print(f"Erro no FFmpeg/Discord: {erro}")

bot.run("COLOQUE_SEU_TOKEN_AQUI")
