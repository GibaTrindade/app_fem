from __future__ import annotations

import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection, transaction
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from conclusao_informal.models import ConclusaoInformalPTM
from core.models import AreaInvestimento, Secretaria, StatusObra, StatusPTM, TipoFEM
from eventos.models import EventoPTM
from observacoes.models import ObservacaoEncaminhamentoPTM
from pagamentos.models import PagamentoPTM
from prestacao_contas.models import PrestacaoContaHistorico, PrestacaoContaPTM
from ptms.models import PTM
from vistorias.models import VistoriaPTM


@dataclass
class ImportCounts:
    tipo_fem: int = 0
    status_ptm: int = 0
    status_obra: int = 0
    area_investimento: int = 0
    secretaria: int = 0
    ptm: int = 0
    evento: int = 0
    pagamento: int = 0
    vistoria: int = 0
    prestacao: int = 0
    prestacao_historico: int = 0
    observacao: int = 0
    conclusao: int = 0


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

        counts = ImportCounts()
        ptm_rows = []

        try:
            with transaction.atomic():
                counts.tipo_fem = self._import_catalog(source, "core_tipofem", TipoFEM)
                counts.status_ptm = self._import_catalog(source, "core_statusptm", StatusPTM)
                counts.status_obra = self._import_catalog(source, "core_statusobra", StatusObra)
                counts.area_investimento = self._import_catalog(
                    source, "core_areainvestimento", AreaInvestimento
                )
                counts.secretaria = self._import_catalog(source, "core_secretaria", Secretaria)

                ptm_rows = self._fetch_rows(source, "ptms_ptm")
                counts.ptm = self._import_ptms(ptm_rows)
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

                self._reset_sequences(
                    [
                        TipoFEM,
                        StatusPTM,
                        StatusObra,
                        AreaInvestimento,
                        Secretaria,
                        PTM,
                        EventoPTM,
                        PagamentoPTM,
                        VistoriaPTM,
                        PrestacaoContaPTM,
                        PrestacaoContaHistorico,
                        ObservacaoEncaminhamentoPTM,
                        ConclusaoInformalPTM,
                    ]
                )
        finally:
            source.close()

        self.stdout.write(self.style.SUCCESS("Importacao SQLite -> PostgreSQL concluida."))
        self.stdout.write(
            "Registros importados: "
            f"tipo_fem={counts.tipo_fem}, status_ptm={counts.status_ptm}, "
            f"status_obra={counts.status_obra}, area_investimento={counts.area_investimento}, "
            f"secretaria={counts.secretaria}, ptm={counts.ptm}, evento={counts.evento}, "
            f"pagamento={counts.pagamento}, vistoria={counts.vistoria}, prestacao={counts.prestacao}, "
            f"prestacao_historico={counts.prestacao_historico}, observacao={counts.observacao}, "
            f"conclusao={counts.conclusao}"
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

    def _reset_sequences(self, models):
        statements = connection.ops.sequence_reset_sql(no_style(), models)
        if not statements:
            return
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
