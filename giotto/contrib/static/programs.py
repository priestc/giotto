from cStringIO import StringIO
from giotto.programs import GiottoProgram
from giotto.views import GiottoView, renders

class FileView(GiottoView):
    @renders('*/*')
    def html(self, result):
        return {'body': result, 'mimetype': ''}

    @renders('text/x-cmd')
    def cmd(self, result):
        return {'body': result.read(), 'mimetype': ''}

def StaticServe(base_path):
    """
    Meta program for serving any file based on the path
    """
    def get_file(path):
        return open(base_path + path, 'r')

    class StaticServe(GiottoProgram):
        controllers = ('http-get', )
        model = [get_file, StringIO("Mock file content")]
        view = FileView

    return StaticServe()

def SingleStaticServe(file_path):
    """
    Meta program for serving a single file. Useful for favicon.ico
    """
    def get_file():
        return open(file_path, 'r')

    class SingleStaticServe(GiottoProgram):
        controllers = ('http-get', )
        model = [get_file, StringIO("Mock file content")]
        view = FileView

    return SingleStaticServe()