from django.utils import translation

class ForceRussianMiddleware:
    """
    Temporarily forces Russian for all requests.
    Only for testing translations.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        translation.activate('ru')  # force Russian
        response = self.get_response(request)
        translation.deactivate()
        return response