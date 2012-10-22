import json
import mimetypes

import magic
from jinja2 import Template
from jinja2.exceptions import TemplateNotFound
from giotto.exceptions import NoViewMethod
from giotto.utils import get_config

class GiottoView(object):
    """
    Base class for all Giotto view objects. All Giotto Views must at least descend
    from this class, as ths class contains piping that the controller calls.
    """
    def __init__(self, result, controller):
        """
        result == the output from the model
        """
        self.result = result
        self.controller = controller

    def render(self, mimetype):
        status = 200
        variable_mimetype = False
        if mimetype.endswith('/*'):
            # if the mimetype is defined with a variable subtype, then
            # use the 'supertype' render method, and then determine the
            # actual mimetype later.
            variable_mimetype = True
            mimetype = mimetype[:-2] # 'image/*' --> 'image'
        
        method = mimetype.replace('/', '_')
        renderer = getattr(self, method, None)
        
        if not renderer:
            raise NoViewMethod("%s not supported for this program" % mimetype)

        data = renderer(self.result)

        if variable_mimetype:
            mimetype = magic.from_buffer(data.read(1024), mime=True)
            data.seek(0)

        return {'body': data, 'mimetype': mimetype, 'status': status}

def htmlize(value):
    """
    Turn any object into a html viewable entity.
    """
    return str(value).replace('<', '&lt;').replace('>', '&gt;')

def htmlize_list(items):
    """
    Turn a python list into an html list.
    """
    out = ["<ul>"]
    for item in items:
        out.append("<li>" + htmlize(item) + "</li>")
    out.append("</ul>")
    return "\n".join(out)

class BasicView(GiottoView):
    """
    Basic viewer that contains generic functionality for showing any data.
    """
    def application_json(self, result):
        try:
            j = json.dumps(result)
        except TypeError:
            j = json.dumps(result.__dict__)

        return j

    def text_cmd(self, result):
        return self.text_plain(result)

    def text_html(self, result):
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
            return "<!DOCTYPE html><html><body><table>None</table></body></html>"
        if not hasattr(result, 'iteritems'):
            header = "<tr><th>Value</th></tr>"
            if type(result) is list:
                result = htmlize_list(result)
            else:
                result = htmlize(result)
            out = ["<tr><td>" + result + "</td></tr>"]
        else:
            # object is a dict
            header = "<tr><th>Key</th><th>Value</th></tr>"
            for key, value in result.iteritems():
                v = htmlize(value)
                row = "<tr><td>{0}</td><td>{1}</td></tr>".format(key, v)
                out.append(row)

        out = "\n".join(out)
        return """<!DOCTYPE html><html><head>{1}</head><body><h1>{3}</h1>
        <table>
            {2}
            {0}
        </table>
        </body></html>""".format(out, css, header, h1)

    def text_plain(self, result):
        out = []
        for key, value in result.iteritems():
            row = "{0} - {1}".format(key, value)
            out.append(row)

        return "\n".join(out)

class JinjaTemplateView(BasicView):
    """
    A view renderer where each mimetype renderer returns a jinja template that
    will get rendered automatically. The context_name attribute denotes the
    name of the model object in the template. Each mimetype method should return
    a string that locates a jinja2 template. Required is to define a jinja2 environment
    (``jinja2_env``) in your project's ``config.py`` file.
    """
    context_name = 'obj'
    def render(self, mimetype):
        jinja2_env = get_config('jinja2_env')
        result = super(JinjaTemplateView, self).render(mimetype)
        template = result['body']
        if hasattr(template, 'lower'):
            try:
                jinja_template = jinja2_env.get_template(template)
            except TemplateNotFound:
                jinja_template = Template(template)

            rendered = jinja_template.render(obj=self.result)
            result['body'] = rendered
            return result
        raise TypeError('Template must be a string')

class ImageViewer(GiottoView):
    """
    For viewing images. The 'result' must be a file object that contains image
    data (doesn't matter the format).
    """

    def text_plain(self, result):
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
