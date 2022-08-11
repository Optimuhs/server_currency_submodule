####################################################################################################################
######################     PARAMETERS FOR SERVER CURRENCY EXTENSION    ############################################
####################################################################################################################


coin_name_singular = "Killamile"
coin_name_plural = "Killamilez"

hourly_command_name = "ride"
hourly_command_description = "earn " + coin_name_plural + " by riding around the server"
hourly_timeframe = 1 * 60
hourly_minimum_amount = 100
hourly_maximum_amount = 200
hourly_response_part1 = "Congrats, You rode"
hourly_response_part2 = "before you ran out of gazzz!"

daily_command_name = "tour"
daily_command_description = "earn " + coin_name_plural + " by touring around the server"
daily_timeframe = 2 * 60
daily_minimum_amount = 200
daily_maximum_amount = 400
daily_consecutive_bonus_amount = 100
daily_consecutive_bonus_max_days = 5
daily_response_part1 = "Congrats, You toured"
daily_response_part2 = "before you ran out of gazzz!"
daily_response_bonus1 = "double the fun ! you earned a bonus on top of that:"
daily_response_bonus2 = "for a streak of "

coins_command_name = "earnings"
coins_command_description = "check how many " + coin_name_plural + " you have earned"

coinflip_command_name = "flip"
coinflip_command_description = "flip a coin to win or lose some coins "
coinflip_heads_name = "heads"
coinflip_tails_name = "tails"
coinflip_max_loss_percentage = 100
coinflip_max_win_percentage = 90
coinflip_min_loss_percentage = 50
coinflip_min_win_percentage = 10
coinflip_max_bet = 1000

economy_settings_command_name = "settings"
economy_settings_command_description = "view the custom settings for the economy"

inventory_command_name = "inventory"
inventory_command_description = "view the coins and items in a user's inventory"

irl_command_name = "IRL"
irl_command_description = "submit proof of your irl bike tours to get extra " + str(coin_name_plural)
irl_submitchannel_id = 983711625473314836
