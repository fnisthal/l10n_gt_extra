"""
Pre-migration 19.0.2.0: crea tablas de wizards transitorios si no existen.
Se ejecuta antes de que el ORM procese los modelos.
"""
import logging

_logger = logging.getLogger(__name__)


def _table_exists(cr, table_name):
    cr.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s",
        (table_name,),
    )
    return bool(cr.fetchone())


def _column_exists(cr, table_name, column_name):
    cr.execute(
        "SELECT 1 FROM information_schema.columns WHERE table_name = %s AND column_name = %s",
        (table_name, column_name),
    )
    return bool(cr.fetchone())


def _ensure_column(cr, table, col, col_type):
    if not _column_exists(cr, table, col):
        cr.execute(f'ALTER TABLE "{table}" ADD COLUMN "{col}" {col_type}')
        _logger.info("Columna agregada: %s.%s", table, col)


def _create_base_table(cr, table):
    cr.execute(f"""
        CREATE TABLE "{table}" (
            id SERIAL PRIMARY KEY,
            create_uid INTEGER,
            create_date TIMESTAMP WITHOUT TIME ZONE,
            write_uid INTEGER,
            write_date TIMESTAMP WITHOUT TIME ZONE
        )
    """)
    _logger.info("Tabla creada: %s", table)


def migrate(cr, version):
    _logger.info("pre-create-wizard-tables 19.0.2.0: inicio")

    wizard_tables = [
        "l10n_gt_extra_reporte_banco_wizard",
        "l10n_gt_extra_reporte_compras_wizard",
        "l10n_gt_extra_reporte_diario_wizard",
        "l10n_gt_extra_reporte_inventario_wizard",
        "l10n_gt_extra_reporte_mayor_wizard",
        "l10n_gt_extra_reporte_ventas_wizard",
    ]

    for table in wizard_tables:
        if not _table_exists(cr, table):
            _create_base_table(cr, table)

    _logger.info("pre-create-wizard-tables 19.0.2.0: completado")
