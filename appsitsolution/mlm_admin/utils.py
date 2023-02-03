from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context

from shop.models import Order, Material_center


def html_to_pdf_directly(request):
     import cStringIO as StringIO
     template = get_template("template_name.html")
     context = Context({'pagesize':'A4'})
     html = template.render(context)
     result = StringIO.StringIO()
     pdf = pisa.pisaDocument(StringIO.StringIO(html), dest=result)
     if not pdf.err:
         return HttpResponse(result.getvalue(), content_type='application/pdf')
     else: return HttpResponse('Errors')


def get_order_list_for_mlm_admin(cf=False):
     if cf:
          return Order.objects.filter(material_center__frontend=False,
                                      material_center__advisory_owned='NO',
                                      material_center__company_depot='YES',
                                      delete=False,
                                      paid=True)
     else:
          return Order.objects.filter(material_center__frontend=True,
                                      delete=False,
                                      paid=True)

