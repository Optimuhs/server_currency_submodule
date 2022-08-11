from sqlite3 import Error

from db.db_connection import DbConnection


class DbServerCurrency(DbConnection):

    #           **************              CURRENCY TABLES             **********************

    def create_tables(self):
        #   CURRENCY

        coins_log = """CREATE TABLE IF NOT EXISTS coins_log
                                   (id INTEGER PRIMARY KEY,
                                   user_id VARCHAR(255) NOT NULL,
                                   timestamp VARCHAR(255) NOT NULL,
                                   event VARCHAR(255) NOT NULL,
                                   amount INTEGER NOT NULL,
                                   related_user_id INTEGER,
                                   extra VARCHAR(255) )
                                   """
        self.create_tables_q.append(coins_log)

        shop = """CREATE TABLE IF NOT EXISTS shop
                                    (guild_id INTEGER, 
                                    role_id INTEGER, 
                                    item_name TEXT, 
                                    description TEXT, 
                                    price INTEGER, 
                                    item_number INTEGER, 
                                    msg TEXT)
                                    """
        self.create_tables_q.append(shop)

        try:

            for t in self.create_tables_q:
                self.db.execute(t)
                print("CREATED CURRENCY TABLES")
        except Error as e:
            print(e)
            print("ERROR CREATING CURRENCY TABLES")

    #           **************              CURRENCY DB METHODS             **********************

    ### hourly command
    async def get_last_hourly(self, discord_user_id, discord_server_id):
        try:
            user_id = await self.get_user_id(discord_user_id, discord_server_id)
            event = "hourly"
            sql = """   SELECT  MAX(timestamp)
                        FROM    coins_log 
                        WHERE   user_id = ?
                        AND     event = ?"""
            params = (user_id, event)
            self.db.execute(sql, params)
            result = self.db.fetchall()
            if result[0][0] == None:
                result = 0
                return result
            ### todo: check/format result, return 0 for users without entry
            return float(result[0][0])
        except Error as e:
            print(e)
            print("error getting last hourly event")
            return 0

    async def add_hourly(self, discord_user_id, discord_server_id, amount):
        print("add_hourly")
        try:
            user_id = await self.get_user_id(discord_user_id, discord_server_id)
            timestamp = await self.get_current_timestamp()
            event = "hourly"
            sql = """   INSERT INTO coins_log 
                                    (user_id, timestamp, event, amount)
                             VALUES (?, ?, ? , ?)           """
            params = (user_id, timestamp, event, amount)
            print(params)
            self.db.execute(sql, params)
            return True
        except Error as e:
            print(e)
            print("error saving new hourly event")
            return False

    ### daily command
    async def get_last_daily(self, discord_user_id, discord_server_id):
        try:
            user_id = await self.get_user_id(discord_user_id, discord_server_id)
            event = "daily"
            sql = """   SELECT  MAX(timestamp)
                        FROM    coins_log 
                        WHERE   user_id = ?
                        AND     event = ?"""
            params = (user_id, event)
            self.db.execute(sql, params)
            result = self.db.fetchall()
            print("get_last_daily result")
            print(discord_user_id)
            print(discord_server_id)
            print(user_id)
            print(result)
            if result[0][0] == None:
                result = 0
                return result
            ### todo: check/format result, return 0 for users without entry
            return float(result[0][0])
        except Error as e:
            print(e)
            print("error getting last daily event")
            return 0

    async def get_daily_streak(self, discord_user_id, discord_server_id, timestamp):
        try:
            user_id = await self.get_user_id(discord_user_id, discord_server_id)
            event = "daily"

            sql = """   SELECT  MAX(extra)
                        FROM    coins_log 
                        WHERE   user_id = ?
                        AND     event = ?
                        AND     timestamp = ?"""
            params = (user_id, event, timestamp)
            self.db.execute(sql, params)
            result = self.db.fetchall()
            print("get_daily_streak result")
            print(discord_user_id)
            print(discord_server_id)
            print(user_id)
            print(result)
            if result[0][0] == None:
                result = 0
                return result
            ### todo: check/format result, return 0 for users without entry
            return float(result[0][0])
        except Error as e:
            print(e)
            print("error getting daily streak")
            return (0, 0)

    async def add_daily(self, discord_user_id, discord_server_id, amount, daily_streak):
        try:
            user_id = await self.get_user_id(discord_user_id, discord_server_id)
            timestamp = await self.get_current_timestamp()
            event = "daily"
            sql = """   INSERT INTO coins_log 
                                    (user_id, timestamp, event, amount, extra)
                             VALUES (?, ?, ? , ?, ?)           """
            params = (user_id, timestamp, event, amount, daily_streak)
            self.db.execute(sql, params)
            print("success saving new daily event")
            return True
        except Error as e:
            print(e)
            print("error setting daily event")
            return False

    ### coins command
    async def get_coins_total(self, discord_user_id, discord_server_id):
        try:
            user_id = await self.get_user_id(discord_user_id, discord_server_id)

            sql = """   SELECT  SUM(amount)
                        FROM    coins_log 
                        WHERE   user_id = ? """
            params = (user_id,)
            self.db.execute(sql, params)
            result = self.db.fetchall()
            print("get_coins_total result")

            print(result)
            if result[0][0] == None:
                result = 0
                return result
            ### todo: check/format result, return 0 for users without entry
            return float(result[0][0])
        except Error as e:
            print(e)
            print("error getting coins total")
            return (0, 0)

    ### coinflip command
    async def add_coinflip(self, discord_user_id, discord_server_id, amount, outcome):
        try:
            user_id = await self.get_user_id(discord_user_id, discord_server_id)
            timestamp = await self.get_current_timestamp()
            event = "coinflip" + "_" + outcome
            sql = """   INSERT INTO coins_log 
                                    (user_id, timestamp, event, amount)
                             VALUES (?, ?, ? , ?)           """
            params = (user_id, timestamp, event, amount)
            self.db.execute(sql, params)
            print("success saving new coinflip event")
            return True
        except Error as e:
            print(e)
            print("error setting coinflip event")
            return False

    ################################ SHOP ################################

    async def add_to_shop(self, discord_server_id, role_id, item_name, descirption, price, item_number, msg):
        try:

            sql = """   INSERT INTO shop 
                                    (guild_id, role_id, item_name, description, price, item_number, msg)
                             VALUES (?, ?, ?, ?, ?, ?, ?)           """
            params = (discord_server_id, role_id, item_name, descirption, price, item_number, msg)
            self.db.execute(sql, params)
            print("success saving shop item")
            return True
        except Error as e:
            print(e)
            print("error saving shop item")
            return False

    async def delete_from_shop(self, discord_server_id, item_number):
        try:

            sql = """   DELETE FROM shop 
                        WHERE  guild_id = ?
                        AND item_number = ?        """
            params = (discord_server_id, item_number)
            self.db.execute(sql, params)
            print("success deleting shop item " + str(item_number))
            return True
        except Error as e:
            print(e)
            print("error deleting shop item " + str(item_number))
            return False

    async def update_shop_item(self, discord_server_id, new_item_number, old_item_number):
        try:

            sql = """   UPDATE  shop 
                        SET     item_number = ?
                        WHERE   guild_id = ?
                        AND     item_number = ?       """
            params = (new_item_number, discord_server_id, old_item_number)
            self.db.execute(sql, params)
            print("success updating shop item " + str(new_item_number))
            return True
        except Error as e:
            print(e)
            print("error updating shop item " + str(old_item_number))
            return False

    async def remove_coins_for_purchase(self, discord_user_id, discord_server_id, price, item_name):
        try:
            user_id = await self.get_user_id(discord_user_id, discord_server_id)
            timestamp = await self.get_current_timestamp()
            event = "buy " + str(item_name)
            sql = """   INSERT INTO coins_log 
                                    (user_id, timestamp, event, amount)
                             VALUES (?, ?, ? , ?)           """
            params = (user_id, timestamp, event, -price)
            self.db.execute(sql, params)
            print("success saving new buy event")
            return True
        except Error as e:
            print(e)
            print("error setting buy event")
            return False

    async def get_shop_items(self, discord_server_id):
        try:
            sql = """    SELECT  *
                        FROM    shop
                        WHERE   guild_id = ?"""
            params = (discord_server_id,)
            self.db.execute(sql, params)
            result = self.db.fetchall()
            print("get_shop items")
            return result

        except Error as e:
            print(e)
            print("error getting daily streak")
            return ()

    async def add_shop_item(self, discord_server_id, role_id, item_name, description, price, item_number, msg):
        try:
            sql = """ INSERT INTO   shop
                                    (guild_id, 
                                    role_id, 
                                    item_name, 
                                    description, 
                                    price, 
                                    item_number, 
                                    msg) 
                        VALUES(?,?,?,?,?,?,?) """
            params = (discord_server_id, role_id, item_name, description, price, item_number, msg)
            self.db.execute(sql, params)
            self.db.commit()
            print("success saving new shop")
            return True
        except Error as e:
            print(e)
            print("error shop item")
            return False
