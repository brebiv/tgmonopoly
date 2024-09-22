import telebot
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .handlers import bot

# Create your views here.
@csrf_exempt
def update(request):
    if request.method != 'POST':
        return HttpResponse("You will be reported for this action. 😡", status=405)

    update_json = request.body.decode()
    update = telebot.types.Update.de_json(update_json)
    bot.process_new_updates([update])
    return HttpResponse()
