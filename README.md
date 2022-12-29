# Den Uitvlucht Telegram Bot
Telegram Bot that can perform various 'bestuurstaken'.


- Automatic brewery order system.
    - Bot sends notifications in chat for order placement and delivery.
    - View a snapshot of 'het drankkot' to check the inventory
- Add additional points to a list.
- Check your cleaning shift.
- Payconiq integration.
    - Check daily, weekly, monthly and yearly totals.
    - Request QR-code.
- Sends weekly polls to bar staff.
- Request general information.
    - E-mail, website, enterprise number and bank account number.
    - Colruyt card

![IMG_20221215_164309](https://user-images.githubusercontent.com/104348706/209989834-90de9993-55c7-44d1-8c3a-4a9282ae7493.png)



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
- PAYCONIQ_EMAIL: Your Payconiq e-mail address.
- PAYCONIQ_PASSWORD: Your Payconiq password.

### Add order Excel sheet
- Download the Excel sheet from [here](https://docs.google.com/spreadsheets/d/1AHRiLHvcQdF1H9SWYESQEUXlUnzsZPkk/edit?usp=share_link&ouid=102649168948120392447&rtpof=true&sd=true).
- Add the file to **denuitvlucht_bot/data/**.

### Add client secret
- Generate an OAuth 2.0 Client ID file from Google Cloud Platform.
    - Change the publishing status of your OAuth app to 'In Production'
    - Download the OAuth credentials
    - Rename the file to **credentials.json** and make sure it's present in the root directory of this project.


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
0 20 * * 4 python denuitvlucht_bot/data/place_order.py
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