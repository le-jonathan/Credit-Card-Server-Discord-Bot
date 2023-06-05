import discord
from discord.ext import commands
import datetime
import random
import json
import os
from discord.utils import find

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

RULES_CHANNEL_ID = 932447065370398791
REFERRALS_CHANNEL_ID = 1105204207172190368
DISCORD_LOGS_CHANNEL_ID = 1105328983245082725
NEEDS_HELP_CHANNEL_ID = 1105328983245082725
COOLDOWN_TIME = 7*24*60*60
GUILD_ID = 931760921825665034
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"last_message": {}, "messages_since_last_referral": {}, "required_messages": {}, "confirmation_sent": {}}
    
    if "confirmation_sent" not in data:
        data["confirmation_sent"] = {}

    return data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()
last_message = {int(user_id): datetime.datetime.fromisoformat(timestamp) for user_id, timestamp in data["last_message"].items()}
messages_since_last_referral = {int(user_id): count for user_id, count in data["messages_since_last_referral"].items()}
required_messages = {int(user_id): count for user_id, count in data["required_messages"].items()}
confirmation_sent = {int(user_id): datetime.datetime.fromisoformat(timestamp) for user_id, timestamp in data["confirmation_sent"].items()}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await create_rules_message()

@bot.event
async def on_message(message):
    if isinstance(message.author, discord.Member):
        diamond_status_role = find(lambda r: r.name == "Diamond Status", message.author.roles)
        diamond_role = find(lambda r: r.name == "Diamond", message.author.roles)
        has_higher_level_role = any([find(lambda r: r.name == f"Level {i}", message.author.roles) for i in range(10, 31, 10)])
    else:
        diamond_status_role = None
        diamond_role = None
        has_higher_level_role = False

    if message.channel.id == REFERRALS_CHANNEL_ID:
        
        is_moderator = any([role.name == "Moderator" for role in message.author.roles])

        if not is_moderator and message.author.id in last_message:
            if (datetime.datetime.now() - last_message[message.author.id]).total_seconds() < COOLDOWN_TIME:
                await message.delete()

                if message.author == bot.user:
                    return

                user = await bot.fetch_user(message.author.id)
                await user.send(f"{message.author.mention}, You can only post once in 7 days in the #referrals channel. Your message has been deleted and you can post again after {datetime.datetime.fromtimestamp((last_message[message.author.id] + datetime.timedelta(seconds=COOLDOWN_TIME)).timestamp()).strftime('%Y-%m-%d %H:%M:%S')} UTC time.")
                return

            if not has_higher_level_role and messages_since_last_referral.get(message.author.id, 0) < required_messages.get(message.author.id, 50) and diamond_role:
                await message.delete()
                await message.author.remove_roles(diamond_role)
                user = await bot.fetch_user(message.author.id)
                await user.send("Your Diamond role has been removed because you were not active enough. Become active again and you will regain the Diamond role.")
                return

        last_message[message.author.id] = datetime.datetime.now()
        messages_since_last_referral[message.author.id] = 0
        if not has_higher_level_role:
            required_messages[message.author.id] = random.randint(50, 75)

        data["last_message"] = {str(user_id): timestamp.isoformat() for user_id, timestamp in last_message.items()}
        data["messages_since_last_referral"] = messages_since_last_referral
        data["required_messages"] = required_messages
        save_data(data)

    if message.channel.type == discord.ChannelType.private:
        await process_diamond_member_reply(message)

    if message.author.id in last_message:
        messages_since_last_referral[message.author.id] += 1

        if diamond_status_role and not diamond_role and not has_higher_level_role:
            if messages_since_last_referral[message.author.id] >= required_messages.get(message.author.id, 50):
                diamond_role = discord.utils.get(message.guild.roles, name="Diamond")
                await message.author.add_roles(diamond_role)
                user = await bot.fetch_user(message.author.id)
                await user.send("You have regained the Diamond role!")

        data["messages_since_last_referral"] = messages_since_last_referral
        save_data(data)

    await bot.process_commands(message)

@bot.event
async def on_member_update(before, after):
    diamond_status_role_name = "Diamond Status"
    diamond_role_name = "Diamond"
    had_diamond_status_role = find(lambda r: r.name == diamond_status_role_name, before.roles)
    has_diamond_status_role = find(lambda r: r.name == diamond_status_role_name, after.roles)
    if has_diamond_status_role and not had_diamond_status_role:
        has_higher_level_role = any([r.name.startswith("Level ") and int(r.name.split(" ")[-1]) >= 10 for r in after.roles])
        if has_higher_level_role:
            diamond_role = discord.utils.get(after.guild.roles, name=diamond_role_name)
            await after.add_roles(diamond_role)
            await after.send("Welcome to the Diamond Membership! You are level 10 or above, therefore you have direct access to the full Diamond Membership. Remember to stay active to retain full Diamond Membership.")
        else:
            await after.send("You are now an active Diamond Status member! To receive full access to Diamond Status perks, please confirm that you understand that you must be ACTIVE in the server to retain your Diamond Status membership perks. If you do not meet the requirements, your role will be revoked until you meet those requirements again. Please reply with \"CONFIRM\" or \"HELP\" to indicate your understanding of this message.")
            confirmation_sent[after.id] = datetime.datetime.now()
            data["confirmation_sent"] = {str(user_id): timestamp.isoformat() for user_id, timestamp in confirmation_sent.items()}
            save_data(data)
    if had_diamond_status_role and not has_diamond_status_role:
        diamond_role = find(lambda r: r.name == diamond_role_name, after.roles)
        if diamond_role:
            await after.remove_roles(diamond_role)
            await after.send("Your Diamond role has been removed because you no longer have the Diamond Status role.")

