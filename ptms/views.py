from decimal import Decimal, InvalidOperation
import unicodedata

from django.contrib import messages
from django.db.models import Count, DateField, DecimalField, F, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from conclusao_informal.models import ConclusaoInformalPTM
from core.models import StatusObra, StatusPTM
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


def _normalize_text(value):
    text = (value or "").strip()
    text = "".join(
        char for char in unicodedata.normalize("NFD", text) if unicodedata.category(char) != "Mn"
    )
    return " ".join(text.lower().split())


def _normalize_municipio(value):
    return _normalize_text(value)


def _allowed_municipios_for_user(user):
    if user.is_superuser:
        return None
    return {
        _normalize_municipio(v)
        for v in user.user_municipios.select_related("municipio").values_list("municipio__nome", flat=True)
    }


def _user_can_edit_ptm(user, ptm):
    allowed = _allowed_municipios_for_user(user)
    if allowed is None:
        return True
    if not allowed:
        return False
    return _normalize_municipio(ptm.municipio) in allowed


def _deny_edit_if_forbidden(request, ptm, tab="eventos"):
    if _user_can_edit_ptm(request.user, ptm):
        return None
    messages.error(
        request,
        "Voce nao tem permissao para alterar este PTM. Verifique seus municipios vinculados.",
    )
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab={tab}")


def _build_dashboard_context():
    today = timezone.localdate()
    stale_limit = today - timezone.timedelta(days=90)

    latest_vistoria = VistoriaPTM.objects.filter(ptm=OuterRef("pk")).order_by("-ordem_vistoria", "-id")
    latest_evento = EventoPTM.objects.filter(ptm=OuterRef("pk")).order_by("-data_evento", "-id")

    kpi_base = PTM.objects.annotate(
        total_pago=Coalesce(
            Sum("pagamentos__valor_realizado"),
            Value(Decimal("0.00")),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        ),
        parcelas_count=Count("pagamentos__parcela", distinct=True),
        ultima_vistoria_resposta=Subquery(
            latest_vistoria.values("dt_resposta")[:1],
            output_field=DateField(),
        ),
        ultima_vistoria_solicitacao=Subquery(
            latest_vistoria.values("dt_solicitacao")[:1],
            output_field=DateField(),
        ),
        ultimo_evento=Subquery(
            latest_evento.values("data_evento")[:1],
            output_field=DateField(),
        ),
    )

    total_ptms = PTM.objects.count()
    total_teto_fem = PTM.objects.aggregate(
        total=Coalesce(
            Sum("teto_fem"),
            Value(Decimal("0.00")),
            output_field=DecimalField(max_digits=16, decimal_places=2),
        )
    )["total"]
    total_pago = kpi_base.aggregate(
        total=Coalesce(
            Sum("total_pago"),
            Value(Decimal("0.00")),
            output_field=DecimalField(max_digits=16, decimal_places=2),
        )
    )["total"]
    total_saldo = total_teto_fem - total_pago
    execucao_financeira_pct = (
        ((total_pago / total_teto_fem) * Decimal("100")) if total_teto_fem else Decimal("0.00")
    )
    execucao_financeira_pct = execucao_financeira_pct.quantize(Decimal("0.01"))

    return {
        "kpi_total_ptms": total_ptms,
        "kpi_total_teto_fem": total_teto_fem,
        "kpi_total_pago": total_pago,
        "kpi_total_saldo": total_saldo,
        "kpi_execucao_financeira_pct": execucao_financeira_pct,
        "kpi_pagamento_pendente": kpi_base.filter(
            Q(parcelas_count=4) & Q(total_pago__lt=F("teto_fem"))
        ).count(),
        "kpi_sem_vistoria": PTM.objects.filter(vistorias__isnull=True).distinct().count(),
        "kpi_vistoria_desatualizada": kpi_base.filter(vistorias__isnull=False)
        .filter(
            Q(ultima_vistoria_resposta__lt=stale_limit)
            | (Q(ultima_vistoria_resposta__isnull=True) & Q(ultima_vistoria_solicitacao__lt=stale_limit))
        )
        .distinct()
        .count(),
        "kpi_prestacao_vencida": PrestacaoContaPTM.objects.filter(prazo_contas__lt=today)
        .filter(Q(data_prestacao__isnull=True) | Q(data_prestacao__gt=F("prazo_contas")))
        .count(),
        "status_breakdown": PTM.objects.values("status_ptm_atual__nome")
        .annotate(total=Count("id"))
        .order_by("-total", "status_ptm_atual__nome")[:6],
        "secretaria_breakdown": PTM.objects.values("secretaria__nome")
        .annotate(total=Count("id"))
        .order_by("-total", "secretaria__nome")[:6],
        "municipio_breakdown": PTM.objects.values("municipio")
        .annotate(total=Count("id"))
        .order_by("-total", "municipio")[:6],
        "alertas_prestacao": PrestacaoContaPTM.objects.select_related("ptm")
        .filter(prazo_contas__lt=today)
        .filter(Q(data_prestacao__isnull=True) | Q(data_prestacao__gt=F("prazo_contas")))
        .order_by("prazo_contas")[:5],
        "alertas_vistoria": kpi_base.filter(vistorias__isnull=False)
        .filter(
            Q(ultima_vistoria_resposta__lt=stale_limit)
            | (Q(ultima_vistoria_resposta__isnull=True) & Q(ultima_vistoria_solicitacao__lt=stale_limit))
        )
        .order_by("ultima_vistoria_resposta", "ultima_vistoria_solicitacao", "ordem")
        .distinct()[:5],
        "alertas_saldo": kpi_base.filter(total_pago__lt=F("teto_fem"))
        .annotate(
            saldo_receber=F("teto_fem") - F("total_pago"),
        )
        .order_by("-saldo_receber", "ordem")[:5],
    }


