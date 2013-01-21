from giotto.middleware import GiottoOutputMiddleware

class AppendMessages(GiottoOutputMiddleware):
    def html(self, request, response):
        from .models import Message
        user = getattr(request, 'user', None)
        if not user:
            return response
        engine, template, context = response.data
        context['messages'] = Message.get(user=user)
        response.body = (engine, template, context)
        return response