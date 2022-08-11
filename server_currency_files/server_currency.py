import random
from datetime import datetime

import disnake
from disnake import *
from disnake.ext import commands
from disnake.ext.commands import group, MissingRequiredArgument, RoleConverter, BadArgument

import cogs.server_currency_files.servercurrencyconfig as sc
from cogs.server_currency_files.db_server_curency import DbServerCurrency
from cogs.server_currency_files.server_currency_helpers import IrlForm


class ServerCurrencyBot(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    ####################################################################################################################
    ######################################   HELP FUNCTIONS   ##########################################################
    ####################################################################################################################
    async def construct_message(self, type, params):

        if type == "hourly":
            hourly = sc.hourly_response_part1 + " " + str(
                params[0]) + " " + sc.coin_name_plural + " " + sc.hourly_response_part2
            return hourly
        elif type == "coinflip":
            coinflip = "you bet " + str(params[2]) + " and flip a coin ... you " + str(params[0]) + " " + str(
                params[1]) + " " + sc.coin_name_plural
            return coinflip
        elif type == "daily":
            earned = params[0]
            streak = params[1]
            bonus = params[2]
            print("daily message")
            print(streak)
            print(bonus)
            if streak > 0:
                daily = sc.daily_response_part1 + " " + str(
                    earned) + " " + sc.coin_name_plural + " " + sc.daily_response_part2 + " " + sc.daily_response_bonus1 + " " + str(
                    bonus) + " " + sc.coin_name_plural + " " + sc.daily_response_bonus2 + " " + str(streak)
            else:
                daily = sc.daily_response_part1 + " " + str(
                    earned) + " " + sc.coin_name_plural + " " + sc.daily_response_part2
            return daily
        elif type == "coins":
            coins = "you have a total of " + str(round(params[0])) + " " + sc.coin_name_plural
            return coins
        elif type == "error":
            error = "something went wrong when you tried to do the " + str(
                params[0]) + " command. please try again. Contact an admin if this problem persists"
            return error
        elif type == "wait":
            seconds = round(params[0])
            if seconds < 60:
                wait = "you have to wait " + str(seconds) + " seconds before you can do this command again"
            else:
                minutes = round(seconds / 60)
                wait = "you have to wait " + str(minutes) + " minutes before you can do this command again"
            return wait
        else:
            return "??? something went wrong"

    async def get_current_timestamp(self):
        return datetime.now().timestamp()

    async def get_random_amount(self, min, max):
        return int(min + (max - min) * random.random())

    async def get_coins_total(self, discord_user_id, discord_server_id):
        print("get_coins_total")
        db = DbServerCurrency()
        coins = await db.get_coins_total(discord_user_id, discord_server_id)
        print(coins)
        return coins

    async def get_coinflip_result(self, bet, choice):
        # 1,3, 5 = heads  2,4,6 = tails
        result = await self.get_random_amount(0, 2)
        print("coinflip")
        print(result)

        if result >= 1:
            result = sc.coinflip_tails_name
        elif result < 1:
            result = sc.coinflip_heads_name
        else:
            print("something went wrong flipping the coin")

        if result == choice:
            print("Win")
            outcome = "win"
            max = int(bet) * sc.coinflip_max_win_percentage / 100
            min = int(bet) * sc.coinflip_min_win_percentage / 100
            random = await self.get_random_amount(min, max)

        else:
            print("Loss")
            outcome = "lose"
            max = int(bet) * sc.coinflip_max_loss_percentage / 100
            min = int(bet) * sc.coinflip_min_loss_percentage / 100
            random = await self.get_random_amount(min, max)

        return [outcome, random]

    async def get_daily_bonus_amount(self, user_id, server_id, last_timestamp):
        now = await self.get_current_timestamp()
        print("check_daily_bonus")
        print(last_timestamp)
        print(now)

        if int(last_timestamp) == 0:
            print("first time, no bonus")
            # first time, no bonus
            streak = 0
            bonus = 0
        else:
            time_since_last = int(now) - int(last_timestamp)
            print("time since last daily")
            print(time_since_last)
            if time_since_last < (2 * sc.daily_timeframe):
                print("in time")
                # in time, check streak
                db = DbServerCurrency()
                streak = await db.get_daily_streak(user_id, server_id, last_timestamp)
                print(streak)

                if streak > sc.daily_consecutive_bonus_max_days:
                    # streak at max, restart
                    streak = 0
                    bonus = 0
                else:
                    # streak bonus earned
                    streak += 1
                    bonus = streak * sc.daily_consecutive_bonus_amount

            else:
                print("too late")
                # too late for daily streak bonus, restart
                bonus = 0
                streak = 0

        print(streak)
        print(bonus)
        return [round(streak), round(bonus)]

    async def check_hourly_wait(self, user_id, server_id):
        db = DbServerCurrency()
        last = await db.get_last_hourly(user_id, server_id)
        now = await self.get_current_timestamp()
        time_since_last = int(now) - int(last)
        if time_since_last > sc.hourly_timeframe:
            return 0
        else:
            return sc.hourly_timeframe - time_since_last

    async def check_daily_wait(self, user_id, server_id):
        db = DbServerCurrency()
        last = await db.get_last_daily(user_id, server_id)
        now = await self.get_current_timestamp()
        print("check_daily_wait")
        print(last)
        print(now)

        time_since_last = int(now) - int(last)
        if time_since_last > sc.daily_timeframe:
            return [0, last]
        else:
            return [sc.daily_timeframe - time_since_last, last]

    async def save_hourly_amount(self, user_id, server_id, amount):
        db = DbServerCurrency()
        await db.add_hourly(user_id, server_id, amount)
        db.conn.commit()
        db.conn.close()

    async def save_daily_amount(self, user_id, server_id, amount, streak):
        db = DbServerCurrency()
        await db.add_daily(user_id, server_id, amount, streak)
        db.conn.commit()
        db.conn.close()

    async def save_coinflip_amount(self, user_id, server_id, amount, outcome):
        if outcome == "lose":
            amount = amount * -1
        db = DbServerCurrency()
        await db.add_coinflip(user_id, server_id, amount, outcome)
        db.conn.commit()
        db.conn.close()

    ####################################################################################################################
    ######################################   SLASH COMMANDS   ##########################################################
    ####################################################################################################################
    @commands.slash_command(
        name=sc.hourly_command_name,
        description=sc.hourly_command_description
    )
    async def hourly(self, inter: disnake.ApplicationCommandInteraction):
        print('hourly')
        discord_user_id = inter.user.id
        discord_server_id = inter.guild_id

        #   check if user can already do hourly command
        wait_secs = await self.check_hourly_wait(discord_user_id, discord_server_id)
        print(wait_secs)
        if wait_secs == 0:
            try:
                earned_amount = await self.get_random_amount(sc.hourly_minimum_amount, sc.hourly_maximum_amount)
                await self.save_hourly_amount(discord_user_id, discord_server_id, earned_amount)
                await inter.response.send_message(await self.construct_message("hourly", [earned_amount]))
            except Exception as e:
                print(e)
                print("problem doing hourly")
                await inter.response.send_message(
                    await self.construct_message("hourly_error", [sc.hourly_command_name]))
        else:
            await inter.response.send_message(await self.construct_message("wait", [wait_secs]))

    @commands.slash_command(
        name=sc.daily_command_name,
        description=sc.daily_command_description
    )
    async def daily(self, inter: disnake.ApplicationCommandInteraction):
        discord_user_id = inter.user.id
        discord_server_id = inter.guild_id

        #   check if user can already do hourly command
        wait_result = await self.check_daily_wait(discord_user_id, discord_server_id)
        wait_secs = wait_result[0]
        last_timestamp = wait_result[1]

        print(wait_secs)
        if wait_secs == 0:
            try:
                earned_amount = await self.get_random_amount(sc.daily_minimum_amount, sc.daily_maximum_amount)
                bonus_result = await self.get_daily_bonus_amount(discord_user_id, discord_server_id, last_timestamp)
                earned_bonus = bonus_result[1]
                streak = bonus_result[0]
                earned_total = earned_bonus + earned_amount
                await self.save_daily_amount(discord_user_id, discord_server_id, earned_total, streak)
                await inter.response.send_message(
                    await self.construct_message("daily", [earned_amount, streak, earned_bonus]))
            except Exception as e:
                print(e)
                print("problem doing daily")
                await inter.response.send_message(
                    await self.construct_message("error", [sc.daily_command_name]))
        else:
            await inter.response.send_message(await self.construct_message("wait", [wait_secs]))

    @commands.slash_command(
        name=sc.coins_command_name,
        description=sc.coins_command_description
    )
    async def coins(self, inter: disnake.ApplicationCommandInteraction):
        discord_user_id = inter.user.id
        discord_server_id = inter.guild_id
        try:

            total = await self.get_coins_total(discord_user_id, discord_server_id)
            await inter.response.send_message(
                await self.construct_message("coins", [total]))
        except Exception as e:
            print(e)
            print("problem getting coins total")
            await inter.response.send_message(
                await self.construct_message("error", [sc.coins_command_name]))

    @commands.slash_command(
        name=sc.irl_command_name,
        description=sc.irl_command_description
    )
    async def irl_request(self, inter: disnake.ApplicationCommandInteraction):
        form = IrlForm(inter)
        await inter.response.send_modal(modal=form)

    @commands.slash_command(
        name=sc.coinflip_command_name,
        description=sc.coinflip_command_description
    )
    async def coin_flip(self, inter: disnake.ApplicationCommandInteraction,
                        bet: commands.Range[0, sc.coinflip_max_bet] = 500,
                        choice: str = commands.Param(choices=["heads", "tails"])):
        discord_user_id = inter.user.id
        discord_server_id = inter.guild_id
        try:
            # todo: check if enough coins to bet
            coinflip = await self.get_coinflip_result(bet, choice)
            outcome = coinflip[0]
            amount = coinflip[1]
            await self.save_coinflip_amount(discord_user_id, discord_server_id, amount, outcome)
            await inter.response.send_message(
                await self.construct_message("coinflip", [outcome, amount, bet]))
        except Exception as e:
            print(e)
            print("problem getting coins total")
            await inter.response.send_message(
                await self.construct_message("error", [sc.coins_command_name]))

    @commands.slash_command(
        name=sc.economy_settings_command_name,
        description=sc.economy_settings_command_description
    )
    async def economy_settings(self, inter: disnake.ApplicationCommandInteraction):
        settings = "-----------------------------------------------------------------" + "\n" + \
                   "------------  CURRENT ECONOMY SETTINGS  ------------" + "\n" + \
                   "-----------------------------------------------------------------" + "\n" + \
                   "          *** COIN NAME ***                      :        *** " + sc.coin_name_singular + "/" + sc.coin_name_plural + "*** \n" + \
                   "          *** DAILY WORK COMMAND ***             :        *** " + sc.daily_command_name + "*** \n" + \
                   "description   :   " + sc.daily_command_description + "\n" + \
                   "wait interval   :   " + str((sc.daily_timeframe) / 60) + " minutes" + "\n" + \
                   "amount   :   " + str(sc.daily_minimum_amount) + "/min - " + str(
            sc.daily_maximum_amount) + "/max" + "\n" + \
                   "bonus base amount   :   " + str(sc.daily_consecutive_bonus_amount) + "\n" + \
                   "bonus max days   :   " + str(sc.daily_consecutive_bonus_max_days) + "\n" + \
                   "          *** HOURLY WORK COMMAND ***            :        *** " + sc.hourly_command_name + "*** \n" + \
                   "description   :   " + sc.hourly_command_description + "\n" + \
                   "wait interval   :   " + str((sc.hourly_timeframe) / 60) + " minutes" + "\n" + \
                   "amount   :   " + str(sc.hourly_minimum_amount) + "/min - " + str(
            sc.hourly_maximum_amount) + "/max" + "*** \n" + \
                   "          *** COINS COMMAND ***                  :        *** " + sc.coins_command_name + "\n" + \
                   "description   :   " + sc.coins_command_description + "\n" + \
                   "          *** COINFLIP COMMAND ***               :         *** " + sc.coinflip_command_name + "*** \n" + \
                   "description   :   " + sc.coinflip_command_description + "\n" + \
                   "max bet amount   :   " + str(sc.coinflip_max_bet) + "\n" + \
                   "win   :   " + str(sc.coinflip_min_win_percentage) + "% of bet amount /min - " + str(
            sc.coinflip_max_win_percentage) + "% of bet amount /max" + "\n" + \
                   "lose   :    " + str(sc.coinflip_min_loss_percentage) + "% of bet amount /min - " + str(
            sc.coinflip_max_loss_percentage) + "% of bet amount /max" + "\n" + \
                   "          *** ECONOMY SETTINGS COMMAND ***       :        *** " + sc.economy_settings_command_name + "*** \n" + \
                   " description   :   " + sc.economy_settings_command_description + "\n"

        await inter.response.send_message(settings)

    ###########################    SHOP    ############
    @group(invoke_without_command=True, case_insensitive=True)
    async def shop(self, inter):
        db = DbServerCurrency()
        items = await db.get_shop_items(inter.guild.id)
        if len(items) == 0:
            return await inter.send(embed=self.ErrorEmbed('Error', 'There are no items in shop yet.'))
        else:
            embed = Embed(title=f"{sc.coin_name_singular} MarketPlace :shopping_cart:", color=Color.gold(),
                          description="Buy any item using `.shop buy <item-name/item-number>`. Example: `.shop buy 1`")
        try:
            embed.set_thumbnail(url=inter.guild.icon.url)
        except:
            pass
        embeds = [embed]
        current_embed = 0
        vals = 1
        for i, data in enumerate(items):
            try:
                if data[1] != 123:
                    role = f"\n**Obtainable Role: {inter.guild.get_role(data[1]).mention}**"
                else:
                    raise ()
            except:
                role = ""
            if vals <= 5:
                embeds[current_embed].add_field(name=f"{i + 1}     {data[2]}",
                                                value=f'> {data[3]}\n**Price: {data[4]} :coin:**' + role, inline=False)
                vals += 1
            else:
                e = Embed(color=Color.gold())
                try:
                    e.set_thumbnail(url=inter.guild.icon.url)
                except:
                    pass
                e.add_field(name=data[2], value=data[3] + f'\n**Price: {data[4]} :coin:**' + role, inline=False)
                embeds.append(e)
                current_embed += 1
                vals = 1

        await inter.send(embed=embeds[0])

    async def ShopAdd(self, inter, item, price, description, role, command):
        db = DbServerCurrency()
        if not inter.author.guild_permissions.administrator:
            return await inter.send(embed=self.ErrorEmbed('Error', 'You are not allowed to use this command.'))
        if command == 'prefix':
            await inter.send("Now input a description for the item.")
            msg = await self.bot.wait_for('message', check=lambda
                m: m.author.id == inter.author.id and m.channel.id == inter.channel.id, timeout=60.0)
            description = msg.content
            await inter.send(
                "Now input the name or id of the role you want to give. You can also mention the role. Type `None` to skip (`None` is case sensitive).")
            msg = await self.bot.wait_for('message', check=lambda
                m: m.author.id == inter.author.id and m.channel.id == inter.channel.id, timeout=60.0)
            if msg.content != "None":
                try:
                    role = await RoleConverter().convert(inter, msg.content)
                    if role != None:
                        role = role.id
                    else:
                        raise ()
                except:
                    return await inter.send(embed=self.ErrorEmbed('Error', 'Role not found.'))
                msg = "None"
            else:
                role = 123
                await inter.send('Now input the message you want to DM the user on purchasing this item.')
                msg = await self.bot.wait_for('message', check=lambda
                    m: m.author.id == inter.author.id and m.channel.id == inter.channel.id, timeout=180.0)
                msg = msg.content
        items = await db.db.get_shop_items(inter.guild.id)
        for data in items:
            if data[2].lower() == item.lower():
                return await inter.send(embed=self.ErrorEmbed('Error',
                                                              f'There is already a item named {item}. Input a different name next time.'))
        await db.add_shop_item(inter.guild.id, role, item, description, price, len(items) + 1, msg)
        await inter.send(embed=self.SuccessEmbed('Item Added!', f'{item} was added in the shop successfully.'))

    @shop.command()
    async def add(self, inter, price: int, *, item):
        await self.ShopAdd(inter, item, price, "", 123, 'prefix')

    @add.error
    async def add_error(self, inter, error):
        if isinstance(error, (BadArgument, MissingRequiredArgument)):
            await inter.send(embed=self.ErrorEmbed('Syntax Error',
                                                   f'Correct syntax is: `.shop add <price> <item-name>`. Example: `.shop add 20 Sneaker Role`.'))

    @shop.command()
    async def remove(self, inter):
        db = DbServerCurrency()
        if not inter.author.guild_permissions.administrator:
            return await inter.send(embed=self.ErrorEmbed('Error', 'You are not allowed to use this command.'))
        datas = await db.DataFetch(self.bot, 'all', 'shop', inter.guild.id)
        if len(datas) == 0:
            return await inter.send(embed=self.ErrorEmbed('Error', 'There are no items in shop yet.'))
        items = [x[2] for x in datas]
        embed = Embed(title="Available Items", description='\n'.join([f"{i + 1}. {x}" for i, x in enumerate(items)]))
        await inter.send(content="Input the serial number of the item you wish to remove.", embed=embed)
        msg = await self.bot.wait_for('message',
                                      check=lambda
                                          m: m.channel.id == inter.channel.id and m.author.id == inter.author.id,
                                      timeout=120.0)
        try:
            await db.DataUpdate(self.bot,
                                f"DELETE FROM shop WHERE guild_id = {inter.guild.id} and item_number = {msg.content}")
            for i, data in enumerate(datas):
                await db.DataUpdate(self.bot,
                                    f"UPDATE shop SET item_number = ? WHERE guild_id = {inter.guild.id} and item_number = {data[5]}",
                                    i + 1)
            await inter.send(embed=self.SuccessEmbed('Item Removed!', f'Item removed successfully.'))
        except:
            await inter.send(
                embed=self.ErrorEmbed('Error', 'Could not remove the item. Make sure the serial number is correct.'))

    async def BuyItem(self, inter, data, points):
        db = DbServerCurrency()
        remaining_points = points - data[4]
        if remaining_points < 0:
            return await inter.reply(f"You do not have enough {sc.coin_name_plural} :coin: to purchase this item.")
        else:
            pass
            if data[1] != 123:
                await self.bot.wait_until_ready()
                role = inter.guild.get_role(data[1])
                try:
                    if role != None:
                        rolegained = role.mention
                        if role in inter.author.roles:
                            return await inter.send(
                                embed=self.ErrorEmbed('Item already purchased!', 'You already have this item.'))
                        await inter.author.add_roles(role)
                    else:
                        raise ()
                except:
                    rolegained = f"I was unable to give the role."
                    await inter.reply("I could not give you the role. Please contact staff.")
            else:
                rolegained = "None"
                await inter.author.send(data[6])
            log_channel = self.bot.get_channel(self.LOG_CHANNEL)
            await db.DataUpdate(self.bot,
                                f"UPDATE points SET points = ? WHERE guild_id = {inter.guild.id} and user_id = {inter.author.id}",
                                remaining_points)
            msg = await inter.reply(embed=self.SuccessEmbed('Item bought!', f'You have bought {data[2]} successfully!'))
            e = Embed(title="New Purchase",
                      description=f"**Item Bought:** {data[2]}\n**Price:** {data[4]} :coin:\n**Role Gained**: {rolegained}",
                      color=Color.green(), timestamp=msg.created_at)
            try:
                e.set_author(icon_url=inter.author.avatar.url, name=f"{inter.author} (Click Here)", url=msg.jump_url)
            except:
                e.set_author(name=f"{inter.author} (Click Here)", url=msg.jump_url)
            await log_channel.send(embed=e)

    @shop.command()
    async def buy(self, inter, *, item):
        db = DbServerCurrency()
        try:
            item = int(item)
            Type = 'num'
        except:
            Type = 'str'
        datas = await db.DataFetch(self.bot, 'all', 'shop', inter.guild.id)
        points = await db.DataFetch(self.bot, 'one', 'points', inter.guild.id, inter.author.id)
        if points:
            points = points[2]
        else:
            points = 0
        length = 0
        for data in datas:
            if Type == 'str':
                if item.lower() == data[2].lower():
                    await self.BuyItem(inter, data, points)
                else:
                    length += 1
            else:
                if item == data[5]:
                    await self.BuyItem(inter, data, points)
                else:
                    length += 1
        if length == len(datas):
            return await inter.send(
                embed=await self.ErrorEmbed('Item not found.', 'I could not find any item with that name or number.'))

    @buy.error
    async def buy_error(self, inter, error):
        if isinstance(error, (MissingRequiredArgument)):
            await inter.send(embed=await self.ErrorEmbed('Syntax Error',
                                                         f'Correct syntax is: `.shop buy <item-name/item-number>`. Example: `.shop buy Sneaker Role` or `.shop buy 1`.'))

    async def SuccessEmbed(self, title, description):
        return Embed(title=":ballot_box_with_check: " + title, description=description, color=Color.green())

    async def ErrorEmbed(self, title, description):
        return Embed(title=":x: " + title, description=description, color=Color.from_rgb(255, 0, 0))

    ####################################################################################################################
    ######################################   USER  COMMANDS   ##########################################################
    ####################################################################################################################

    @commands.user_command(
        name=sc.inventory_command_name,
        description=sc.inventory_command_description
    )
    async def user_inventory(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        discord_user_id = user.id
        discord_server_id = inter.guild_id

        try:
            total = await self.get_coins_total(discord_user_id, discord_server_id)
            titel = f"{user.display_name}'s inventory"
            description = "current " + sc.coin_name_plural + " amount = " + str(round(total))
            emb = disnake.Embed(title=titel, description=description, color=disnake.Colour.orange())
            emb.set_thumbnail(url=user.display_avatar.url)
            await inter.send(embed=emb)
        except Exception as e:
            print(e)
            print("problem getting inventory")
            await inter.response.send_message(
                await self.construct_message("error", [sc.inventory_command_name]))


def setup(bot: commands.Bot):
    #   MAKE SURE DB TABLES ARE CREATED
    try:
        db = DbServerCurrency()
        db.create_tables()
    except Exception as e:
        print(e)

    bot.add_cog(ServerCurrencyBot(bot))
