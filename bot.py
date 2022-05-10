import asyncio
import datetime
import logging
from platform import python_version
import aiohttp
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot as BotBase
import os
import random
from glob import glob
from itertools import cycle
import json
from collections import Counter, defaultdict
from handler.database import create_database_pool

COGS = [path.split("\\")[-1][:-3] for path in glob("./cogs/*.py")]

"""this is the mai n file that run the bot"""
print(
    " eeeee e   e eeeee eeeee e    e    eeeee  eeeee eeeeeee \n "
    "8     8   8 8     8     8    8    8    8 8   8   88  \n "
    "8eeee 8   8 8eeee 8eeee 8eeee8    8eee8e 8   8   88  \n"
    '     8 8   8     8     8   88      8    8 8   8   88  \n'
    " 8ee88 88ee8 8ee88 8ee88   88      88eee8 8eee8   88  \n")


def get_prefix(client, message):  ##first we define get_prefix
    """load prefix function"""
    try:
        with open('data/prefixes.json',
                  'r') as f:  # we open and read the prefixes.json, assuming it's in the same file
            prefixes = json.load(f)  # load the json as prefixes
            return prefixes[str(message.guild.id)]
    except KeyError:

        with open('data/prefixes.json', 'r') as f:  # read the prefix.json file
            prefixes = json.load(f)  # load the json file

        prefixes[str(message.guild.id)] = '$'  # default prefix

        with open('data/prefixes.json', 'w') as f:  # write in the prefix.json "message.guild.id": "bl!"
            json.dump(prefixes, f, indent=4)  # the indent is to make everything look a bit neater
        with open('data/prefixes.json',
                  'r') as t:  ##we open and read the prefixes.json, assuming it's in the same file
            prefixes = json.load(t)

            return prefixes[str(message.guild.id)]
    except:
        return


