import logging


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
    """Verifica si una tabla existe"""
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
    """
    Script de post-migración que verifica que todas las tablas wizard existan.
    
    Las tablas deben haber sido creadas por 00-create-wizard-tables.py en la fase pre-migration.
    Este script solo verifica el estado final.
    """
    _logger.info("Verificando tablas wizard después de ORM init...")
    
    all_exist = True
    for model_name in _WIZARD_MODELS:
        # Convertir nombre de modelo a nombre de tabla
        # l10n_gt_extra.reporte_banco.wizard → l10n_gt_extra_reporte_banco_wizard
        table_name = model_name.replace('.', '_')
        
        if _table_exists(cr, table_name):
            _logger.info("✓ Tabla existe: %s", table_name)
        else:
            _logger.error("✗ Tabla FALTA: %s (debería haber sido creada por pre-migration)", table_name)
            all_exist = False
    
    if all_exist:
        _logger.info("✓ Todas las tablas wizard existen correctamente")
    else:
        _logger.error("✗ Algunas tablas wizard no existen. Revisa el log de pre-migration.")