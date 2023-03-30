from django.core.exceptions import ValidationError
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils.deconstruct import deconstructible
from PIL import Image

# PDF Handler

def render_to_pdf(template_path, context={}):
    template = get_template(template_path)
    html = template.render(context)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="drink_stock.pdf"'
        return response

    return HttpResponse('Error rendering PDF', status=400)


# Image Handler

@deconstructible
class ImageValidator:
    def __init__(self, max_size=5 * 1024 * 1024, allowed_extensions=None):
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions or []

    def __call__(self, image):
        if image.size > self.max_size:
            raise ValidationError(f'Maximum file size is {self.max_size} bytes')

        if not self._is_valid_extension(image):
            allowed_extensions = ", ".join(self.allowed_extensions)
            raise ValidationError(f'Only {allowed_extensions} files are allowed')

        return image

    def _is_valid_extension(self, image):
        extension = image.name.split('.')[-1]
        return extension.lower() in self.allowed_extensions


def validate_image(image, max_size=5 * 1024 * 1024, allowed_extensions=None):
    validator = ImageValidator(max_size=max_size, allowed_extensions=allowed_extensions)
    validator(Image.open(image))
