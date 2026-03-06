from decimal import Decimal, InvalidOperation

from django import forms

from conclusao_informal.models import ConclusaoInformalPTM
from eventos.models import EventoPTM
from observacoes.models import ObservacaoEncaminhamentoPTM
from pagamentos.models import PagamentoPTM
from prestacao_contas.models import PrestacaoContaHistorico, PrestacaoContaPTM
from ptms.models import PTM
from vistorias.models import VistoriaPTM


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs["class"] = f"{attrs.get('class', '')} form-control".strip()
        super().__init__(attrs=attrs)


class BaseBootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
                continue
            css = widget.attrs.get("class", "")
            if isinstance(widget, forms.Select):
                widget.attrs["class"] = f"{css} form-select".strip()
            else:
                widget.attrs["class"] = f"{css} form-control".strip()


class PTMForm(BaseBootstrapModelForm):
    class Meta:
        model = PTM
        fields = [
            "ordem",
            "regiao",
            "municipio",
            "projeto",
            "projeto_detalhado",
            "tipo_fem",
            "data_final",
            "data_aprovacao",
            "teto_fem",
            "investimento_total",
            "recurso_fem",
            "rendimentos_fem",
            "contrapartida",
            "ressalva",
            "secretaria",
            "area_investimento",
            "conta_ptm",
            "descricao",
            "populacao_beneficiada",
        ]
        widgets = {
            "data_final": DateInput(),
            "data_aprovacao": DateInput(),
        }


class EventoPTMForm(BaseBootstrapModelForm):
    class Meta:
        model = EventoPTM
        fields = ["data_evento", "descricao", "status_ptm", "status_obra"]
        widgets = {"data_evento": DateInput()}


class PagamentoPTMForm(BaseBootstrapModelForm):
    class Meta:
        model = PagamentoPTM
        fields = [
            "parcela",
            "tipo_registro",
            "dt_solicitacao",
            "dt_envio_pg",
            "dt_pagamento",
            "valor_previsto",
            "valor_realizado",
            "numero_ob",
            "numero_empenho",
            "observacao",
        ]
        widgets = {
            "dt_solicitacao": DateInput(),
            "dt_envio_pg": DateInput(),
            "dt_pagamento": DateInput(),
        }


class VistoriaPTMForm(BaseBootstrapModelForm):
    percentual_execucao = forms.CharField(required=False)

    class Meta:
        model = VistoriaPTM
        fields = ["dt_solicitacao", "dt_resposta", "percentual_execucao", "observacao"]
        widgets = {
            "dt_solicitacao": DateInput(),
            "dt_resposta": DateInput(),
        }

    def clean_percentual_execucao(self):
        raw = (self.cleaned_data.get("percentual_execucao") or "").strip()
        if not raw:
            return Decimal("0.0000")
        raw = raw.replace("%", "").replace(",", ".")
        try:
            valor = Decimal(raw)
        except InvalidOperation:
            raise forms.ValidationError("Informe um percentual valido.")
        if valor > Decimal("1"):
            return (valor / Decimal("100")).quantize(Decimal("0.0001"))
        return valor.quantize(Decimal("0.0001"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["percentual_execucao"].required = False


class PrestacaoContaPTMForm(BaseBootstrapModelForm):
    class Meta:
        model = PrestacaoContaPTM
        fields = ["prazo_contas", "data_prestacao", "situacao"]
        widgets = {
            "prazo_contas": DateInput(),
            "data_prestacao": DateInput(),
        }


class PrestacaoContaHistoricoForm(BaseBootstrapModelForm):
    class Meta:
        model = PrestacaoContaHistorico
        fields = ["data", "observacao"]
        widgets = {"data": DateInput()}


class ObservacaoEncaminhamentoForm(BaseBootstrapModelForm):
    class Meta:
        model = ObservacaoEncaminhamentoPTM
        fields = ["data", "origem", "observacao"]
        widgets = {"data": DateInput()}


class ConclusaoInformalForm(BaseBootstrapModelForm):
    percentual_declarado = forms.CharField(required=False)

    class Meta:
        model = ConclusaoInformalPTM
        fields = ["percentual_declarado", "data", "contato", "observacao"]
        widgets = {"data": DateInput()}

    def clean_percentual_declarado(self):
        raw = (self.cleaned_data.get("percentual_declarado") or "").strip()
        if not raw:
            return Decimal("0.0000")
        raw = raw.replace("%", "").replace(",", ".")
        try:
            valor = Decimal(raw)
        except InvalidOperation:
            raise forms.ValidationError("Informe um percentual valido.")
        if valor > Decimal("1"):
            return (valor / Decimal("100")).quantize(Decimal("0.0001"))
        return valor.quantize(Decimal("0.0001"))
