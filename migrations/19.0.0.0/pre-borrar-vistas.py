import logging
import re

_logger = logging.getLogger(__name__)


def _delete_xmlid_target(cr, xmlid):
    module, name = xmlid.split(".", 1)
    cr.execute(
        """
        SELECT model, res_id
        FROM ir_model_data
        WHERE module = %s
          AND name = %s
        """,
        (module, name),
    )
    row = cr.fetchone()
    if not row:
        return

    model, res_id = row
    table_name = model.replace(".", "_")
    if re.match(r"^[a-z0-9_]+$", table_name):
        cr.execute(f'DELETE FROM "{table_name}" WHERE id = %s', (res_id,))

    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE module = %s
          AND name = %s
        """,
        (module, name),
    )


def migrate(cr, version):
    xmlids_to_remove = [
        "l10n_gt_extra.asistente_reporte_banco",
        "l10n_gt_extra.window_reporte_banco",
        "l10n_gt_extra.action_reporte_banco",
        "l10n_gt_extra.menu_asistente_reporte_banco",
        "l10n_gt_extra.asistente_compras_reporte",
        "l10n_gt_extra.window_reporte_compras",
        "l10n_gt_extra.action_reporte_compras",
        "l10n_gt_extra.menu_asistente_reporte_compras",
        "l10n_gt_extra.asistente_reporte_diario",
        "l10n_gt_extra.window_reporte_diario",
        "l10n_gt_extra.action_reporte_diario",
        "l10n_gt_extra.menu_asistente_reporte_diario",
        "l10n_gt_extra.asistente_reporte_inventario",
        "l10n_gt_extra.window_reporte_inventario",
        "l10n_gt_extra.action_reporte_inventario",
        "l10n_gt_extra.menu_asistente_reporte_inventario",
        "l10n_gt_extra.asistente_reporte_mayor",
        "l10n_gt_extra.window_reporte_mayor",
        "l10n_gt_extra.action_reporte_mayor",
        "l10n_gt_extra.menu_asistente_reporte_mayor",
        "l10n_gt_extra.asistente_ventas_reporte",
        "l10n_gt_extra.window_reporte_ventas",
        "l10n_gt_extra.action_reporte_ventas",
        "l10n_gt_extra.menu_asistente_reporte_ventas",
    ]

    for xmlid in xmlids_to_remove:
        _delete_xmlid_target(cr, xmlid)

    _logger.info("Vistas viejas borradas")
