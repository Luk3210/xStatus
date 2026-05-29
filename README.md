# xStatus

![GitHub License](https://img.shields.io/github/license/Luk3210/xStatus?style=for-the-badge&labelColor=gray&color=blue)

xStatus is an application that will notify you if one of your controllers goes offline while your show is running.

You must join [the Discord server](https://discord.gg/KVKhZHZ2Aa) in order to be notified by the bot.

Microsoft Defender SmartScreen blocks this. I am currently working on signing it and becoming a verified publisher. If you don't trust me, you can use an external decompiler to see for yourself.

[Decoration icons created by Marz Gallery - Flaticon](https://www.flaticon.com/free-icon/light_14745209?term=christmas&page=1&position=61&origin=search&related_id=14745209 "decoration icons")

Not associated with the xLights organization.

# Setup instructions: 
**(It is not difficult, I just wrote very detailed instructions)**
- You must first ensure that you have a [Discord account](https://discord.com) and have the app installed on your phone with notifications on.
- Once you have done this, you must join [the Discord server](https://discord.gg/KVKhZHZ2Aa). This is because Discord requires you to have a mutual server with a bot in order for it to message you. You will not be directly notified from this server.
- From here, obtain the local ip address of the computer that will be running xSchedule.
- You will also need the xSchedule api port, you can find this by opening xSchedule and opening options. The connection to xSchedule is important because it grants xStatus the neccessary information about your controllers in order to ping them.
- Once you have this, open your xStatus application's web interface. It will tell you the local ip and port to access it when it starts up.
- Now, arrange your xStatus API URL in the format "http://"ipAddress":"port"/xScheduleQuery?Query=GetPlayingStatus" and input it into the config in the field titled "xSchedule API URL"
- Now you can select your notification method. Currently, only discord is supported.
- Imput you discord username into the correct field. This is different from your "display name" and can be found underneath your display name when you view your profile. ([See example](https://github.com/Luk3210/TurboLib/blob/e0f37bd6de8f360a5d79037d02777f5f0897282a/discord_username.jpg))
- Now select the start and stop time. This tells xStatus when your show is supposed to be running so that it doesn't alert you when your show turns off for the night.
- All you have to do now is press the save button at the bottom, wait a few seconds, and close and re-open your xStatus application.
