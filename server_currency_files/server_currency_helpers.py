import disnake
from disnake import TextInputStyle


class IrlForm(disnake.ui.Modal):
    irl_submitchannel_id = 983711625473314836

    def __init__(self, inter: disnake.ApplicationCommandInteraction):
        self.user = inter.user
        components = [
            disnake.ui.TextInput(
                label="Date",
                placeholder="day-month-year",
                custom_id="Trip Date",
                style=TextInputStyle.short,
                max_length=20,
            ),
            disnake.ui.TextInput(
                label="Location",
                placeholder="from lalaland to wonderwood",
                custom_id="Trip Location",
                style=TextInputStyle.short,
                max_length=1000,
            ),
            disnake.ui.TextInput(
                label="Description",
                placeholder="description of your trip",
                custom_id="Trip Description",
                style=TextInputStyle.paragraph,

            ),
            disnake.ui.TextInput(
                label="Distance",
                placeholder="666 km",
                custom_id="Trip Distance",
                style=TextInputStyle.short,
                max_length=20,
            ),
        ]
        super().__init__(
            title="Submit Your Roadtrip",
            custom_id="irl_form" + str(self.user.id),
            components=components,
        )

    # The callback received when the user input is completed.
    async def callback(self, inter: disnake.ModalInteraction):
        embed = disnake.Embed(title="Roadtrip Submitted by " + self.user.display_name)
        for key, value in inter.text_values.items():
            embed.add_field(
                name=key.capitalize(),
                value=value[:1024],
                inline=True,
            )
            embed.set_thumbnail(url=self.user.display_avatar.url)
        irl_submit_channel = inter.guild.get_channel(self.irl_submitchannel_id)
        message = await irl_submit_channel.send(embed=embed)

        thread = await message.create_thread(
            name=self.user.display_name + "thread for pictures and extra info",
            auto_archive_duration=60,
            # type=disnake.ChannelType.private_thread,
        )
        await thread.add_user(inter.user)
        await thread.send(
            self.user.display_name + ", you can post pictures or extra information to support your claim here")
        await inter.response.send_message(
            "Go to the newly created thread in the claim your IRL TRIP channel: " + thread.jump_url)