class PTMListView(ListView):
    model = PTM
    template_name = "ptms/ptm_list.html"
    context_object_name = "ptms"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            PTM.objects.select_related("tipo_fem", "status_ptm_atual", "status_obra_atual", "secretaria")
            .order_by("ordem")
        )
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        municipio = self.request.GET.get("municipio", "").strip()

        if q:
            q_norm = _normalize_text(q)
            ids = [
                item.id
                for item in queryset
                if q_norm in _normalize_text(item.ordem)
                or q_norm in _normalize_text(item.municipio)
                or q_norm in _normalize_text(item.projeto)
            ]
            queryset = queryset.filter(id__in=ids)
        if status:
            queryset = queryset.filter(status_ptm_atual__id=status)
        if municipio:
            municipio_norm = _normalize_text(municipio)
            ids = [item.id for item in queryset if municipio_norm in _normalize_text(item.municipio)]
            queryset = queryset.filter(id__in=ids)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_options"] = (
            StatusPTM.objects.order_by("nome").values_list("id", "nome").distinct()
        )
        context["can_create_ptm"] = self.request.user.is_superuser or bool(
            _allowed_municipios_for_user(self.request.user)
        )
        context["total_ptms_filtrados"] = context["paginator"].count
        return context


class DashboardView(TemplateView):
    template_name = "ptms/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_build_dashboard_context())
        return context


class PTMDetailView(DetailView):
    model = PTM
    template_name = "ptms/ptm_detail.html"
    context_object_name = "ptm"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ptm = self.object
        tab = self.request.GET.get("tab", "eventos")
        context["tab"] = tab
        context["eventos"] = ptm.eventos.select_related("status_ptm", "status_obra").all()
        context["pagamentos"] = ptm.pagamentos.all()
        context["status_ptm_options"] = StatusPTM.objects.filter(ativo=True).order_by("nome")
        context["status_obra_options"] = StatusObra.objects.filter(ativo=True).order_by("nome")
        context["vistorias"] = ptm.vistorias.all()
        context["prestacao"] = getattr(ptm, "prestacao_conta", None)
        context["prestacao_historico"] = (
            context["prestacao"].historico.all() if context["prestacao"] else []
        )
        context["observacoes"] = ptm.observacoes_enc.all()
        context["conclusoes"] = ptm.conclusoes_informais.all()
        context["can_edit_ptm"] = _user_can_edit_ptm(self.request.user, ptm)
        return context


