# handlers/admin/broadcast.py
# ...
BROADCAST_MESSAGE = 0

async def broadcast_start(update, context):
    # ...
    return BROADCAST_MESSAGE

async def broadcast_receive(update, context):
    # Пайдаланушылар тізімін ДБ-дан алып, циклмен хабар жіберу логикасы
    # Telegram лимиттерін ескеру керек (try-except, time.sleep)
    return ConversationHandler.END

broadcast_conv = ConversationHandler(...)
