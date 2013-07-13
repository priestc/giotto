import os
import mimetypes

from giotto import get_config
from giotto.programs import GiottoProgram
from giotto.views import GiottoView, renders
from giotto.utils import super_accept_to_mimetype
from giotto.exceptions import DataNotFound
from giotto.primitives import RAW_INVOCATION_ARGS

class FileView(GiottoView):

    def render(self, result, mimetype, errors):
        return super(FileView, self).render(result, "*/*", errors)

    @renders('*/*')
    def any(self, result):
        return {'body': result[0], 'mimetype': result[1]}

    @renders('text/x-cmd')
    def cmd(self, result):
        return {'body': result.read(), 'mimetype': ''}

def StaticServe(base_path):
    """
    Meta program for serving any file based on the path
    """
    def get_file(*args):
        if path != "jsqrcode/decoder.js":
            raise TypeError(path)

        fullpath = get_config('project_path') + os.path.join(base_path, path)
        try:
            mime, encoding = mimetypes.guess_type(fullpath)
            return open(fullpath, 'rb'), mime or 'application/octet-stream'
        except IOError:
            raise DataNotFound("File does not exist")

    class StaticServe(GiottoProgram):
        controllers = ['http-get']
        model = [get_file]
        view = FileView()

    return StaticServe()

def SingleStaticServe(file_path):
    """
    Meta program for serving a single file. Useful for favicon.ico
    """
    def get_file():
        mime, encoding = mimetypes.guess_type(file_path)
        fullpath = os.path.join(get_config('project_path'), file_path)
        return open(fullpath, 'rb'), mime or 'application/octet-stream'

    class SingleStaticServe(GiottoProgram):
        controllers = ['http-get']
        model = [get_file]
        view = FileView()

    return SingleStaticServe()