class PTMCreateView(CreateView):
    model = PTM
    form_class = PTMForm
    template_name = "ptms/ptm_form.html"

    def form_valid(self, form):
        allowed = _allowed_municipios_for_user(self.request.user)
        if allowed is not None:
            if not allowed:
                messages.error(
                    self.request,
                    "Seu usuario nao possui municipios vinculados para criar PTM.",
                )
                return self.form_invalid(form)
            municipio_form = _normalize_municipio(form.cleaned_data.get("municipio"))
            if municipio_form not in allowed:
                messages.error(
                    self.request,
                    "Voce so pode criar PTM para municipios vinculados ao seu usuario.",
                )
                return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "PTM criado com sucesso.")
        return reverse("ptm_detail", kwargs={"pk": self.object.pk})


class PTMUpdateView(UpdateView):
    model = PTM
    form_class = PTMForm
    template_name = "ptms/ptm_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        blocked = _deny_edit_if_forbidden(request, self.object)
        if blocked:
            return blocked
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        allowed = _allowed_municipios_for_user(self.request.user)
        if allowed is not None and _normalize_municipio(form.cleaned_data.get("municipio")) not in allowed:
            messages.error(
                self.request,
                "Voce so pode salvar PTM com municipio vinculado ao seu usuario.",
            )
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "PTM atualizado com sucesso.")
        return reverse("ptm_detail", kwargs={"pk": self.object.pk})


class PTMDeleteView(DeleteView):
    model = PTM
    template_name = "ptms/ptm_confirm_delete.html"
    success_url = reverse_lazy("ptm_list")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        blocked = _deny_edit_if_forbidden(request, self.object)
        if blocked:
            return blocked
        return super().dispatch(request, *args, **kwargs)


def evento_create(request, ptm_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="eventos")
    if blocked:
        return blocked
    if request.method == "POST":
        form = EventoPTMForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.ptm = ptm
            instance.save()
            messages.success(request, "Evento criado com sucesso.")
        else:
            errors = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items())
            messages.error(request, f"Nao foi possivel criar evento. {errors}")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=eventos")


def evento_update(request, ptm_id, evento_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="eventos")
    if blocked:
        return blocked
    evento = get_object_or_404(EventoPTM, pk=evento_id, ptm=ptm)
    if request.method == "POST":
        form = EventoPTMForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento atualizado com sucesso.")
        else:
            errors = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items())
            messages.error(request, f"Nao foi possivel atualizar evento. {errors}")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=eventos")


def evento_delete(request, ptm_id, evento_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="eventos")
    if blocked:
        return blocked
    evento = get_object_or_404(EventoPTM, pk=evento_id, ptm=ptm)
    if request.method == "POST":
        evento.delete()
        messages.success(request, "Evento excluido com sucesso.")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=eventos")


def pagamento_create(request, ptm_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="pagamentos")
    if blocked:
        return blocked
    if request.method == "POST":
        form = PagamentoPTMForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.ptm = ptm
            instance.save()
            messages.success(request, "Pagamento criado com sucesso.")
        else:
            errors = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items())
            messages.error(request, f"Nao foi possivel criar pagamento. {errors}")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=pagamentos")


def pagamento_update(request, ptm_id, pagamento_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="pagamentos")
    if blocked:
        return blocked
    pagamento = get_object_or_404(PagamentoPTM, pk=pagamento_id, ptm=ptm)
    if request.method == "POST":
        form = PagamentoPTMForm(request.POST, instance=pagamento)
        if form.is_valid():
            form.save()
            messages.success(request, "Pagamento atualizado com sucesso.")
        else:
            errors = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items())
            messages.error(request, f"Nao foi possivel atualizar pagamento. {errors}")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=pagamentos")


