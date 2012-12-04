from cStringIO import StringIO
from giotto.programs import GiottoProgram
from giotto.utils import get_config
from giotto.views import GiottoView

class FileView(GiottoView):
    def text_html(self, result):
        return result

    def text_cmd(self, result):
        return result.read()

def StaticServe(base_path, cache=None):
    """
    Meta program for serving any file based on the path
    """
    cache_ = cache # to avoid a NameError because the attribute is the same name
    def get_file(path):
        return open(base_path + path, 'r')

    class StaticServeInternal(GiottoProgram):
        controllers = ('http-get', )
        model = [get_file, StringIO("Mock file content")]
        cache = cache_
        view = FileView

    return StaticServeInternal

def SingleStaticServe(file_path, cache=None):
    """
    Meta program for serving a single file. Useful for favicon.ico
    """
    cache_ = cache # to avoid a NameError because the attribute is the same name
    def get_file():
        return open(file_path, 'r')

    class StaticServeInternal(GiottoProgram):
        controllers = ('http-get', )
        model = [get_file, StringIO("Mock file content")]
        cache = cache_
        view = FileView

    return StaticServeInternal