async def process_diamond_member_reply(message):
    user = message.author
    guild = bot.get_guild(GUILD_ID)
    member = await guild.fetch_member(user.id)
    if message.content.lower() == "confirm" and user.id in confirmation_sent:
        diamond_role = discord.utils.get(guild.roles, name="Diamond")
        await member.add_roles(diamond_role)
        await member.send("Thanks for confirming, you have been given the Diamond role. Welcome to the Diamond Status, and thank you for supporting thee server. You can always type \"HELP\" here to get help from a moderator!")
        del confirmation_sent[user.id]
        data["confirmation_sent"] = {str(user_id): timestamp.isoformat() for user_id, timestamp in confirmation_sent.items()}
        save_data(data)
    elif message.content.lower() == "help":
        help_needed_role = discord.utils.get(guild.roles, name="Help")
        await member.add_roles(help_needed_role)
        logs_channel = bot.get_channel(DISCORD_LOGS_CHANNEL_ID)
        moderator_role = discord.utils.get(guild.roles, name='Moderator')
        await logs_channel.send(f"{member.mention} needs help! {moderator_role.mention}")
        
async def create_rules_message():
    channel_id = RULES_CHANNEL_ID
    channel = bot.get_channel(channel_id)
    async for message in channel.history(limit=100):
        if message.author == bot.user:
            await message.delete()
    
    rules_message_part1 = """
    ```yaml
Welcome to The Credit Community!

Please take a moment to read and adhere to the following rules:

THE CREDIT COMMUNITY RULES

1. Be respectful, civil, and welcoming to all members.

2. Discriminatory language, hate speech, and trolling is prohibited.

3. No drama or toxicity; keep it in the DMs.

4. No bullying or harassment in any way, shape, or form.

5. Any behavior intended to target specific groups/individuals is prohibited.

6. Community members are free to express themselves openly and give constructive criticism and feedback.

7. Remain on topic and use channels correctly and appropriately. This includes being cautious when introducing conversations regarding controversial or sensitive topics.

8. No flooding or spamming chat messages. This includes unnecessarily mentioning any user or group, along with sending excessive amounts of messages, emojis, videos, memes, pics, etc.

9. No NSFW or obscene content. This includes text, images, or links featuring nudity, sex, hard violence, or other graphically disturbing content.
    ```
    """

    rules_message_part2 = """
    ```yaml
10. No personal medical information, such as lab results, etc.

11. No bragging or attempting to make yourself seem better than another member.

12. Community members should strive for a certain level of quality in their messages.

13. The ability to post referral links is strictly limited to Verified Diamond Status Members. Referral posts are limited to once per week. A minimum level of engagement is required to retain Verified Diamond Member Status.

14. No fake identities or catfishing of any kind.

15. Do not search for members personal information.

16. We do not allow you to ask for handouts, such as credit card information.

17. Regardless of age, strive to treat each other as you would like to be treated yourself.

18. The Credit Community promotes diversity and inclusivity. We expect your interactions in this community to be respectful and guided by these rules.

19. By joining The Credit Community, you are certifying/admitting that you are at least 18 years old.

20. Follow all staff instructions immediately and at all times.

Breaking any of the following rules may result in a timeout or ban. If we miss any rule breakers, please @ owners or staff immediately.
    ```

React with a ✅ below to verify that you have read and agree to the rules.
    """
    
    message1 = await channel.send(rules_message_part1)
    message2 = await channel.send(rules_message_part2)
    await message2.add_reaction('✅')

''' Server no longer has the Verified role, reinstate if server wants to bring back the role
@bot.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == RULES_CHANNEL_ID and payload.emoji.name == "✅":
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        verified_role = discord.utils.get(guild.roles, name="Verified")
        await member.add_roles(verified_role)
        '''

@bot.command()
@commands.has_any_role('Moderator', 'Owner', 'Intern')
async def clear(ctx, user: discord.Member):
    if user.id in last_message:
        del last_message[user.id]
        data["last_message"] = {str(user_id): timestamp.isoformat() for user_id, timestamp in last_message.items()}
        save_data(data)
        await ctx.send(f"{user.mention}'s cooldown has been cleared.")
    else:
        await ctx.send(f"{user.mention} doesn't have an active cooldown.")

my_secret = os.environ['token']
bot.run(my_secret)