def pagamento_delete(request, ptm_id, pagamento_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="pagamentos")
    if blocked:
        return blocked
    pagamento = get_object_or_404(PagamentoPTM, pk=pagamento_id, ptm=ptm)
    if request.method == "POST":
        pagamento.delete()
        messages.success(request, "Pagamento excluido com sucesso.")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=pagamentos")


def vistoria_create(request, ptm_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="vistorias")
    if blocked:
        return blocked
    if request.method == "POST":
        form = VistoriaPTMForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            next_ordem = (
                ptm.vistorias.order_by("-ordem_vistoria").values_list("ordem_vistoria", flat=True).first() or 0
            ) + 1
            instance.ptm = ptm
            instance.ordem_vistoria = next_ordem
            instance.save()
            messages.success(request, "Vistoria criada com sucesso.")
        else:
            errors = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items())
            messages.error(request, f"Nao foi possivel criar a vistoria. {errors}")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=vistorias")


def vistoria_update(request, ptm_id, vistoria_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="vistorias")
    if blocked:
        return blocked
    vistoria = get_object_or_404(VistoriaPTM, pk=vistoria_id, ptm=ptm)
    if request.method == "POST":
        post_data = request.POST.copy()
        raw_pct = (post_data.get("percentual_execucao") or "").strip()
        if raw_pct:
            try:
                pct = Decimal(raw_pct.replace(",", "."))
                if pct > Decimal("1"):
                    pct = pct / Decimal("100")
                post_data["percentual_execucao"] = str(pct)
            except (InvalidOperation, ValueError):
                pass
        form = VistoriaPTMForm(post_data, instance=vistoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Vistoria atualizada com sucesso.")
        else:
            errors = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items())
            messages.error(request, f"Nao foi possivel atualizar a vistoria. {errors}")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=vistorias")


def vistoria_delete(request, ptm_id, vistoria_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="vistorias")
    if blocked:
        return blocked
    vistoria = get_object_or_404(VistoriaPTM, pk=vistoria_id, ptm=ptm)
    if request.method == "POST":
        vistoria.delete()
        messages.success(request, "Vistoria excluida com sucesso.")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=vistorias")


def observacao_create(request, ptm_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="observacoes")
    if blocked:
        return blocked
    if request.method == "POST":
        form = ObservacaoEncaminhamentoForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.ptm = ptm
            instance.save()
            messages.success(request, "Observacao/encaminhamento criado com sucesso.")
        else:
            errors = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items())
            messages.error(request, f"Nao foi possivel criar observacao/encaminhamento. {errors}")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=observacoes")


def observacao_update(request, ptm_id, observacao_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="observacoes")
    if blocked:
        return blocked
    observacao = get_object_or_404(ObservacaoEncaminhamentoPTM, pk=observacao_id, ptm=ptm)
    if request.method == "POST":
        form = ObservacaoEncaminhamentoForm(request.POST, instance=observacao)
        if form.is_valid():
            form.save()
            messages.success(request, "Observacao/encaminhamento atualizado com sucesso.")
        else:
            errors = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items())
            messages.error(request, f"Nao foi possivel atualizar observacao/encaminhamento. {errors}")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=observacoes")


def observacao_delete(request, ptm_id, observacao_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="observacoes")
    if blocked:
        return blocked
    observacao = get_object_or_404(ObservacaoEncaminhamentoPTM, pk=observacao_id, ptm=ptm)
    if request.method == "POST":
        observacao.delete()
        messages.success(request, "Observacao/encaminhamento excluido com sucesso.")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=observacoes")


def conclusao_create(request, ptm_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="conclusoes")
    if blocked:
        return blocked
    if request.method == "POST":
        form = ConclusaoInformalForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.ptm = ptm
            instance.save()
            messages.success(request, "Conclusao informal criada com sucesso.")
        else:
            errors = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items())
            messages.error(request, f"Nao foi possivel criar conclusao informal. {errors}")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=conclusoes")


