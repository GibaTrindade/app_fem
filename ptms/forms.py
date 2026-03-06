from django import forms

from conclusao_informal.models import ConclusaoInformalPTM
from eventos.models import EventoPTM
from observacoes.models import ObservacaoEncaminhamentoPTM
from pagamentos.models import PagamentoPTM
from prestacao_contas.models import PrestacaoContaHistorico, PrestacaoContaPTM
from ptms.models import PTM
from vistorias.models import VistoriaPTM


class DateInput(forms.DateInput):
    input_type = 'date'


class PTMForm(forms.ModelForm):
    class Meta:
        model = PTM
        fields = [
            'ordem', 'regiao', 'municipio', 'projeto', 'projeto_detalhado', 'tipo_fem',
            'data_final', 'data_aprovacao', 'teto_fem', 'investimento_total', 'recurso_fem',
            'rendimentos_fem', 'contrapartida', 'ressalva', 'secretaria', 'area_investimento',
            'conta_ptm', 'descricao', 'populacao_beneficiada',
        ]
        widgets = {
            'data_final': DateInput(),
            'data_aprovacao': DateInput(),
        }


class EventoPTMForm(forms.ModelForm):
    class Meta:
        model = EventoPTM
        fields = ['data_evento', 'descricao', 'status_ptm', 'status_obra']
        widgets = {'data_evento': DateInput()}


class PagamentoPTMForm(forms.ModelForm):
    class Meta:
        model = PagamentoPTM
        fields = [
            'parcela', 'tipo_registro', 'dt_solicitacao', 'dt_envio_pg', 'dt_pagamento',
            'valor_previsto', 'valor_realizado', 'numero_ob', 'numero_empenho', 'observacao',
        ]
        widgets = {
            'dt_solicitacao': DateInput(),
            'dt_envio_pg': DateInput(),
            'dt_pagamento': DateInput(),
        }


class VistoriaPTMForm(forms.ModelForm):
    class Meta:
        model = VistoriaPTM
        fields = ['dt_solicitacao', 'dt_resposta', 'percentual_execucao', 'observacao']
        widgets = {
            'dt_solicitacao': DateInput(),
            'dt_resposta': DateInput(),
        }


class PrestacaoContaPTMForm(forms.ModelForm):
    class Meta:
        model = PrestacaoContaPTM
        fields = ['prazo_contas', 'data_prestacao', 'situacao']
        widgets = {
            'prazo_contas': DateInput(),
            'data_prestacao': DateInput(),
        }


class PrestacaoContaHistoricoForm(forms.ModelForm):
    class Meta:
        model = PrestacaoContaHistorico
        fields = ['data', 'observacao']
        widgets = {'data': DateInput()}


class ObservacaoEncaminhamentoForm(forms.ModelForm):
    class Meta:
        model = ObservacaoEncaminhamentoPTM
        fields = ['data', 'origem', 'observacao']
        widgets = {'data': DateInput()}


class ConclusaoInformalForm(forms.ModelForm):
    class Meta:
        model = ConclusaoInformalPTM
        fields = ['percentual_declarado', 'data', 'contato', 'observacao']
        widgets = {'data': DateInput()}
