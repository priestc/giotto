import json
import mimetypes

import magic
from jinja2 import Template
from giotto.exceptions import NoViewMethod

class GiottoView(object):
    def __init__(self, result, controller):
        """
        result == the output from the model
        """
        self.result = result
        self.controller = controller
        
    def application_json(self, result):
        try:
            j = json.dumps(result)
        except TypeError:
            j = json.dumps(result.__dict__)

        return j

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

class GiottoTemplateView(GiottoView):
    """
    A view renderer where each mimetype renderer returns a jinja template that
    will get rendered automatically. The context_name attribute denotes the
    name of the model object in the template.
    """
    context_name = 'obj'
    def render(self, mimetype):
        result = super(GiottoTemplateView, self).render(mimetype)
        template = result['body']
        if hasattr(template, 'lower'):
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