def conclusao_update(request, ptm_id, conclusao_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="conclusoes")
    if blocked:
        return blocked
    conclusao = get_object_or_404(ConclusaoInformalPTM, pk=conclusao_id, ptm=ptm)
    if request.method == "POST":
        form = ConclusaoInformalForm(request.POST, instance=conclusao)
        if form.is_valid():
            form.save()
            messages.success(request, "Conclusao informal atualizada com sucesso.")
        else:
            errors = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items())
            messages.error(request, f"Nao foi possivel atualizar conclusao informal. {errors}")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=conclusoes")


def conclusao_delete(request, ptm_id, conclusao_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="conclusoes")
    if blocked:
        return blocked
    conclusao = get_object_or_404(ConclusaoInformalPTM, pk=conclusao_id, ptm=ptm)
    if request.method == "POST":
        conclusao.delete()
        messages.success(request, "Conclusao informal excluida com sucesso.")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=conclusoes")


def prestacao_upsert(request, ptm_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="prestacao")
    if blocked:
        return blocked
    instance, _ = PrestacaoContaPTM.objects.get_or_create(ptm=ptm)
    if request.method == "POST":
        form = PrestacaoContaPTMForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Prestacao de contas atualizada com sucesso.")
        else:
            errors = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items())
            messages.error(request, f"Nao foi possivel salvar prestacao. {errors}")
        return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=prestacao")
    else:
        form = PrestacaoContaPTMForm(instance=instance)

    return render(
        request,
        "ptms/child_form.html",
        {"form": form, "ptm": ptm, "title": "Editar Prestacao de Contas", "tab": "prestacao"},
    )


def prestacao_historico_create(request, ptm_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="prestacao")
    if blocked:
        return blocked
    if request.method == "POST":
        form = PrestacaoContaHistoricoForm(request.POST)
        if form.is_valid():
            prestacao, _ = PrestacaoContaPTM.objects.get_or_create(ptm=ptm)
            instance = form.save(commit=False)
            instance.prestacao = prestacao
            instance.save()
            messages.success(request, "Observacao da prestacao adicionada com sucesso.")
        else:
            errors = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items())
            messages.error(request, f"Nao foi possivel adicionar observacao. {errors}")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=prestacao")


def prestacao_historico_update(request, ptm_id, historico_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="prestacao")
    if blocked:
        return blocked
    prestacao = get_object_or_404(PrestacaoContaPTM, ptm=ptm)
    historico = get_object_or_404(PrestacaoContaHistorico, pk=historico_id, prestacao=prestacao)
    if request.method == "POST":
        form = PrestacaoContaHistoricoForm(request.POST, instance=historico)
        if form.is_valid():
            form.save()
            messages.success(request, "Observacao da prestacao atualizada com sucesso.")
        else:
            errors = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items())
            messages.error(request, f"Nao foi possivel atualizar observacao. {errors}")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=prestacao")


def prestacao_historico_delete(request, ptm_id, historico_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="prestacao")
    if blocked:
        return blocked
    prestacao = get_object_or_404(PrestacaoContaPTM, ptm=ptm)
    historico = get_object_or_404(PrestacaoContaHistorico, pk=historico_id, prestacao=prestacao)
    if request.method == "POST":
        historico.delete()
        messages.success(request, "Observacao da prestacao excluida com sucesso.")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=prestacao")


def prestacao_delete(request, ptm_id):
    ptm = get_object_or_404(PTM, pk=ptm_id)
    blocked = _deny_edit_if_forbidden(request, ptm, tab="prestacao")
    if blocked:
        return blocked
    prestacao = PrestacaoContaPTM.objects.filter(ptm=ptm).first()
    if request.method == "POST" and prestacao:
        prestacao.delete()
        messages.success(request, "Prestacao de contas excluida com sucesso.")
    return redirect(f"{reverse('ptm_detail', kwargs={'pk': ptm.pk})}?tab=prestacao")
