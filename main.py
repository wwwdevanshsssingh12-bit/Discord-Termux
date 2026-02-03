import discord
from discord.ext import commands
from discord import app_commands
import datetime

# --- CONFIGURATION ---
TOKEN = 'MTQ1OTQ0MDk1NzIwNzM0NzM1Mg.GTS14n.286Wl1Qr1cH5RhR3ieLn1uRHv2tvzM5Wufyprk'  # Replace with your actual bot token
VERIFICATION_LINK = "https://your-verification-site.com" # Replace with your link
GUILD_ID = 123456789012345678  # Replace with your Server (Guild) ID for faster command syncing

# Initialize Bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Needed for ticket permissions
bot = commands.Bot(command_prefix="!", intents=intents)

# --- VIEWS (BUTTONS) ---

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.blurple, emoji="✅", custom_id="verify_btn")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sends the link as a hidden (ephemeral) message
        await interaction.response.send_message(
            f"Please proceed to the verification site here: {VERIFICATION_LINK}\n\n"
            "Once completed, you will gain full access.",
            ephemeral=True
        )

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction: discord.Interaction, issue_type: str):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")
        
        # Create category if it doesn't exist
        if not category:
            category = await guild.create_category("Tickets")

        # Check if user already has a ticket
        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"You already have a ticket open: {existing_channel.mention}", ephemeral=True)
            return

        # Permission Overwrites
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        # Create Channel
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        # Send Welcome Embed in Ticket
        embed = discord.Embed(
            title=f"{issue_type} Support",
            description=f"Hello {interaction.user.mention}, support will be with you shortly.\n\n**Issue:** {issue_type}",
            color=0x5865F2
        )
        await ticket_channel.send(embed=embed)
        await interaction.response.send_message(f"Ticket created! {ticket_channel.mention}", ephemeral=True)

    @discord.ui.button(label="Unable to verify", style=discord.ButtonStyle.red, custom_id="ticket_unable")
    async def unable_verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Unable to Verify")

    @discord.ui.button(label="Can't see channels after verify", style=discord.ButtonStyle.blurple, custom_id="ticket_cant_see")
    async def cant_see(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Channel Visibility")

    @discord.ui.button(label="Server Down", style=discord.ButtonStyle.grey, custom_id="ticket_server_down")
    async def server_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Server Down Report")

class PrivateServerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def deny_access(self, interaction: discord.Interaction):
        await interaction.response.send_message("❌ **Access Denied:** You are not verified. Please verify to access private servers.", ephemeral=True)

    @discord.ui.button(label="Private Server 1", style=discord.ButtonStyle.green, custom_id="ps_1")
    async def ps1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.deny_access(interaction)

    @discord.ui.button(label="Private Server 2", style=discord.ButtonStyle.green, custom_id="ps_2")
    async def ps2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.deny_access(interaction)
    
    @discord.ui.button(label="Private Server 3", style=discord.ButtonStyle.green, custom_id="ps_3")
    async def ps3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.deny_access(interaction)

class RewardsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Invite Url", style=discord.ButtonStyle.blurple, emoji="🔗", custom_id="invite_url_btn")
    async def invite_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ **Access Denied:** You are not verified. You cannot generate an invite link yet.", ephemeral=True)


# --- BOT EVENTS ---

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    # Load persistent views so buttons work after restart
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(PrivateServerView())
    bot.add_view(RewardsView())
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# --- SETUP COMMAND ---

@bot.tree.command(name="setup", description="Setup specific bot panels")
@app_commands.choices(module=[
    app_commands.Choice(name="Verification Panel", value="verify"),
    app_commands.Choice(name="Ticket Panel", value="ticket"),
    app_commands.Choice(name="Private Server Hub", value="private"),
    app_commands.Choice(name="Rewards Program", value="rewards"),
])
async def setup(interaction: discord.Interaction, module: app_commands.Choice[str]):
    # Check for admin perms
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need Administrator permissions to use this.", ephemeral=True)
        return

    await interaction.response.send_message(f"Setting up {module.name}...", ephemeral=True)
    channel = interaction.channel

    # 1. VERIFICATION PANEL
    if module.value == "verify":
        embed = discord.Embed(
            title="Verification",
            description="Verify to our server to join giveaways, do fun stuff and more, and get access to almost everything.\n\n**System Setup Complete:**\nServer architecture has been built.",
            color=0x9b59b6 # Purple-ish
        )
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        embed.set_footer(text="Bloxify System")
        # You can add the specific cube image if you have a URL for it using embed.set_image(url="...")
        
        await channel.send(embed=embed, view=VerifyView())

    # 2. TICKET PANEL
    elif module.value == "ticket":
        embed = discord.Embed(
            title="Problem related verification",
            description="Let's Fix",
            color=0x9b59b6
        )
        # Using a placeholder image for the cube concept
        embed.set_image(url="https://dummyimage.com/600x400/2f004f/fff&text=Verification+Support") 
        
        await channel.send(embed=embed, view=TicketView())

    # 3. PRIVATE SERVER HUB
    elif module.value == "private":
        embed = discord.Embed(
            title="🎮 Official Private Server Hub",
            description=(
                "**Exclusive Access for Verified Members**\n"
                "We provide premium, low-latency private servers.\n\n"
                "**Server Benefits:**\n"
                "⚡ Zero Lag Performance\n"
                "🛡️ Griefer-Free Environment\n\n"
                "*Select a server node below to connect. Access is restricted.*"
            ),
            color=0x9b59b6
        )
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        embed.set_footer(text="Private Network System")
        
        await channel.send(embed=embed, view=PrivateServerView())

    # 4. REWARDS PROGRAM
    elif module.value == "rewards":
        embed = discord.Embed(
            title="📦 Exclusive Invite Rewards Program ✨",
            description=(
                "Hey everyone!\n"
                "We are excited to announce our official Invite Rewards system.\n"
                "Turn your invites into amazing prizes! 🚀\n\n"
                "**💰 Robux Rewards**\n"
                "The more friends you bring, the more you earn!\n"
                "5 Invites ➔ 10 Robux 💵\n"
                "10 Invites ➔ 20 Robux 💵\n"
                "15 Invites ➔ 30 Robux 💵\n\n"
                "**🐍 Grand Prize:**\n"
                "Perm Dragon\n"
                "We have a massive reward for our top recruiters:\n"
                "50 Invites ➔ Permanent Dragon Fruit 🍎\n\n"
                "**⚠️ Note:** This is strictly limited to the first 3 users who reach the goal!\n\n"
                "Requirements: To ensure fairness and prevent botting: **You must be verified.**"
            ),
            color=0xFFD700 # Gold color
        )
        
        await channel.send(embed=embed, view=RewardsView())

# Run the bot
bot.run(TOKEN)
