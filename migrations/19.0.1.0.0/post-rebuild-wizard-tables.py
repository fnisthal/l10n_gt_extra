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
    missing_models = []

    for model_name in _WIZARD_MODELS:
        try:
            model = env[model_name]
        except KeyError:
            _logger.warning("No se encontró el modelo %s durante post-migración", model_name)
            continue

        if not _table_exists(cr, model._table):
            missing_models.append(model_name)

    if not missing_models:
        _logger.info("Todas las tablas de wizards ya existen")
        return

    _logger.warning("Se reconstruyen tablas faltantes para: %s", ", ".join(missing_models))
    env.registry.init_models(cr, missing_models, {"module": "l10n_gt_extra"}, new_install=False)

    for model_name in missing_models:
        model = env[model_name]
        if _table_exists(cr, model._table):
            continue

        _logger.warning("init_models no creó %s; se intenta _auto_init()", model._table)
        model._auto_init()