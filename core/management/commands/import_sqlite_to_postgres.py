from __future__ import annotations

import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.contrib.auth import get_user_model
from django.contrib.admin.models import LogEntry
from django.db import connection, transaction
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from conclusao_informal.models import ConclusaoInformalPTM
from core.models import (
    AreaInvestimento,
    Municipio,
    Secretaria,
    StatusAnaliseDocumentacao,
    StatusObra,
    StatusPTM,
    TipoFEM,
    UserMunicipio,
)
from eventos.models import EventoPTM
from observacoes.models import ObservacaoEncaminhamentoPTM
from pagamentos.models import PagamentoPTM
from prestacao_contas.models import PrestacaoContaHistorico, PrestacaoContaPTM
from ptms.models import DocumentoPublicoPTM, PTM
from vistorias.models import VistoriaPTM


@dataclass
class ImportCounts:
    user: int = 0
    tipo_fem: int = 0
    status_ptm: int = 0
    status_obra: int = 0
    status_analise_documentacao: int = 0
    area_investimento: int = 0
    secretaria: int = 0
    municipio: int = 0
    user_municipio: int = 0
    ptm: int = 0
    documento_publico: int = 0
    evento: int = 0
    pagamento: int = 0
    vistoria: int = 0
    prestacao: int = 0
    prestacao_historico: int = 0
    observacao: int = 0
    conclusao: int = 0
    admin_log: int = 0


def _to_datetime(value):
    if value in (None, ""):
        return None
    if hasattr(value, "tzinfo"):
        if timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_default_timezone())
        return value
    parsed = parse_datetime(str(value))
    if parsed and timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_default_timezone())
    return parsed


def _to_date(value):
    if value in (None, ""):
        return None
    parsed = parse_date(str(value))
    return parsed


def _to_decimal(value, places="0.00"):
    if value in (None, ""):
        return Decimal(places)
    try:
        return Decimal(str(value)).quantize(Decimal(places))
    except (InvalidOperation, ValueError):
        return Decimal(places)


