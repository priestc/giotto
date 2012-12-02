from giotto.programs import GiottoProgram
from giotto.utils import get_config
from giotto.views import GiottoView

class FileView(GiottoView):
    def text_html(self, result):
        return result

def StaticServe(base_path):
    def get_file(path):
        base_path = get_config('base_path', '')
        f = open(base_path + path, 'r')
        return f

    class StaticServeInternal(GiottoProgram):
        name = 'static'
        controllers = ('http-get', )
        model = [get_file]
        view = FileView

    return StaticServeInternal