
import discord
from discord.ext import commands
from discord import app_commands
import os
import aiosqlite
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    async with aiosqlite.connect("league.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                captain TEXT
            )
        """)
        await db.commit()

    await bot.tree.sync()
    print(f"Blox Strike League online: {bot.user}")

@bot.tree.command(name="ping", description="Sprawdza działanie bota")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏆 Blox Strike League działa!")

@bot.tree.command(name="druzyna_dodaj", description="Dodaje drużynę do ligi")
@app_commands.describe(nazwa="Nazwa drużyny", kapitan="Kapitan drużyny")
async def druzyna_dodaj(
    interaction: discord.Interaction,
    nazwa: str,
    kapitan: discord.Member
):
    async with aiosqlite.connect("league.db") as db:
        try:
            await db.execute(
                "INSERT INTO teams (name, captain) VALUES (?, ?)",
                (nazwa, str(kapitan.id))
            )
            await db.commit()
        except aiosqlite.IntegrityError:
            await interaction.response.send_message(
                "❌ Taka drużyna już istnieje!",
                ephemeral=True
            )
            return

    await interaction.response.send_message(
        f"🏆 Dodano drużynę **{nazwa}**! Kapitan: {kapitan.mention}"
    )

@bot.tree.command(name="druzyny", description="Pokazuje drużyny ligi")
async def druzyny(interaction: discord.Interaction):
    async with aiosqlite.connect("league.db") as db:
        async with db.execute("SELECT name, captain FROM teams") as cursor:
            rows = await cursor.fetchall()

    if not rows:
        await interaction.response.send_message("Nie ma jeszcze drużyn.")
        return

    opis = "\n".join(
        f"🏆 **{name}** — <@{captain}>"
        for name, captain in rows
    )
    await interaction.response.send_message(
        f"**BLOX STRIKE LEAGUE — DRUŻYNY**\n\n{opis}"
    )

if not TOKEN:
    raise RuntimeError("Brak DISCORD_TOKEN w ustawieniach środowiska!")

bot.run(TOKEN)
  