class Command(BaseCommand):
    help = "Importa dados legados do SQLite local para o PostgreSQL configurado no projeto."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sqlite-file",
            default="db.sqlite3",
            help="Caminho do banco SQLite de origem.",
        )

    def handle(self, *args, **options):
        if connection.vendor != "postgresql":
            raise CommandError("O banco ativo precisa ser PostgreSQL para executar esta importacao.")

        sqlite_path = Path(options["sqlite_file"]).resolve()
        if not sqlite_path.exists():
            raise CommandError(f"Banco SQLite nao encontrado: {sqlite_path}")

        source = sqlite3.connect(sqlite_path)
        source.row_factory = sqlite3.Row
        user_model = get_user_model()

        counts = ImportCounts()
        ptm_rows = []

        try:
            with transaction.atomic():
                counts.user = self._import_users(source, user_model)
                counts.tipo_fem = self._import_catalog(source, "core_tipofem", TipoFEM)
                counts.status_ptm = self._import_catalog(source, "core_statusptm", StatusPTM)
                counts.status_obra = self._import_catalog(source, "core_statusobra", StatusObra)
                counts.status_analise_documentacao = self._import_catalog(
                    source, "core_statusanalisedocumentacao", StatusAnaliseDocumentacao
                )
                counts.area_investimento = self._import_catalog(
                    source, "core_areainvestimento", AreaInvestimento
                )
                counts.secretaria = self._import_catalog(source, "core_secretaria", Secretaria)
                counts.municipio = self._import_catalog(source, "core_municipio", Municipio)
                counts.user_municipio = self._import_user_municipios(source)

                ptm_rows = self._fetch_rows(source, "ptms_ptm")
                counts.ptm = self._import_ptms(ptm_rows)
                counts.documento_publico = self._import_documentos_publicos(
                    self._fetch_rows(source, "ptms_documentopublicoptm")
                )
                counts.evento = self._import_eventos(self._fetch_rows(source, "eventos_eventoptm"))
                counts.pagamento = self._import_pagamentos(
                    self._fetch_rows(source, "pagamentos_pagamentoptm")
                )
                counts.vistoria = self._import_vistorias(
                    self._fetch_rows(source, "vistorias_vistoriaptm")
                )
                counts.prestacao = self._import_prestacoes(
                    self._fetch_rows(source, "prestacao_contas_prestacaocontaptm")
                )
                counts.prestacao_historico = self._import_prestacao_historico(
                    self._fetch_rows(source, "prestacao_contas_prestacaocontahistorico")
                )
                counts.observacao = self._import_observacoes(
                    self._fetch_rows(source, "observacoes_observacaoencaminhamentoptm")
                )
                counts.conclusao = self._import_conclusoes(
                    self._fetch_rows(source, "conclusao_informal_conclusaoinformalptm")
                )
                counts.admin_log = self._import_admin_logs(
                    self._fetch_rows(source, "django_admin_log")
                )

                self._reset_sequences(
                    [
                        user_model,
                        TipoFEM,
                        StatusPTM,
                        StatusObra,
                        StatusAnaliseDocumentacao,
                        AreaInvestimento,
                        Secretaria,
                        Municipio,
                        UserMunicipio,
                        PTM,
                        DocumentoPublicoPTM,
                        EventoPTM,
                        PagamentoPTM,
                        VistoriaPTM,
                        PrestacaoContaPTM,
                        PrestacaoContaHistorico,
                        ObservacaoEncaminhamentoPTM,
                        ConclusaoInformalPTM,
                        LogEntry,
                    ]
                )
        finally:
            source.close()

        self.stdout.write(self.style.SUCCESS("Importacao SQLite -> PostgreSQL concluida."))
        self.stdout.write(
            "Registros importados: "
            f"user={counts.user}, tipo_fem={counts.tipo_fem}, status_ptm={counts.status_ptm}, "
            f"status_obra={counts.status_obra}, status_analise_documentacao={counts.status_analise_documentacao}, "
            f"area_investimento={counts.area_investimento}, secretaria={counts.secretaria}, "
            f"municipio={counts.municipio}, user_municipio={counts.user_municipio}, ptm={counts.ptm}, "
            f"documento_publico={counts.documento_publico}, evento={counts.evento}, pagamento={counts.pagamento}, "
            f"vistoria={counts.vistoria}, prestacao={counts.prestacao}, "
            f"prestacao_historico={counts.prestacao_historico}, observacao={counts.observacao}, "
            f"conclusao={counts.conclusao}, admin_log={counts.admin_log}"
        )

    def _table_exists(self, source, table_name):
        cursor = source.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?",
            [table_name],
        )
        return cursor.fetchone() is not None

    def _fetch_rows(self, source, table_name):
        if not self._table_exists(source, table_name):
            self.stdout.write(self.style.WARNING(f"Tabela ausente no SQLite, ignorando: {table_name}"))
            return []
        cursor = source.execute(f"SELECT * FROM {table_name} ORDER BY id")
        return cursor.fetchall()

    def _import_catalog(self, source, table_name, model):
        rows = self._fetch_rows(source, table_name)
        model.objects.bulk_create(
            [
                model(
                    id=row["id"],
                    nome=row["nome"],
                    ativo=bool(row["ativo"]),
                    created_at=_to_datetime(row["created_at"]),
                    updated_at=_to_datetime(row["updated_at"]),
                )
                for row in rows
            ],
            batch_size=1000,
        )
        return len(rows)

    def _import_users(self, source, user_model):
        rows = self._fetch_rows(source, "auth_user")
        user_model.objects.bulk_create(
            [
                user_model(
                    id=row["id"],
                    password=row["password"],
                    last_login=_to_datetime(row["last_login"]),
                    is_superuser=bool(row["is_superuser"]),
                    username=row["username"],
                    last_name=row["last_name"] or "",
                    email=row["email"] or "",
                    is_staff=bool(row["is_staff"]),
                    is_active=bool(row["is_active"]),
                    date_joined=_to_datetime(row["date_joined"]),
                    first_name=row["first_name"] or "",
                )
                for row in rows
            ],
            batch_size=1000,
        )
        return len(rows)

    def _import_ptms(self, rows):
        PTM.objects.bulk_create(
            [
                PTM(
                    id=row["id"],
                    ordem=row["ordem"],
                    regiao=row["regiao"] or "",
                    municipio=row["municipio"] or "",
                    projeto=row["projeto"] or "",
                    projeto_detalhado=row["projeto_detalhado"] or "",
                    data_final=_to_date(row["data_final"]),
                    data_aprovacao=_to_date(row["data_aprovacao"]),
                    teto_fem=_to_decimal(row["teto_fem"]),
                    investimento_total=_to_decimal(row["investimento_total"]),
                    recurso_fem=_to_decimal(row["recurso_fem"]),
                    rendimentos_fem=_to_decimal(row["rendimentos_fem"]),
                    contrapartida=_to_decimal(row["contrapartida"]),
                    ressalva=row["ressalva"] or "",
                    conta_ptm=row["conta_ptm"] or "",
                    descricao=row["descricao"] or "",
                    populacao_beneficiada=row["populacao_beneficiada"],
                    area_investimento_id=row["area_investimento_id"],
                    secretaria_id=row["secretaria_id"],
                    status_obra_atual_id=row["status_obra_atual_id"],
                    status_ptm_atual_id=row["status_ptm_atual_id"],
                    tipo_fem_id=row["tipo_fem_id"],
                    codigo_acesso_publico=None,
                    status_analise_documentacao_id=None,
                    created_at=_to_datetime(row["created_at"]),
                    updated_at=_to_datetime(row["updated_at"]),
                )
                for row in rows
            ],
            batch_size=1000,
        )
        return len(rows)

    def _import_user_municipios(self, source):
        rows = self._fetch_rows(source, "core_usermunicipio")
        UserMunicipio.objects.bulk_create(
            [
                UserMunicipio(
                    id=row["id"],
                    municipio_id=row["municipio_id"],
                    user_id=row["user_id"],
                    created_at=_to_datetime(row["created_at"]),
                    updated_at=_to_datetime(row["updated_at"]),
                )
                for row in rows
            ],
            batch_size=1000,
        )
        return len(rows)

    def _import_documentos_publicos(self, rows):
        DocumentoPublicoPTM.objects.bulk_create(
            [
                DocumentoPublicoPTM(
                    id=row["id"],
                    nome_remetente=row["nome_remetente"] or "",
                    contato=row["contato"] or "",
                    descricao=row["descricao"] or "",
                    arquivo=row["arquivo"] or "",
                    ptm_id=row["ptm_id"],
                    created_at=_to_datetime(row["created_at"]),
                    updated_at=_to_datetime(row["updated_at"]),
                )
                for row in rows
            ],
            batch_size=1000,
        )
        return len(rows)

    def _import_eventos(self, rows):
        EventoPTM.objects.bulk_create(
            [
                EventoPTM(
                    id=row["id"],
                    data_evento=_to_date(row["data_evento"]),
                    descricao=row["descricao"] or "",
                    ptm_id=row["ptm_id"],
                    status_obra_id=row["status_obra_id"],
                    status_ptm_id=row["status_ptm_id"],
                    created_at=_to_datetime(row["created_at"]),
                    updated_at=_to_datetime(row["updated_at"]),
                )
                for row in rows
            ],
            batch_size=1000,
        )
        return len(rows)

    def _import_pagamentos(self, rows):
        PagamentoPTM.objects.bulk_create(
            [
                PagamentoPTM(
                    id=row["id"],
                    parcela=str(row["parcela"] or ""),
                    tipo_registro=row["tipo_registro"] or "normal",
                    dt_solicitacao=_to_date(row["dt_solicitacao"]),
                    dt_envio_pg=_to_date(row["dt_envio_pg"]),
                    dt_pagamento=_to_date(row["dt_pagamento"]),
                    valor_previsto=_to_decimal(row["valor_previsto"]),
                    valor_realizado=_to_decimal(row["valor_realizado"]),
                    numero_ob=row["numero_ob"] or "",
                    numero_empenho=row["numero_empenho"] or "",
                    observacao=row["observacao"] or "",
                    ptm_id=row["ptm_id"],
                    created_at=_to_datetime(row["created_at"]),
                    updated_at=_to_datetime(row["updated_at"]),
                )
                for row in rows
            ],
            batch_size=1000,
        )
        return len(rows)

    def _import_vistorias(self, rows):
        ordem_por_ptm = defaultdict(int)
        objects = []
        for row in rows:
            ordem_por_ptm[row["ptm_id"]] += 1
            objects.append(
                VistoriaPTM(
                    id=row["id"],
                    ordem_vistoria=ordem_por_ptm[row["ptm_id"]],
                    dt_solicitacao=_to_date(row["dt_solicitacao"]),
                    dt_resposta=_to_date(row["dt_resposta"]),
                    percentual_execucao=_to_decimal(row["percentual_execucao"], "0.0000"),
                    observacao=row["observacao"] or "",
                    ptm_id=row["ptm_id"],
                    created_at=_to_datetime(row["created_at"]),
                    updated_at=_to_datetime(row["updated_at"]),
                )
            )
        VistoriaPTM.objects.bulk_create(objects, batch_size=1000)
        return len(rows)

    def _import_prestacoes(self, rows):
        PrestacaoContaPTM.objects.bulk_create(
            [
                PrestacaoContaPTM(
                    id=row["id"],
                    prazo_contas=_to_date(row["prazo_contas"]),
                    data_prestacao=_to_date(row["data_prestacao"]),
                    situacao=row["situacao"] or "",
                    ptm_id=row["ptm_id"],
                    created_at=_to_datetime(row["created_at"]),
                    updated_at=_to_datetime(row["updated_at"]),
                )
                for row in rows
            ],
            batch_size=1000,
        )
        return len(rows)

    def _import_prestacao_historico(self, rows):
        PrestacaoContaHistorico.objects.bulk_create(
            [
                PrestacaoContaHistorico(
                    id=row["id"],
                    data=_to_date(row["data"]),
                    observacao=row["observacao"] or "",
                    prestacao_id=row["prestacao_id"],
                    created_at=_to_datetime(row["created_at"]),
                    updated_at=_to_datetime(row["updated_at"]),
                )
                for row in rows
            ],
            batch_size=1000,
        )
        return len(rows)

    def _import_observacoes(self, rows):
        ObservacaoEncaminhamentoPTM.objects.bulk_create(
            [
                ObservacaoEncaminhamentoPTM(
                    id=row["id"],
                    data=_to_date(row["data"]),
                    observacao=row["observacao"] or "",
                    origem=row["origem"] or "",
                    ptm_id=row["ptm_id"],
                    created_at=_to_datetime(row["created_at"]),
                    updated_at=_to_datetime(row["updated_at"]),
                )
                for row in rows
            ],
            batch_size=1000,
        )
        return len(rows)

    def _import_conclusoes(self, rows):
        ConclusaoInformalPTM.objects.bulk_create(
            [
                ConclusaoInformalPTM(
                    id=row["id"],
                    data=_to_date(row["data"]),
                    contato=row["contato"] or "",
                    observacao=row["observacao"] or "",
                    percentual_declarado=_to_decimal(row["percentual_declarado"], "0.0000"),
                    ptm_id=row["ptm_id"],
                    created_at=_to_datetime(row["created_at"]),
                    updated_at=_to_datetime(row["updated_at"]),
                )
                for row in rows
            ],
            batch_size=1000,
        )
        return len(rows)

    def _import_admin_logs(self, rows):
        LogEntry.objects.bulk_create(
            [
                LogEntry(
                    id=row["id"],
                    object_id=row["object_id"],
                    object_repr=row["object_repr"] or "",
                    action_flag=row["action_flag"],
                    change_message=row["change_message"] or "",
                    content_type_id=row["content_type_id"],
                    user_id=row["user_id"],
                    action_time=_to_datetime(row["action_time"]),
                )
                for row in rows
            ],
            batch_size=1000,
        )
        return len(rows)

    def _reset_sequences(self, models):
        statements = connection.ops.sequence_reset_sql(no_style(), models)
        if not statements:
            return
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