# class bot the main code
class SussyBot(commands.Bot):
    user: discord.ClientUser
    bot_app_info: discord.AppInfo
    """the code that run the bot and load prefix"""

    def __init__(self):
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)
        self.ready = False
        super().__init__(
            command_prefix=(get_prefix),
            case_insensitive=True,
            intents=discord.Intents.all(),
            application_id=953274927027458148,
            heartbeat_timeout=1000.0,
        )
        # CUSTOM
        self.online_time = datetime.datetime.now(datetime.timezone.utc)
        self.version = "0.0.11"
        self.owner_id = 888058231094665266
        self.console_message_prefix = "Sussy bot"
        self.changelog = "https://discord.gg/wC37kY3qwH"
        self.dashboard = "https://sussybot.xyz"
        self.fake_ip = "ur mom"
        self.fake_location = "new-york"
        self.simple_user_agent = "Sussybot (Discord Bot)"
        self.user_agent = (
            "Sussybot (Discord Bot) "
            f"Python/{python_version()} "
            f"aiohttp/{aiohttp.__version__}"
            f"discord.py/{discord.__version__}"
        )
        # colours
        self.bot_color = self.bot_colour = 0xff0047
        self.embed_default_colour = self.embed_default_colour = 0x00ffad
        self.pink_color = self.pink_color = 0xff0f8c
        self.blue_color = self.blue_color = 0x356eff
        self.red_color = self.red_color = 0xff0047
        self.cyan_color = self.cyan_color = 0x00ffad
        self.dark_theme_background_color = self.dark_theme_background_colour = 0x36393e
        self.white_color = self.white_colour = 0xffffff
        self.black_color = self.white_color = 0x000000
        self.youtube_color = self.youtube_colour = 0xcd201f
        self.violet_color = self.violet_color = 0xba9aeb
        self.green_colour = self.green_colour = 0x00ff85
        self.yellow_colour = self.yellow_colour = 0xffe000

        # database
        self.db = self.database = self.database_connection_pool = None
        self.connected_to_database = asyncio.Event()
        self.connected_to_database.set()

    # load cogs from other files
    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.bot_app_info = await self.application_info()
        self.owner_id = self.bot_app_info.owner.id
        await self.initialize_database()
        COGS = ["messagess","randomapi"]
        print("loading cogs ....")
        print("h")
        for cog in COGS:
            await self.load_extension(f"cogs.{cog}")
            print(f"{cog} loaded ")
        print("setup complete")

    # connect to database execute on setup hook
    async def connect_to_database(self):
        if self.database_connection_pool:
            return
        if self.connected_to_database.is_set():
            self.connected_to_database.clear()
            self.db = self.database = self.database_connection_pool = await create_database_pool()
            self.connected_to_database.set()
        else:
            await self.connected_to_database.wait()

    # setup database and create tables
    async def initialize_database(self):
        await self.connect_to_database()
        await self.db.execute("CREATE SCHEMA IF NOT EXISTS chat")
        await self.db.execute("CREATE SCHEMA IF NOT EXISTS direct_messages")
        await self.db.execute("CREATE SCHEMA IF NOT EXISTS meta")
        await self.db.execute("CREATE SCHEMA IF NOT EXISTS guilds")
        await self.db.execute("CREATE SCHEMA IF NOT EXISTS users")
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS chat.messages (
                created_at				TIMESTAMPTZ, 
                message_id				BIGINT PRIMARY KEY, 
                author_id				BIGINT, 
                author_name				TEXT, 
                author_discriminator	TEXT, 
                author_display_name		TEXT, 
                direct_message			BOOL, 
                channel_id				BIGINT, 
                channel_name			TEXT, 
                guild_id				BIGINT, 
                guild_name				TEXT, 
                message_content			TEXT, 
                embeds					JSONB [], 
                thread					BOOL, 
                thread_id				BIGINT, 
                thread_name				TEXT
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS chat.messagecount(
               guild_id         BIGINT,
               user_id          BIGINT,
               message          INT,
               PRIMARY KEY		(guild_id, user_id)
                                
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS chat.edits (
                edited_at		TIMESTAMPTZ, 
                message_id		BIGINT REFERENCES chat.messages(message_id) ON DELETE CASCADE, 
                before_content	TEXT,
                after_content	TEXT, 
                before_embeds	JSONB [], 
                after_embeds	JSONB [], 
                PRIMARY KEY		(edited_at, message_id)
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS direct_messages.prefixes (
                channel_id	BIGINT PRIMARY KEY, 
                prefixes	TEXT []
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS guilds.prefixes (
                guild_id	BIGINT PRIMARY KEY, 
                prefixes	TEXT []
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS guilds.settings (
                guild_id		BIGINT, 
                name			TEXT, 
                setting			BOOL, 
                PRIMARY KEY		(guild_id, name)
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS meta.commands_invoked (
                command		TEXT PRIMARY KEY, 
                invokes		BIGINT
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS meta.message_context_menu_commands (
                command			TEXT PRIMARY KEY, 
                invocations		BIGINT
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS meta.restart_channels (
                channel_id				BIGINT PRIMARY KEY, 
                player_text_channel_id	BIGINT, 
                restart_message_id		BIGINT
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS meta.slash_commands (
                command			TEXT PRIMARY KEY, 
                invocations		BIGINT
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS meta.stats (
                timestamp			TIMESTAMPTZ PRIMARY KEY DEFAULT NOW(), 
                uptime				INTERVAL, 
                restarts			INT, 
                cogs_reloaded		INT, 
                commands_invoked	BIGINT, 
                reaction_responses	BIGINT, 
                menu_reactions		BIGINT
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS meta.user_context_menu_commands (
                command			TEXT PRIMARY KEY, 
                invocations		BIGINT
            )
            """
        )
        previous = await self.db.fetchrow(
            """
            SELECT * FROM meta.stats
            ORDER BY timestamp DESC
            LIMIT 1
            """
        )
        if previous:
            await self.db.execute(
                """
                INSERT INTO meta.stats (timestamp, uptime, restarts, cogs_reloaded, commands_invoked, reaction_responses, menu_reactions)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT DO NOTHING
                """,
                self.online_time, previous["uptime"], previous["restarts"],
                previous["cogs_reloaded"], previous["commands_invoked"], previous["reaction_responses"],
                previous["menu_reactions"]
            )
        else:
            await self.db.execute(
                """
                INSERT INTO meta.stats (timestamp, uptime, restarts, cogs_reloaded, commands_invoked, reaction_responses, menu_reactions)
                VALUES ($1, INTERVAL '0 seconds', 0, 0, 0, 0, 0)
                """,
                self.online_time
            )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS users.stats (
                user_id										BIGINT PRIMARY KEY, 
                commands_invoked							INT, 
                slash_command_invocations					BIGINT, 
                message_context_menu_command_invocations	BIGINT, 
                user_context_menu_command_invocations		BIGINT
            )
            """
        )

    def print(self, message):
        print(f"[{datetime.datetime.now().isoformat()}] > {self.console_message_prefix} > {message}")
    # do ready tasks
    @property
    async def app_info(self):
        if not hasattr(self, "_app_info"):
            self._app_info = await self.application_info()
        return self._app_info

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    # the code that change bot status in every hours.
    @tasks.loop(seconds=20)
    async def change_status(self):
        status = cycle(
            ["do not disturb me :)", '$help', 'Green apple', 'amongus', 'SUS', 'bruh', 'ur mom', '0101000101',
             'game of life', 'what do you know about about rolling down in the deep'])
        await self.change_presence(status=discord.Status.online,
                                   activity=discord.Activity(type=discord.ActivityType.playing, name=next(status)))
    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.print("ready")
            print("status loop complete")
            print(f"bot is logged as {self.user}")
        else:
            self.print('bot reconnected.')

    def reply(self, content, *args, **kwargs):
        return self.send(f"{self.author.display_name}:\n{content}", **kwargs)
    async def on_message_edit(self, before, after):
        if after.edited_at != before.edited_at:
            if before.content != after.content:
                await self.db.execute(
                    """
                    INSERT INTO chat.edits (edited_at, message_id, before_content, after_content)
                    SELECT $1, $2, $3, $4
                    WHERE EXISTS (SELECT * FROM chat.messages WHERE chat.messages.message_id = $2)
                    ON CONFLICT (edited_at, message_id) DO
                    UPDATE SET before_content = $3, after_content = $4
                    """,
                    after.edited_at.replace(tzinfo=datetime.timezone.utc), after.id,
                    before.content.replace('\N{NULL}', ""), after.content.replace('\N{NULL}', "")
                )
            before_embeds = [embed.to_dict() for embed in before.embeds]
            after_embeds = [embed.to_dict() for embed in after.embeds]
            if before_embeds != after_embeds:
                await self.db.execute(
                    """
                    INSERT INTO chat.edits (edited_at, message_id, before_embeds, after_embeds)
                    SELECT $1, $2, $3, $4
                    WHERE EXISTS (SELECT * FROM chat.messages WHERE chat.messages.message_id = $2)
                    ON CONFLICT (edited_at, message_id) DO
                    UPDATE SET before_embeds = CAST($3 AS jsonb[]), after_embeds = CAST($4 AS jsonb[])
                    """,
                    after.edited_at.replace(tzinfo=datetime.timezone.utc), after.id, before_embeds, after_embeds
                )


    # load the prefix on guild join
    async def on_guild_join(self, guild):  # when the bot joins the guild
        await self.db.execute(
            """
            INSERT INTO guilds.prefixes (guild_id, prefixes)
            VALUES ($1, $2)
            ON CONFLICT (guild_id) DO NOTHING
            """,
            guild.id, "$"
        )
        with open('data/prefixes.json', 'r') as f:  # read the prefix.json file
            prefixes = json.load(f)  # load the json file
        prefixes[str(guild.id)] = '$'  # default prefix
        with open('data/prefixes.json', 'w') as f:  # write in the prefix.json "message.guild.id": "bl!"
            json.dump(prefixes, f, indent=4)  # the indent is to make everything look a bit neater
        print(f"{guild.name} prefix loaded")
        """send to support server that bot is joined the guild"""

    # pop the guild prefix on leaving from the guild
    async def on_guild_remove(self, guild):
        await self.db.execute(
            """
            DELETE FROM guilds.prefixes 
            WHERE guild_id = $1
            """,
            guild.id
        )
        with open('data/prefixes.json', 'r') as f:  # read the file
            prefixes = json.load(f)

        prefixes.pop(str(guild.id))
        with open('data/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

    async def close(self) -> None:
        await super().close()
        await self.session.close()

    async def start(self) -> None:
        await super().start(token, reconnect=True)

    async def on_resumed(self):
        self.print("resumed")

    async def on_disconnect(self):
        self.print("disconnected")

    async def shutdown_tasks(self):
        # Close database connection
        await self.database_connection_pool.close()

    """the random words that bot sent"""

    # this is the code that make the bot automaticly respose on ping
    async def on_message(self, message):

        a = ["keep your mouth close",
             " dont disturb me :)",
             "stfu",
             "shut your mouth",
             "you smell",
             "nuts?",
             "why you pinged me ",
             "among us",
             "go outside touch some grass",
             "ur mom",
             "imposter was ejected",
             "you are sus",
             "SUS",
             "What you want to me",
             "red was the imposter",
             "yo! you looking nice today :)",
             "hmm tell me who is baka",
             "joe mama",
             "retard"
             ]
        message_in = message.content
        # logging
        print(f"{message.guild} {message.channel} : {message.author}: {message.author.display_name}: {message.content}")

        if message.author.bot:
            return
        elif message_in.lower().find('sus') != -1:
            await message.channel.send("amongus", delete_after=10)

        elif (self.user in message.mentions) and message_in.lower().find('prefix') != -1:
            v = await self.get_prefix(message)
            embed = discord.Embed(title=f"YO :wave:  my prefix is {v}", )

            await message.channel.send(embed=embed)
        elif self.user in message.mentions:
            if message_in.lower().find('amongus') != -1 or message_in.lower().find(
                    'cool') != -1 or message_in.lower().find('good') != -1 or message_in.lower().find('nice') != -1:
                await message.channel.send(f'amongus')


            elif message_in.lower().find('bad') != -1 or message_in.lower().find(
                    'horrible') != -1 or message_in.lower().find('suck') != -1 or message_in.lower().find(
                'terrible') != -1 or message_in.lower().find('waste') != -1 or message_in.lower().find(
                'fk') != -1 or message_in.lower().find('fuck') != -1:
                await message.channel.send(f'ur mom', delete_after=11)

            elif message_in.lower().find('hi') != -1 or message_in.lower().find(
                    'helo') != -1 or message_in.lower().find('sup') != -1 or message_in.lower().find(
                'hello') != -1 or message_in.lower().find('sup') != -1 or message_in.lower().find(
                'yo') != -1 or message_in.lower().find('hola') != -1 or message_in.lower().find(
                'ello') != -1 or message_in.lower().find('yes') != -1:
                await message.channel.send(f'**hello there how are you?**')

            elif message_in.lower().find('how are you') != -1:
                await message.channel.send(f'I can smell sus,btw how about you {message.author.display_name} ?')

            elif message_in.lower().find('ur mom') != -1:
                await message.channel.send(f'ur mom in my basement, {message.author.display_name}')

            elif message_in.lower().find('ur dad') != -1:
                await message.channel.send(f'shut up YOU, {message.author.display_name}')

            elif message_in.lower().find('fuck you') != -1:
                await message.channel.send(f'f you too, {message.author.display_name}')

            elif message_in.lower().find('what do you do for living') != -1:
                await message.channel.send(f'i eat bananas , {message.author.display_name}')

            else:
                await message.channel.send(f'{random.choice(a)}, **{message.author.display_name}**!')
        await self.process_commands(message)


token = os.environ['TOKEN']