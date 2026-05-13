import logging

from odoo import SUPERUSER_ID, api


_logger = logging.getLogger(__name__)

_WIZARD_MODELS = [
    "l10n_gt_extra.reporte_banco.wizard",
    "l10n_gt_extra.reporte_compras.wizard",
    "l10n_gt_extra.reporte_diario.wizard",
    "l10n_gt_extra.reporte_inventario.wizard",
    "l10n_gt_extra.reporte_mayor.wizard",
    "l10n_gt_extra.reporte_ventas.wizard",
]


def _table_exists(cr, table_name):
    cr.execute(
        """
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = %s
        """,
        (table_name,),
    )
    return bool(cr.fetchone())


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    for model_name in _WIZARD_MODELS:
        try:
            model = env[model_name]
        except KeyError:
            _logger.warning("No se encontró el modelo %s durante post-migración", model_name)
            continue

        if _table_exists(cr, model._table):
            continue

        _logger.warning(
            "Tabla %s ausente para %s; se ejecuta _auto_init()",
            model._table,
            model_name,
        )
        model._auto_init()