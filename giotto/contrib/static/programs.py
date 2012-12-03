from cStringIO import StringIO
from giotto.programs import GiottoProgram
from giotto.utils import get_config
from giotto.views import GiottoView

class FileView(GiottoView):
    def text_html(self, result):
        return result

    def text_cmd(self, result):
        return result.read()

def StaticServe(base_path):
    """
    Meta program for serving any file based on the path
    """
    def get_file(path):
        return open(base_path + path, 'r')

    class StaticServeInternal(GiottoProgram):
        name = 'static'
        controllers = ('http-get', )
        model = [get_file, StringIO("Mock file content")]
        view = FileView

    return StaticServeInternal

def SingleStaticServe(file_path):
    """
    Meta program for serving a single file. Useful for favicon.ico
    """
    def get_file():
        return open(file_path, 'r')

    class StaticServeInternal(GiottoProgram):
        name = 'static'
        controllers = ('http-get', )
        model = [get_file, StringIO("Mock file content")]
        view = FileView

    return StaticServeInternal