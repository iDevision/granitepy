# TODO:
#  - Listen to VC state updates for player state 
from discord.ext import commands


class Client:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def create_node(self, url: str, password: str, identifer: str):
        ...
