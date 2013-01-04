import os
import mimetypes

from giotto.programs import GiottoProgram
from giotto.views import GiottoView, renders
from giotto.utils import super_accept_to_mimetype
from giotto.exceptions import DataNotFound


class FileView(GiottoView):
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
    def get_file(path):
        fullpath = base_path + path
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
        return open(file_path, 'rb'), mime or 'application/octet-stream'

    class SingleStaticServe(GiottoProgram):
        controllers = ['http-get']
        model = [get_file]
        view = FileView()

    return SingleStaticServe()