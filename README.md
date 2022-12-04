# Den Uitvlucht Telegram Bot
Telegram Bot that can perform various 'bestuurstaken'.


- Automatic brewery order system.
    - Bot sends notifications in chat for order placement and delivery.
- Add additional points to a list.
- Check your cleaning shift.
- Sends weekly polls to bar staff.

![bot_main](https://user-images.githubusercontent.com/104348706/205510493-404b9fa4-97a4-4534-afa2-c368948bcb1c.png)



## Motivation

Laziness.

## Installation
### Install requirements

```bash
pip install -r requirements.txt
```

### Create your bot

Create a bot using the [BotFather](https://t.me/BotFather). It's pretty straight forward.
Write down your API token.

### Collect your chat IDs
- Add [IDBot](https://t.me/myidbot) to your group chat and collect the chat ID.
- Collect the IDs of the users that are allowed to interact with the bot.


### Add environment variables

- API_TOKEN: Your Telegram bot API token.
- CHAT_ID: The group chat ID, collected using IDBot.
- BESTUUR_IDS: List of allowed users, seperated by ','.
- FROM: E-mail address of the sender (denuitvlucht@gmail.com in our case ).
- TO: E-mail address of the receiver (bestelling@omer.be in our case).
- BARBEZETTING_CHAT_ID: Chat ID of the bar staff group, collected using IDBot.

### Add order Excel sheet
- Download the Excel sheet from [here](https://docs.google.com/spreadsheets/d/1AHRiLHvcQdF1H9SWYESQEUXlUnzsZPkk/edit?usp=share_link&ouid=102649168948120392447&rtpof=true&sd=true).
- Add the file to **denuitvlucht_bot/data/**.

### Create output folder
- Create a new folder called 'output' in **denuitvlucht_bot/**.

### Add client secret
- Generate an OAuth 2.0 Client ID file from Google Cloud Platform. More information can be found [here](https://github.com/jeremyephron/simplegmail).
    - Rename the file to **client_secret.json**.



### Start the bot
```bash
python denuitvlucht_bot/
```

### Set Cronjobs for all notifiers
```bash
10 20 * * 4 python denuitvlucht_bot/notifiers/order_notifier.py
```
```bash
0 18 * * 2 python denuitvlucht_bot/notifiers/levering_notifier.py
```
```bash
0 12 * * 1 python denuitvlucht_bot/notifiers/shift_notifier.py
```

### Set Cronjob for order placement
```bash
0 19 * * 4 python denuitvlucht_bot/data/place_order.py
```

## Usage

### Commands
- **/denuitvlucht**: summons the bot.

- **/add something**: adds an additional point to the list.

- **/list**: retrieve list with additional points.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)