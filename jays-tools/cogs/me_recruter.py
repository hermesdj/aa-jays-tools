# Cog Stuff
import logging

import discord
# AA-Discordbot
from discord.embeds import Embed
from discord.ext import commands
# AA Contexts
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .. import app_settings

logger = logging.getLogger(__name__)


class MeRecruter(commands.Cog):
    """
    Thread Tools for recruiting!
    """

    def __init__(self, bot):
        self.bot = bot

    async def open_ticket(
            self,
            ctx: discord.Interaction,
            member: discord.Member
    ):
        sup_channel = settings.RECRUIT_CHANNEL_ID
        ch = ctx.guild.get_channel(sup_channel)
        th = await ch.create_thread(
            name=f"{member.display_name} | {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            auto_archive_duration=10080,
            type=discord.ChannelType.private_thread,
            reason=None
        )
        msg = (f"<@{member.id}> recherche un recruteur !\n\n"
               f"Quelqu'un du groupe <@&{settings.RECRUITER_GROUP_ID}> te contactera rapidement !")
        embd = Embed(
            title="Guide des Fils de Recrutement",
            description="Pour ajouter une personne à ce fil vous pouvez simplement les '@ping'. Cela fonctionne avec les `@groupes` aussi pour ajouter plusieurs personnes d'un seul coup. Utilisez ça avec sagesse, aucun abus ne sera toléré.\n\nCeci est une fonction en béta, si vous rencontrez des ennuis veuillez contacter l'admin. :heart:"
        )

        await th.send(msg, embed=embd)
        await ctx.response.send_message(content=_("Fil de recrutement créé !"), view=None, ephemeral=True)

    @commands.slash_command(
        name='me_recruter',
        guild_ids=app_settings.get_all_servers()
    )
    async def slash_halp(
            self,
            ctx,
    ):
        """
            Get hold of a recruiter
        """
        await self.open_ticket(ctx, ctx.user)

    @commands.message_command(
        name="Créer un fil de recrutement",
        guild_ids=app_settings.get_all_servers()
    )
    async def reverse_recruit_msg_context(
            self,
            ctx,
            message
    ):
        """
            Help a new guy get recruiter
        """
        await self.open_ticket(ctx, message.author)

    @commands.user_command(
        name="Me Recruter",
        guild_ids=app_settings.get_all_servers()
    )
    async def reverse_recruit_user_context(
            self, ctx, user
    ):
        """
            Help a new guy get recruiter
        """
        await self.open_ticket(ctx, user)


def setup(bot):
    bot.add_cog(MeRecruter(bot))
