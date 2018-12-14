#!/usr/bin/python3.6
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from app import Bancos
import config

TOKEN = config.TOKENS["TELEGRAM_API"]

GOOGLE_MAP_API_KEY = config.TOKENS["GOOGLE_MAPS_API"]


def start(bot, update, user_data):
    """Despliega el boton para pedir la ubicacion del usuario"""

    mensaje ="Buen día {}, para poder continuar, necesito que me compartas tu ubicacion.".format(update.message.from_user.first_name)

    location_keyboard = KeyboardButton(text="Enviar Ubicacion", request_location=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    bot.send_message(chat_id=update.message.chat_id, text=mensaje, reply_markup = reply_markup)


def cajeros(bot, update, user_data):
    """Busca los 3 cajeros mas cercanos al usuario y despliega un mensaje y un mapa con los mismos"""
    if not "coordenadas" in user_data:
        bot.send_message(chat_id=update.message.chat_id, text="Lo siento, primero necesito conocer tu ubicacion (usá /start)")

    user_data["firma"] = (update.message.text).replace("/","").upper()
    cajeros = Bancos.buscarCajeros(user_data)

    if len(cajeros) == 0:
        mensaje = "No hay cajeros cercanos"
        map = ""
    else:
        mensaje = "Tenes cerca los siguientes cajeros {}:\n".format(user_data["firma"])
        marker_cajeros = ""
        for cajero in cajeros:
            mensaje += "{} en {}\n".format(cajero.nombre(), cajero.ubicacion())
            marker_cajeros += "%7C{},{}".format(cajero.coords()[1], cajero.coords()[0])

        map = """https://maps.googleapis.com/maps/api/staticmap?zoom=15&size=600x400&maptype=roadmap
                &markers=color:blue%7Clabel:C{2}&markers=color:red%7Clabel:T%7C{0},{1}&key={3}""".format(
                user_data["coordenadas"][1], user_data["coordenadas"][0], marker_cajeros, GOOGLE_MAP_API_KEY)

    bot.send_message(chat_id=update.message.chat_id, text=mensaje)
    bot.send_photo(chat_id=update.message.chat_id, photo=map)


def obtener_ubicacion(bot, update, user_data):
    """Recibe la ubicacion del usuario y la guarda en 'user_data'"""

    user_data["coordenadas"] = (float(update.message.location.longitude), float(update.message.location.latitude))

    mensaje ="""
Muy bien, ahora usá uno de los siguientes comandos:
-------------------------------------------------------
/link: Lista cajeros de la firma ‘Link’ 
/banelco: Lista cajeros de la firma ‘Banelco’
-------------------------------------------------------"""

    bot.send_message(chat_id=update.message.chat_id, text=mensaje, reply_markup=ReplyKeyboardRemove())


def main():

    updater = Updater(token=TOKEN)

    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start, pass_user_data=True)
    link_handler = CommandHandler(['link','banelco'], cajeros, pass_user_data=True)
    location_handler = MessageHandler(Filters.location, obtener_ubicacion, pass_user_data=True)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(link_handler)
    dispatcher.add_handler(location_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

