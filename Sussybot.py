import logging

from bot import SussyBot
import os
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp

client = SussyBot()

@client.command()
async def pre(ctx):
    prefixes = await client.db.fetchval(
        """
        SELECT prefixes
        FROM guilds.prefixes
        WHERE guild_id = $1
        """,
        ctx.guild.id
    )
    await ctx.send(prefixes)
@client.command()
async def setpre(ctx,prefix:list):
    await client.db.execute(
        """
        UPDATE guilds.prefixes 
        SET prefixes = $2
        WHERE guild_id = $1
        """,
        ctx.guild.id, prefix
    )
    await ctx.send("done")
@client.command()
async def delpre(ctx):
    await client.db.execute(
        """
        DELETE FROM guilds.prefixes 
        WHERE guild_id = $1
        """,
        ctx.guild.id
    )
    prefixes = await client.db.fetchval(
        """
        SELECT prefixes
        FROM guilds.prefixes
        WHERE guild_id = $1
        """,
        ctx.guild.id
    )
    logging.warning(prefixes)
    if prefixes is None:
        await ctx.send("hello")
    elif prefixes != None:
        await ctx.send("yes")







async def main():
    """Launches the bot."""
    async with client:
        try:
            await client.start()

        finally:
            await client.shutdown_tasks()
            await client.close()


if __name__ == "__main__":

    asyncio.run(main())