from .models import Categoria

def menu_links(request):
    links= Categoria.objects.all()
    return dict(links=links)