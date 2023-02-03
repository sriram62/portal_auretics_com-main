from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
# specific to this view
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from mlm_admin.forms import NoticeTemplateForm, ReadOnlyNoticeTemplateForm
from notify.models import NoticeTemplate


@method_decorator(login_required, name='dispatch')
class TemplateListView(ListView):
    model = NoticeTemplate
    template_name = 'mlm_admin/template/template_list.html'
    context_object_name = 'template'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(books, self.paginate_by)
        try:
            templates = paginator.page(page)
        except PageNotAnInteger:
            templates = paginator.page(1)
        except EmptyPage:
            templates = paginator.page(paginator.num_pages)
        context['templates'] = templates
        return context


@method_decorator(login_required, name='dispatch')
class TemplateDeleteView(DeleteView):
    model = NoticeTemplate
    context_object_name = 'template'
    paginate_by = 10
    success_url = reverse_lazy('template_list')
    template_name = 'mlm_admin/template/delete_confirm.html'

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return HttpResponseRedirect(self.success_url)
        else:
            return super().post(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class TemplateCreateView(CreateView):
    model = NoticeTemplate
    template_name = 'mlm_admin/template/template_create.html'
    context_object_name = 'template'
    form_class = NoticeTemplateForm


@method_decorator(login_required, name='dispatch')
class TemplateDetailView(UpdateView):
    model = NoticeTemplate
    template_name = 'mlm_admin/template/template_detail.html'
    context_object_name = 'template'
    form_class = ReadOnlyNoticeTemplateForm
    success_url = reverse_lazy('template_list')


@method_decorator(login_required, name='dispatch')
class TemplateUpdateView(UpdateView):
    model = NoticeTemplate
    template_name = 'mlm_admin/template/template_update.html'
    context_object_name = 'template'
    form_class = NoticeTemplateForm
    success_url = reverse_lazy('template_list')
