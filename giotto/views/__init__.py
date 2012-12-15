import json
import mimetypes

import magic
import mimeparse

from jinja2 import Template
from jinja2.exceptions import TemplateNotFound
from giotto.exceptions import NoViewMethod
from giotto.utils import Mock, htmlize, htmlize_list, pre_process_json

def renders(*mimetypes):
    def decorator(func):
        func.render_map = {}
        for mimetype in mimetypes:
            func.render_map[mimetype] = func.__name__
        return func
    return decorator

class GiottoView(object):
    """
    Base class for all Giotto view objects. All Giotto Views must at least descend
    from this class, as ths class contains piping that the controller calls.
    """

    render_map = {}

    def __init__(self):
        for method in [x for x in dir(self) if not x.startswith('__')]:
            # register all render methods based on the render decorator
            attr = getattr(self, method)
            render_map = getattr(attr, 'render_map', None)
            if render_map and type(render_map) == dict:
                self.render_map.update(render_map)

    def render(self, result, mimetype, errors=None):
        status = 200
        available_mimetypes = self.render_map.keys()
        target_mimetype = mimeparse.best_match(available_mimetypes, mimetype)
        self.errors = errors or Mock()
        renderer = self.render_map[target_mimetype]

        if not renderer:
            raise NoViewMethod("%s not supported for this program" % mimetype)

        data = getattr(self, renderer)(result)

        if target_mimetype == '*/*':
            data['mimetype'] = ''

        if not 'mimetype' in data:
            data['mimetype'] = target_mimetype

        data['status'] = status
        return data

class BasicView(GiottoView):
    """
    Basic viewer that contains generic functionality for showing any data.
    """
    @renders('application/json')
    def json(self, result):
        obj = pre_process_json(result)
        j = json.dumps(obj)
        return {'body': j, 'mimetype': 'application/json'}

    @renders('text/html')
    def html(self, result):
        """
        Try to display any object in sensible HTML.
        """
        css = """
        <style>
            table {border-collapse: collapse}
            td, th {border: 1px solid black; padding: 10px}
            th {background: white;}
            tr:nth-child(even) {background: #DDEE00}
            tr:nth-child(odd) {background: #00EEDD}
        </style>
        """
        h1 = htmlize(type(result))

        if result is None:
            return "<!DOCTYPE html><html><body>None</body></html>"

        out = []
        if not hasattr(result, 'iteritems'):
            header = "<tr><th>Value</th></tr>"
            if type(result) is list:
                result = htmlize_list(result)
            else:
                result = htmlize(result)
            out = ["<tr><td>" + result + "</td></tr>"]
        elif hasattr(result, 'lower'):
            out = ["<tr><td>" + result + "</td></tr>"]
        else:
            # object is a dict
            header = "<tr><th>Key</th><th>Value</th></tr>"
            for key, value in result.iteritems():
                v = htmlize(value)
                row = "<tr><td>{0}</td><td>{1}</td></tr>".format(key, v)
                out.append(row)

        out = "\n".join(out)
        return {'body': """<!DOCTYPE html>
        <html>
            <head>{0}</head>
            <body>
                <h1>{1}</h1>
                <table>
                    {2}
                    {3}
                </table>
            </body>
        </html>""".format(css, h1, header, out),
        'mimetype': 'text/html'}

    @renders('text/x-cmd', 'text/x-irc', 'text/plain')
    def plaintext(self, result):
        out = []
        if hasattr(result, 'iteritems'):
            to_iterate = result.iteritems()
        elif hasattr(result, 'lower'):
            return {'body': result, 'mimetype': "text/plain"}
        else:
            to_iterate = result.__dict__.iteritems()

        for key, value in to_iterate:
            row = "{0} - {1}".format(key, value)
            out.append(row)

        return {'body': "\n".join(out), 'mimetype': "text/plain"}

def JinjaTemplateView(template_name, name='data', mimetype="text/html"):
    class JinjaTemplateView(BasicView):
        @renders(mimetype)
        def html(self, result):
            from giotto import config
            template = config.jinja2_env.get_template(template_name)
            context = {name: result or Mock(), 'errors': self.errors}
            rendered = template.render(**context)
            return {'body': rendered, 'mimetype': mimetype}

    return JinjaTemplateView

class ImageViewer(GiottoView):
    """
    For viewing images. The 'result' must be a file object that contains image
    data (doesn't matter the format).
    """

    @renders('text/plain')
    def plaintext(self, result):
        """
        Converts the image object into an ascii representation. Code taken from
        http://a-eter.blogspot.com/2010/04/image-to-ascii-art-in-python.html
        """
        from PIL import Image

        ascii_chars = ['#', 'A', '@', '%', 'S', '+', '<', '*', ':', ',', '.']

        def image_to_ascii(image):
            image_as_ascii = []
            all_pixels = list(image.getdata())
            for pixel_value in all_pixels:
                index = pixel_value / 25 # 0 - 10
                image_as_ascii.append(ascii_chars[index])
            return image_as_ascii   

        img = Image.open(result)
        width, heigth = img.size
        new_width = 80 
        new_heigth = int((heigth * new_width) / width)
        new_image = img.resize((new_width, new_heigth))
        new_image = new_image.convert("L") # convert to grayscale

        # now that we have a grayscale image with some fixed width we have to convert every pixel
        # to the appropriate ascii character from "ascii_chars"
        img_as_ascii = image_to_ascii(new_image)
        img_as_ascii = ''.join(ch for ch in img_as_ascii)
        out = []
        for c in range(0, len(img_as_ascii), new_width):
            out.append(img_as_ascii[c:c+new_width])

        return "\n".join(out)

    def image(self, result):
        return result

    def image_jpeg(self, result):
        return self.image(result)

    def text_cmd(self, result):
        return result.read()

    def text_html(self, result):
        return """<!DOCTYPE html>
        <html>
            <body>
                <img src="/multiply?x=4&y=7">
            </body>
        </html>"""
