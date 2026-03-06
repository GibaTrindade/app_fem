from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from conclusao_informal.models import ConclusaoInformalPTM
from eventos.models import EventoPTM
from observacoes.models import ObservacaoEncaminhamentoPTM
from pagamentos.models import PagamentoPTM
from prestacao_contas.models import PrestacaoContaHistorico, PrestacaoContaPTM
from ptms.forms import (
    ConclusaoInformalForm,
    EventoPTMForm,
    ObservacaoEncaminhamentoForm,
    PagamentoPTMForm,
    PrestacaoContaHistoricoForm,
    PrestacaoContaPTMForm,
    PTMForm,
    VistoriaPTMForm,
)
from ptms.models import PTM
from vistorias.models import VistoriaPTM


class PTMListView(ListView):
    model = PTM
    template_name = 'ptms/ptm_list.html'
    context_object_name = 'ptms'
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            PTM.objects.select_related('tipo_fem', 'status_ptm_atual', 'status_obra_atual', 'secretaria')
            .order_by('ordem')
        )
        q = self.request.GET.get('q', '').strip()
        status = self.request.GET.get('status', '').strip()
        municipio = self.request.GET.get('municipio', '').strip()

        if q:
            queryset = queryset.filter(
                Q(ordem__icontains=q) | Q(municipio__icontains=q) | Q(projeto__icontains=q)
            )
        if status:
            queryset = queryset.filter(status_ptm_atual__id=status)
        if municipio:
            queryset = queryset.filter(municipio__icontains=municipio)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_options'] = (
            PTM.objects.values_list('status_ptm_atual__id', 'status_ptm_atual__nome').distinct()
        )
        return context


class PTMDetailView(DetailView):
    model = PTM
    template_name = 'ptms/ptm_detail.html'
    context_object_name = 'ptm'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ptm = self.object
        tab = self.request.GET.get('tab', 'eventos')
        context['tab'] = tab
        context['eventos'] = ptm.eventos.select_related('status_ptm', 'status_obra').all()
        context['pagamentos'] = ptm.pagamentos.all()
        context['vistorias'] = ptm.vistorias.all()
        context['prestacao'] = getattr(ptm, 'prestacao_conta', None)
        context['prestacao_historico'] = context['prestacao'].historico.all() if context['prestacao'] else []
        context['observacoes'] = ptm.observacoes_enc.all()
        context['conclusoes'] = ptm.conclusoes_informais.all()
        return context


class PTMCreateView(CreateView):
    model = PTM
    form_class = PTMForm
    template_name = 'ptms/ptm_form.html'

    def get_success_url(self):
        messages.success(self.request, 'PTM criado com sucesso.')
        return reverse('ptm_detail', kwargs={'pk': self.object.pk})


class PTMUpdateView(UpdateView):
    model = PTM
    form_class = PTMForm
    template_name = 'ptms/ptm_form.html'

    def get_success_url(self):
        messages.success(self.request, 'PTM atualizado com sucesso.')
        return reverse('ptm_detail', kwargs={'pk': self.object.pk})


class PTMDeleteView(DeleteView):
    model = PTM
    template_name = 'ptms/ptm_confirm_delete.html'
    success_url = reverse_lazy('ptm_list')


def _create_child(request, ptm_id, form_class, tab_name, title, save_handler=None):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            if save_handler:
                save_handler(form, ptm)
            else:
                instance = form.save(commit=False)
                instance.ptm = ptm
                instance.save()
            messages.success(request, 'Registro incluído com sucesso.')
            return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab={tab_name}")
    else:
        form = form_class()

    return render(
        request,
        'ptms/child_form.html',
        {'form': form, 'ptm': ptm, 'title': title, 'tab': tab_name},
    )


def evento_create(request, ptm_id):
    return _create_child(request, ptm_id, EventoPTMForm, 'eventos', 'Novo Evento')


def pagamento_create(request, ptm_id):
    return _create_child(request, ptm_id, PagamentoPTMForm, 'pagamentos', 'Novo Pagamento')


def vistoria_create(request, ptm_id):
    return _create_child(request, ptm_id, VistoriaPTMForm, 'vistorias', 'Nova Vistoria')


def observacao_create(request, ptm_id):
    return _create_child(request, ptm_id, ObservacaoEncaminhamentoForm, 'observacoes', 'Nova Observação/Encaminhamento')


def conclusao_create(request, ptm_id):
    return _create_child(request, ptm_id, ConclusaoInformalForm, 'conclusoes', 'Nova Conclusão Informal')


def prestacao_upsert(request, ptm_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    instance, _ = PrestacaoContaPTM.objects.get_or_create(ptm=ptm)
    if request.method == 'POST':
        form = PrestacaoContaPTMForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prestação de contas atualizada com sucesso.')
            return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=prestacao")
    else:
        form = PrestacaoContaPTMForm(instance=instance)

    return render(
        request,
        'ptms/child_form.html',
        {'form': form, 'ptm': ptm, 'title': 'Editar Prestação de Contas', 'tab': 'prestacao'},
    )


def prestacao_historico_create(request, ptm_id):
    def _save(form, ptm):
        prestacao, _ = PrestacaoContaPTM.objects.get_or_create(ptm=ptm)
        instance = form.save(commit=False)
        instance.prestacao = prestacao
        instance.save()

    return _create_child(
        request,
        ptm_id,
        PrestacaoContaHistoricoForm,
        'prestacao',
        'Nova Observação da Prestação de Contas',
        save_handler=_save,
    )
