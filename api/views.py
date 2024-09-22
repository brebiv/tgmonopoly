from django.http import HttpRequest, HttpResponse, JsonResponse

from .serializers import CreateGameSerializer
from .utils import telegram_auth_required


# Create your views here.
@telegram_auth_required
def me(request: HttpRequest):
    me = {
        'id': request.telegram_user.user_id,
        'username': request.telegram_user.username,
        'first_name': request.telegram_user.first_name,
        'last_name': request.telegram_user.last_name,
        'language': request.telegram_user.language,
    }
    return JsonResponse(me)


@telegram_auth_required
def create_game(request: HttpRequest):
    if request.method == 'POST':
        serializer = CreateGameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=405)
