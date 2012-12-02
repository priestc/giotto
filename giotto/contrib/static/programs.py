from giotto.programs import GiottoProgram
from giotto.utils import get_config
from giotto.views import GiottoView

def get_file(path):
    base_path = get_config('base_path', '')
    f = open(base_path + path, 'r')
    return f

class FileView(GiottoView):
    def text_html(self, result):
        return result

class StaticServe(GiottoProgram):
    name = 'static'
    controllers = ('http-get', )
    model = [get_file]
    view = FileView