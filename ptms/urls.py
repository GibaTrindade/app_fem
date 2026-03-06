from django.urls import path

from ptms.views import (
    PTMCreateView,
    PTMDeleteView,
    PTMDetailView,
    PTMListView,
    PTMUpdateView,
    conclusao_create,
    evento_create,
    observacao_create,
    pagamento_create,
    prestacao_historico_create,
    prestacao_upsert,
    vistoria_create,
)

urlpatterns = [
    path('', PTMListView.as_view(), name='ptm_list'),
    path('ptms/novo/', PTMCreateView.as_view(), name='ptm_create'),
    path('ptms/<int:pk>/', PTMDetailView.as_view(), name='ptm_detail'),
    path('ptms/<int:pk>/editar/', PTMUpdateView.as_view(), name='ptm_update'),
    path('ptms/<int:pk>/excluir/', PTMDeleteView.as_view(), name='ptm_delete'),

    path('ptms/<int:ptm_id>/eventos/novo/', evento_create, name='evento_create'),
    path('ptms/<int:ptm_id>/pagamentos/novo/', pagamento_create, name='pagamento_create'),
    path('ptms/<int:ptm_id>/vistorias/novo/', vistoria_create, name='vistoria_create'),
    path('ptms/<int:ptm_id>/prestacao/editar/', prestacao_upsert, name='prestacao_upsert'),
    path('ptms/<int:ptm_id>/prestacao/historico/novo/', prestacao_historico_create, name='prestacao_historico_create'),
    path('ptms/<int:ptm_id>/observacoes/novo/', observacao_create, name='observacao_create'),
    path('ptms/<int:ptm_id>/conclusoes/novo/', conclusao_create, name='conclusao_create'),
]
