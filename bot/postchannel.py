import os
import logging
import bot.constants as con
from typing import Dict

from telegram import (
    Update,
    ParseMode,
    BotCommand,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    ConversationHandler,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def facts_to_str(user_data: Dict[str, str]):
    nombre = user_data['nombre']
    link = user_data['link']
    descripcion = user_data['descripcion']
    contenido = user_data['contenido']
    palabras = user_data['palabras']
    valoracion = user_data['valoracion']
    return (
        f'🏷🔖<b>{nombre}</b>\n🔗 <b>Link:</b> {link}\n♨️ <b>Descripción:</b> {descripcion}\n\n'
        f'\n📤 <b>Contenido a subir:</b> {contenido}\n🎞️ <b>Palabras extras del creador:</b> {palabras}\n'
        f'\n👍  <b>Valoración:</b> {valoracion}\n\n'
        '🔷🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔷\n🌐 <a href="https://t.me/Program_Plus_channel"><b>Program Plus Channel</b></a> 🌐'
    )


def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    if user_id in con.administradores:
        update.message.reply_text(
            text=f'Hola <a href="tg://user?id={user_id}">{first_name}</a>\nPulsa /comenzar para generar una plantilla.',
            parse_mode=ParseMode.HTML
            )
        context.bot.set_my_commands([
            BotCommand(command='comenzar', description='Generar una plantilla.'),
            BotCommand(command='cancelar', description='Detener el proceso actual.')
            ]
        )
    else:
        update.message.reply_text(
            text=f'<a href="tg://user?id={user_id}">{first_name}</a> no tienes acceso para usar este bot.',
            parse_mode=ParseMode.HTML
            )


def comenzar(update: Update, context: CallbackContext):
    if update.effective_user.id in con.administradores:
        update.message.reply_text(
            "Enviame la imagen del Canal.",
            )
        return con.PHOTO


def photo(update: Update, context: CallbackContext):
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('bot/photo/{}.jpg'.format(update.message.chat_id))
    update.message.reply_text(
        'Enviame el nombre del Canal.'
    )
    return con.NOMBRE


def nombre(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['nombre'] = text
    update.message.reply_text(
        f'Enviame el Link del canal.'
    )
    return con.LINK



def link(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['link'] = text
    update.message.reply_text(
        f'Enviame la descripcion del Canal.'
    )
    return con.DESCRIPCION


def descripcion(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['descripcion'] = text
    update.message.reply_text(
        f'Enviame el contenido que sube el canal #película #series #youtube #anime #mangas #doramas #shows #juegos #música #programas .'
    )
    return con.CONTENIDO_SUBIR


def contenido(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['contenido'] = text
    update.message.reply_text(
        f'Enviame el argumento del creador.'
    )
    return con.PALABRA_CREADOR


def palabras(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['palabras'] = text
    update.message.reply_text(
        f'Enviame la valoracíon 10/10.'
    )
    return con.VALORACION



def valoracion(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['valoracion'] = text

    update.message.reply_text(
        text=f"✅ Plantilla creada correctamente\n<b>Resultado:</b>\n\n{facts_to_str(context.user_data)}" +
            "\n\nPulsa el botón de debajo para enviar la plantilla. 📢",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup([['Enviar plantilla ✅']],
            one_time_keyboard=True,
            resize_keyboard=True
            )
        )
    return con.SEND


def done(update: Update, context: CallbackContext):
    user_data = context.user_data
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name


    context.bot.send_photo(
        chat_id=con.CHANNEL,
        photo=open(f'bot/photo/{update.message.chat_id}.jpg', 'rb'),
        caption=f'{facts_to_str(user_data)}'.format(user=user_id, name=first_name),
        parse_mode=ParseMode.HTML,
    )
    user_data.clear()
    return ConversationHandler.END


def stop(update: Update, context: CallbackContext):
    if update.effective_user.id in con.administradores:
        update.message.reply_text(
            text='Operación cancelada.',
            reply_markup=ReplyKeyboardRemove(selective=True)
        )
        return ConversationHandler.END

def main():
    token = os.getenv('TELEGRAM_TOKEN')
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('comenzar', comenzar)],
        states={
            con.PHOTO: [
                MessageHandler(Filters.photo, photo),
            ],
            con.NOMBRE: [
                MessageHandler(Filters.text, nombre)
            ],
            con.LINK: [
                MessageHandler(Filters.text, link)
            ],
            con.DESCRIPCION: [
                MessageHandler(Filters.text, descripcion)
            ],
            con.CONTENIDO_SUBIR: [
                MessageHandler(Filters.text, contenido)
            ],
            con.PALABRA_CREADOR: [
                MessageHandler(Filters.text, palabras)
            ],
            con.VALORACION: [
                MessageHandler(Filters.text, valoracion),
            ],
            con.SEND: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Enviar plantilla ✅$')), done),
            ],
        },
        fallbacks=[
            MessageHandler(Filters.regex('^Enviar plantilla ✅$'), done),
            CommandHandler('cancelar', stop),
            ],
        allow_reentry=True
    )
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
