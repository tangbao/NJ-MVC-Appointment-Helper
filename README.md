# NJ MVC Appointment Helper

An UNOFFICIAL Telegram bot that helps you find the most recent available appointment place for you.

If it could help you, please give me a star. Appreciated.

Update 2022 Oct 25: It seems that everything is on the way back to normal (hopefully). I do not know why you cannot find
this project repo page in Google search results, which is annoying because it prevents people from getting access to this 
project. Does anyone have idea about it?

Stay safe. Stay health.

## Recent Updates

**Please always update to the newest version before reporting any bugs.**

To receive updates in real time, you can subscribe to Telegram channel [@njmvc_bot_notif](https://t.me/njmvc_bot_notif).

Update 2022 Oct 25: I am updating the python-telegram-bot to v20.x, which is not compatible with the old version. For 
the last version of the bot using PTB v13.x, please visit 
https://github.com/tangbao/NJ-MVC-Appointment-Helper/releases/tag/v0.1.

## Demo

[@njmvc_bot](https://t.me/njmvc_bot)

Note that you can only use `/check` function of this demo bot. Only authorized users can use `/subscribe`. I do not make
it fully public because I cannot afford too much cloud resources.

You are welcome to contact me to be an authorized user, but there is no warranty to use this bot.

### **Privacy Disclaimer**

The logger of the bot may record your Telegram username and all the messages you send to the bot. Your Telegram user 
id will be used to verify if you are an authorized user or not. All the data collected by the bot will only be used for 
debug and will not be used for any analytics or shared/sold to a third party.

If you do not agree with this privacy policy, please do not use the bot, and consider 
[building your own bot](#build-your-own).

Privacy disclaimer updated 2021 Jul 28.

## Usage

`/check` Check the most recent available places for appointment.

`/subscribe` Receive a notification when a more recent time slot is available. Authorized users only. 
You can have at most three subscriptions.

`/mysub` Manage your subscriptions.

`/help` Show the help message.

`/updateconfig` Update the config so that you do not need to restart the bot. Admin user only.

## Examples

`/check`

![/check Part 1](/media/check1.png)

![/check Part 2](/media/check2.png)

`/subscribe`

![/subscription Part 1](/media/sub1.png)

![/subscription Part 2](/media/sub2.png)

An example of a running subscription

![/subscription Running](/media/active_sub.png)

`/mysub`

![/mysub](/media/mysub.png)

## Build Your Own

> Use at your own risk. There is NO WARRANTY.

### Preparations

- Apply for a Telegram bot from [@BotFather](https://t.me/botfather). 
  See [official instructions](https://core.telegram.org/bots/#6-botfather). 
  Remember to get the API token.
- Get your (or other authorized users') user id from [@userinfobot](https://t.me/userinfobot).

### Configuration & Deployment

**This part is out-of-date.**

> In the current version, the bot is not persistent. It means that everything will lose after you restart the bot. You 
> have to create the subscriptions again.

- `git clone https://github.com/tangbao/NJ-MVC-Appointment-Helper.git`
- [Optional but recommended] Create and activate your virtual env, like Anaconda.
- `pip install -r requirements.txt`
- Check `config.yaml` if you want some customized settings, like the maximum number of subscriptions a user can create.
- Make a copy of `config.secret.yaml.example`, name it as `config.secret.yaml`, follow the comments inside 
  to finish the config.
- Run `bot.py` and start using!

### Resources

The bot is using [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot), please refer to its 
documentation for more detailed information about docs, deployment, and so on.

## Development Plan (NO GUARANTEE)
- Make the location list be updated automatically.
- Make the bot persistent - subscription still exists after the bot restarts.
- Automatically submit an appointment (I guess I will never do this).

## Questions, Bugs, and Contributions

You can open an issue or email me (i AT tbis DOT me) directly. You can also contact me 
[@kirov_dev](https://t.me/kirov_dev) at Telegram. PR is welcome.

## License

The project is published under the [GNU General Public License - v3.0](https://www.gnu.org/licenses/gpl-3.0.html).
