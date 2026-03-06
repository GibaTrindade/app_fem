from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
import unicodedata

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from conclusao_informal.models import ConclusaoInformalPTM
from core.models import AreaInvestimento, Secretaria, StatusObra, StatusPTM, TipoFEM
from eventos.models import EventoPTM
from observacoes.models import ObservacaoEncaminhamentoPTM
from pagamentos.models import PagamentoPTM
from prestacao_contas.models import PrestacaoContaHistorico, PrestacaoContaPTM
from ptms.models import PTM
from vistorias.models import VistoriaPTM


def _norm(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).strip().lower()


def _sheet_by_name(workbook, expected: str) -> Worksheet:
    expected_norm = _norm(expected)
    for ws in workbook.worksheets:
        if _norm(ws.title) == expected_norm:
            return ws
    raise CommandError(f"Aba '{expected}' nao encontrada no arquivo.")


def _to_str(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _to_date(value) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def _to_decimal(value) -> Decimal:
    if value in (None, ""):
        return Decimal("0.00")
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value)).quantize(Decimal("0.01"))
    try:
        clean = str(value).strip()
        if "," in clean and "." in clean and clean.rfind(",") > clean.rfind("."):
            clean = clean.replace(".", "").replace(",", ".")
        else:
            clean = clean.replace(",", ".")
        return Decimal(clean).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return Decimal("0.00")


def _to_percentage(value) -> Decimal:
    if value in (None, ""):
        return Decimal("0.0000")
    try:
        return Decimal(str(value)).quantize(Decimal("0.0001"))
    except (InvalidOperation, ValueError):
        return Decimal("0.0000")


def _iter_ptm_rows(ws: Worksheet):
    for row in range(7, ws.max_row + 1):
        ordem = _to_str(ws[f"B{row}"].value)
        if ordem:
            yield row, ordem


def _get_or_create_nome(model, value: str):
    value = _to_str(value)
    if not value:
        return None
    obj, _ = model.objects.get_or_create(nome=value)
    return obj


@dataclass
class Counters:
    ptms_created: int = 0
    ptms_updated: int = 0
    eventos: int = 0
    pagamentos: int = 0
    vistorias: int = 0
    prestacoes: int = 0
    prestacao_historico: int = 0
    observacoes: int = 0
    conclusoes: int = 0


