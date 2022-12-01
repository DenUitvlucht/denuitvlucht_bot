# Den Uitvlucht Telegram Bot
Telegram Bot that can perform various 'bestuurstaken'
Scope is limited to 'brouwerstaken' and 'extra puntjes' for now.

## Motivation

Laziness

## Installation
### Install requirements

```bash
pip install -r requirements.txt
```
### Add environment variables

- Telegram Bot API Token (API_TOKEN)
- Telegram Chat ID (CHAT_ID)
- Allowed Users (BESTUUR_IDS)
- Sender (FROM)
- Receiver (TO)

## Usage
### BOT
```bash
python denuitvlucht_bot
```

### Place Order
```bash
python denuitvlucht_bot/data/place_order.py
```

### Notifiers
```bash
python denuitvlucht_bot/notifiers/order_notifier.py
```
```bash
python denuitvlucht_bot/notifiers/levering_notifier.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)