class Command(BaseCommand):
    help = "Importa a planilha FEM XLSM para o banco SQLite."

    def add_arguments(self, parser):
        parser.add_argument("--file", required=True, help="Caminho da planilha .xlsm")
        parser.add_argument("--limit", type=int, default=0, help="Limita quantidade de PTMs importados (teste)")

    def handle(self, *args, **options):
        file_path = Path(options["file"])
        if not file_path.exists():
            raise CommandError(f"Arquivo nao encontrado: {file_path}")

        limit = max(0, int(options["limit"] or 0))
        wb = load_workbook(file_path, data_only=True, keep_vba=True)
        ws_apoio = _sheet_by_name(wb, "APOIO")
        ws_inf = _sheet_by_name(wb, "INF GERAIS")
        ws_eventos = _sheet_by_name(wb, "EVENTOS")
        ws_pagamentos = _sheet_by_name(wb, "PAGAMENTOS")
        ws_vistorias = _sheet_by_name(wb, "VISTORIA")
        ws_prestacao = _sheet_by_name(wb, "PRESTAÇÃO DE CONTAS")
        ws_obs = _sheet_by_name(wb, "OBS  ENC")
        ws_conclusao = _sheet_by_name(wb, "CONCLUSÃO INFORMAL")

        counters = Counters()
        self._seed_catalogs(ws_apoio)

        processed = 0
        for row, ordem in _iter_ptm_rows(ws_inf):
            if limit and processed >= limit:
                break
            with transaction.atomic():
                ptm, created = self._upsert_ptm(ws_inf, row, ordem)
                if created:
                    counters.ptms_created += 1
                else:
                    counters.ptms_updated += 1

                ptm.eventos.all().delete()
                ptm.pagamentos.all().delete()
                ptm.vistorias.all().delete()
                ptm.observacoes_enc.all().delete()
                ptm.conclusoes_informais.all().delete()
                PrestacaoContaPTM.objects.filter(ptm=ptm).delete()

                counters.eventos += self._import_eventos(ws_eventos, row, ptm)
                counters.pagamentos += self._import_pagamentos(ws_pagamentos, row, ptm)
                counters.vistorias += self._import_vistorias(ws_vistorias, row, ptm)
                p_count, ph_count = self._import_prestacao(ws_prestacao, row, ptm)
                counters.prestacoes += p_count
                counters.prestacao_historico += ph_count
                counters.observacoes += self._import_observacoes(ws_obs, row, ptm)
                counters.conclusoes += self._import_conclusoes(ws_conclusao, row, ptm)
            processed += 1
            if processed % 25 == 0:
                self.stdout.write(f"Processados {processed} PTMs...")

        self.stdout.write(self.style.SUCCESS("Importacao concluida."))
        self.stdout.write(
            f"PTMs criados: {counters.ptms_created} | atualizados: {counters.ptms_updated}"
        )
        self.stdout.write(
            "Registros: "
            f"eventos={counters.eventos}, pagamentos={counters.pagamentos}, "
            f"vistorias={counters.vistorias}, prestacoes={counters.prestacoes}, "
            f"prestacao_historico={counters.prestacao_historico}, "
            f"obs_enc={counters.observacoes}, conclusoes={counters.conclusoes}"
        )

    def _seed_catalogs(self, ws_apoio: Worksheet):
        for value in ("NORMAL", "MULHER", "EMENDA"):
            TipoFEM.objects.get_or_create(nome=value)

        for row in range(5, 51):
            _get_or_create_nome(StatusPTM, ws_apoio[f"B{row}"].value)
            _get_or_create_nome(StatusObra, ws_apoio[f"C{row}"].value)

        for row in range(5, 2001):
            _get_or_create_nome(AreaInvestimento, ws_apoio[f"AJ{row}"].value)
            _get_or_create_nome(Secretaria, ws_apoio[f"AL{row}"].value)

    def _upsert_ptm(self, ws_inf: Worksheet, row: int, ordem: str):
        tipo_fem = _get_or_create_nome(TipoFEM, ws_inf[f"G{row}"].value)
        status_ptm = _get_or_create_nome(StatusPTM, ws_inf[f"N{row}"].value)
        status_obra = _get_or_create_nome(StatusObra, ws_inf[f"O{row}"].value)
        area = _get_or_create_nome(AreaInvestimento, ws_inf[f"T{row}"].value)
        secretaria = _get_or_create_nome(Secretaria, ws_inf[f"R{row}"].value)

        defaults = {
            "regiao": _to_str(ws_inf[f"C{row}"].value),
            "municipio": _to_str(ws_inf[f"D{row}"].value),
            "projeto": _to_str(ws_inf[f"E{row}"].value),
            "projeto_detalhado": _to_str(ws_inf[f"F{row}"].value),
            "tipo_fem": tipo_fem,
            "status_ptm_atual": status_ptm,
            "status_obra_atual": status_obra,
            "data_final": _to_date(ws_inf[f"H{row}"].value),
            "data_aprovacao": _to_date(ws_inf[f"P{row}"].value),
            "teto_fem": _to_decimal(ws_inf[f"I{row}"].value),
            "investimento_total": _to_decimal(ws_inf[f"J{row}"].value),
            "recurso_fem": _to_decimal(ws_inf[f"K{row}"].value),
            "rendimentos_fem": _to_decimal(ws_inf[f"L{row}"].value),
            "contrapartida": _to_decimal(ws_inf[f"M{row}"].value),
            "ressalva": _to_str(ws_inf[f"Q{row}"].value),
            "secretaria": secretaria,
            "area_investimento": area,
            "conta_ptm": _to_str(ws_inf[f"U{row}"].value),
            "descricao": _to_str(ws_inf[f"AJ{row}"].value),
            "populacao_beneficiada": ws_inf[f"V{row}"].value if isinstance(ws_inf[f"V{row}"].value, int) else None,
        }

        return PTM.objects.update_or_create(ordem=ordem, defaults=defaults)

    def _import_eventos(self, ws: Worksheet, row: int, ptm: PTM) -> int:
        to_create: list[EventoPTM] = []
        latest_status_ptm = None
        latest_status_obra = None
        latest_data = date.min
        col = 7  # G
        while col + 3 <= ws.max_column:
            descricao = _to_str(ws.cell(row=row, column=col).value)
            data_evento = _to_date(ws.cell(row=row, column=col + 1).value)
            status_ptm_nome = _to_str(ws.cell(row=row, column=col + 2).value)
            status_obra_nome = _to_str(ws.cell(row=row, column=col + 3).value)

            if descricao or data_evento or status_ptm_nome or status_obra_nome:
                status_ptm = _get_or_create_nome(StatusPTM, status_ptm_nome)
                status_obra = _get_or_create_nome(StatusObra, status_obra_nome)
                if data_evento and status_ptm and status_obra:
                    to_create.append(
                        EventoPTM(
                            ptm=ptm,
                            data_evento=data_evento,
                            descricao=descricao or "(sem descricao)",
                            status_ptm=status_ptm,
                            status_obra=status_obra,
                        )
                    )
                    if data_evento >= latest_data:
                        latest_data = data_evento
                        latest_status_ptm = status_ptm
                        latest_status_obra = status_obra
            col += 4
        if to_create:
            EventoPTM.objects.bulk_create(to_create, batch_size=200)
            ptm.status_ptm_atual = latest_status_ptm
            ptm.status_obra_atual = latest_status_obra
            ptm.save(update_fields=["status_ptm_atual", "status_obra_atual", "updated_at"])
        return len(to_create)

    def _import_pagamentos(self, ws: Worksheet, row: int, ptm: PTM) -> int:
        created = 0
        normal_blocks = [
            ("1", "I", "J", "K", "L", "M", "N", "O", "P"),
            ("2", "Q", "R", "S", "T", "U", "V", "W", "X"),
            ("3", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF"),
            ("4", "AG", "AH", "AI", "AJ", "AK", "AL", "AM", "AN"),
        ]
        for parcela, c_sol, c_env, c_prev, c_real, c_pg, c_ob, c_emp, c_obs in normal_blocks:
            valor_real = ws[f"{c_real}{row}"].value
            if valor_real in (None, "") and ws[f"{c_pg}{row}"].value in (None, ""):
                continue
            PagamentoPTM.objects.create(
                ptm=ptm,
                parcela=parcela,
                tipo_registro="normal",
                dt_solicitacao=_to_date(ws[f"{c_sol}{row}"].value),
                dt_envio_pg=_to_date(ws[f"{c_env}{row}"].value),
                dt_pagamento=_to_date(ws[f"{c_pg}{row}"].value),
                valor_previsto=_to_decimal(ws[f"{c_prev}{row}"].value),
                valor_realizado=_to_decimal(valor_real),
                numero_ob=_to_str(ws[f"{c_ob}{row}"].value),
                numero_empenho=_to_str(ws[f"{c_emp}{row}"].value),
                observacao=_to_str(ws[f"{c_obs}{row}"].value),
            )
            created += 1

        extra_blocks = [
            ("AO", "AP", "AQ", "AR", "AS", "AT"),
            ("AU", "AV", "AW", "AX", "AY", "AZ"),
        ]
        for c_parcela, c_real, c_pg, c_ob, c_emp, c_obs in extra_blocks:
            parcela_raw = _to_str(ws[f"{c_parcela}{row}"].value)
            if not parcela_raw and ws[f"{c_real}{row}"].value in (None, ""):
                continue
            parcela_num = parcela_raw.replace("ª", "").replace("a", "").strip() or "1"
            if parcela_num not in {"1", "2", "3", "4"}:
                parcela_num = "1"
            PagamentoPTM.objects.create(
                ptm=ptm,
                parcela=parcela_num,
                tipo_registro="extra",
                dt_pagamento=_to_date(ws[f"{c_pg}{row}"].value),
                valor_realizado=_to_decimal(ws[f"{c_real}{row}"].value),
                numero_ob=_to_str(ws[f"{c_ob}{row}"].value),
                numero_empenho=_to_str(ws[f"{c_emp}{row}"].value),
                observacao=_to_str(ws[f"{c_obs}{row}"].value),
            )
            created += 1
        return created

    def _import_vistorias(self, ws: Worksheet, row: int, ptm: PTM) -> int:
        created = 0
        blocks = [
            ("G", "H", "I", "J"),
            ("K", "L", "M", "N"),
            ("O", "P", "Q", "R"),
            ("S", "T", "U", "V"),
            ("W", "X", "Y", "Z"),
        ]
        for c_sol, c_resp, c_pct, c_obs in blocks:
            if ws[f"{c_sol}{row}"].value in (None, "") and ws[f"{c_resp}{row}"].value in (None, ""):
                continue
            VistoriaPTM.objects.create(
                ptm=ptm,
                dt_solicitacao=_to_date(ws[f"{c_sol}{row}"].value),
                dt_resposta=_to_date(ws[f"{c_resp}{row}"].value),
                percentual_execucao=_to_percentage(ws[f"{c_pct}{row}"].value),
                observacao=_to_str(ws[f"{c_obs}{row}"].value),
            )
            created += 1
        return created

    def _import_prestacao(self, ws: Worksheet, row: int, ptm: PTM) -> tuple[int, int]:
        base_has_data = any(
            ws[f"{col}{row}"].value not in (None, "") for col in ("G", "H", "I")
        )
        hist_pairs = [("J", "K"), ("L", "M"), ("N", "O"), ("P", "Q"), ("R", "S"), ("T", "U"), ("V", "W"), ("X", "Y"), ("Z", "AA"), ("AB", "AC"), ("AD", "AE")]
        hist_count = 0

        if not base_has_data and not any(
            ws[f"{obs_col}{row}"].value not in (None, "") for obs_col, _ in hist_pairs
        ):
            return 0, 0

        prestacao = PrestacaoContaPTM.objects.create(
            ptm=ptm,
            prazo_contas=_to_date(ws[f"G{row}"].value),
            data_prestacao=_to_date(ws[f"H{row}"].value),
            situacao=_to_str(ws[f"I{row}"].value),
        )
        for obs_col, data_col in hist_pairs:
            obs = _to_str(ws[f"{obs_col}{row}"].value)
            data_registro = _to_date(ws[f"{data_col}{row}"].value)
            if obs or data_registro:
                PrestacaoContaHistorico.objects.create(
                    prestacao=prestacao,
                    data=data_registro,
                    observacao=obs or "(sem observacao)",
                )
                hist_count += 1
        return 1, hist_count

    def _import_observacoes(self, ws: Worksheet, row: int, ptm: PTM) -> int:
        created = 0
        col = 7  # G
        while col + 1 <= ws.max_column:
            obs = _to_str(ws.cell(row=row, column=col).value)
            data_registro = _to_date(ws.cell(row=row, column=col + 1).value)
            if obs or data_registro:
                ObservacaoEncaminhamentoPTM.objects.create(
                    ptm=ptm,
                    data=data_registro,
                    observacao=obs or "(sem observacao)",
                )
                created += 1
            col += 2
        return created

    def _import_conclusoes(self, ws: Worksheet, row: int, ptm: PTM) -> int:
        created = 0
        blocks = [
            ("G", "H", "I", "J"),
            ("K", "L", "M", "N"),
            ("O", "P", "Q", "R"),
        ]
        for c_pct, c_data, c_contato, c_obs in blocks:
            pct = ws[f"{c_pct}{row}"].value
            data_registro = _to_date(ws[f"{c_data}{row}"].value)
            contato = _to_str(ws[f"{c_contato}{row}"].value)
            obs = _to_str(ws[f"{c_obs}{row}"].value)
            if pct in (None, "") and not data_registro and not contato and not obs:
                continue
            ConclusaoInformalPTM.objects.create(
                ptm=ptm,
                percentual_declarado=_to_percentage(pct),
                data=data_registro,
                contato=contato,
                observacao=obs,
            )
            created += 1
        return created
