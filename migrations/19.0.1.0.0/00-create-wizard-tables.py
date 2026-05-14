"""
Pre-migration script para crear tablas de wizards transitorios antes de que
el ORM intente cargarlos. Se ejecuta ANTES que los otros scripts pre-migration.

Esto resuelve el error: relation "l10n_gt_extra_reporte_*_wizard" does not exist
"""
import logging


_logger = logging.getLogger(__name__)


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


def _column_exists(cr, table_name, column_name):
    """Verifica si una columna existe en la tabla"""
    cr.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = %s AND column_name = %s
        """,
        (table_name, column_name),
    )
    return bool(cr.fetchone())


def _ensure_column(cr, table_name, column_name, column_type, nullable=True):
    """Agrega una columna si no existe"""
    if _column_exists(cr, table_name, column_name):
        return
    
    null_constraint = "NULL" if nullable else "NOT NULL"
    try:
        cr.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_type} {null_constraint}')
        _logger.info(f"Columna agregada: {table_name}.{column_name}")
    except Exception as e:
        _logger.warning(f"Error al agregar {table_name}.{column_name}: {e}")


def _create_reporte_banco_wizard(cr):
    """Crea tabla para l10n_gt_extra.reporte_banco.wizard"""
    table_name = "l10n_gt_extra_reporte_banco_wizard"
    
    if _table_exists(cr, table_name):
        return
    
    cr.execute(f"""
        CREATE TABLE "{table_name}" (
            id serial primary key,
            create_uid integer,
            create_date timestamp,
            write_uid integer,
            write_date timestamp,
            __last_update timestamp
        )
    """)
    _logger.info(f"Tabla creada: {table_name}")
    
    # Agregar campos específicos
    _ensure_column(cr, table_name, "cuenta_bancaria_id", "integer", nullable=False)
    _ensure_column(cr, table_name, "fecha_desde", "date", nullable=False)
    _ensure_column(cr, table_name, "fecha_hasta", "date", nullable=False)
    _ensure_column(cr, table_name, "name", "varchar")
    _ensure_column(cr, table_name, "archivo", "bytea")


def _create_reporte_compras_wizard(cr):
    """Crea tabla para l10n_gt_extra.reporte_compras.wizard"""
    table_name = "l10n_gt_extra_reporte_compras_wizard"
    
    if _table_exists(cr, table_name):
        return
    
    cr.execute(f"""
        CREATE TABLE "{table_name}" (
            id serial primary key,
            create_uid integer,
            create_date timestamp,
            write_uid integer,
            write_date timestamp,
            __last_update timestamp
        )
    """)
    _logger.info(f"Tabla creada: {table_name}")
    
    # Agregar campos específicos
    _ensure_column(cr, table_name, "folio_inicial", "integer", nullable=False)
    _ensure_column(cr, table_name, "fecha_desde", "date", nullable=False)
    _ensure_column(cr, table_name, "fecha_hasta", "date", nullable=False)
    _ensure_column(cr, table_name, "name", "varchar")
    _ensure_column(cr, table_name, "archivo", "bytea")
    
    # Tablas de relación many2many
    _create_m2m_table(cr, table_name, "diarios_id", "account_journal")
    _create_m2m_table(cr, table_name, "impuestos_id", "account_tax")


def _create_reporte_diario_wizard(cr):
    """Crea tabla para l10n_gt_extra.reporte_diario.wizard"""
    table_name = "l10n_gt_extra_reporte_diario_wizard"
    
    if _table_exists(cr, table_name):
        return
    
    cr.execute(f"""
        CREATE TABLE "{table_name}" (
            id serial primary key,
            create_uid integer,
            create_date timestamp,
            write_uid integer,
            write_date timestamp,
            __last_update timestamp
        )
    """)
    _logger.info(f"Tabla creada: {table_name}")
    
    # Agregar campos específicos
    _ensure_column(cr, table_name, "folio_inicial", "integer", nullable=False)
    _ensure_column(cr, table_name, "agrupado_por_dia", "boolean")
    _ensure_column(cr, table_name, "fecha_desde", "date", nullable=False)
    _ensure_column(cr, table_name, "fecha_hasta", "date", nullable=False)
    _ensure_column(cr, table_name, "name", "varchar")
    _ensure_column(cr, table_name, "archivo", "bytea")
    
    # Tabla de relación many2many
    _create_m2m_table(cr, table_name, "cuentas_id", "account_account")


def _create_reporte_inventario_wizard(cr):
    """Crea tabla para l10n_gt_extra.reporte_inventario.wizard"""
    table_name = "l10n_gt_extra_reporte_inventario_wizard"
    
    if _table_exists(cr, table_name):
        return
    
    cr.execute(f"""
        CREATE TABLE "{table_name}" (
            id serial primary key,
            create_uid integer,
            create_date timestamp,
            write_uid integer,
            write_date timestamp,
            __last_update timestamp
        )
    """)
    _logger.info(f"Tabla creada: {table_name}")
    
    # Agregar campos específicos
    _ensure_column(cr, table_name, "folio_inicial", "integer", nullable=False)
    _ensure_column(cr, table_name, "fecha_hasta", "date", nullable=False)
    
    # Tabla de relación many2many
    _create_m2m_table(cr, table_name, "cuentas_id", "account_account")


def _create_reporte_mayor_wizard(cr):
    """Crea tabla para l10n_gt_extra.reporte_mayor.wizard"""
    table_name = "l10n_gt_extra_reporte_mayor_wizard"
    
    if _table_exists(cr, table_name):
        return
    
    cr.execute(f"""
        CREATE TABLE "{table_name}" (
            id serial primary key,
            create_uid integer,
            create_date timestamp,
            write_uid integer,
            write_date timestamp,
            __last_update timestamp
        )
    """)
    _logger.info(f"Tabla creada: {table_name}")
    
    # Agregar campos específicos
    _ensure_column(cr, table_name, "folio_inicial", "integer", nullable=False)
    _ensure_column(cr, table_name, "agrupado_por_dia", "boolean")
    _ensure_column(cr, table_name, "fecha_desde", "date", nullable=False)
    _ensure_column(cr, table_name, "fecha_hasta", "date", nullable=False)
    _ensure_column(cr, table_name, "name", "varchar")
    _ensure_column(cr, table_name, "archivo", "bytea")
    
    # Tabla de relación many2many
    _create_m2m_table(cr, table_name, "cuentas_id", "account_account")


def _create_reporte_ventas_wizard(cr):
    """Crea tabla para l10n_gt_extra.reporte_ventas.wizard"""
    table_name = "l10n_gt_extra_reporte_ventas_wizard"
    
    if _table_exists(cr, table_name):
        return
    
    cr.execute(f"""
        CREATE TABLE "{table_name}" (
            id serial primary key,
            create_uid integer,
            create_date timestamp,
            write_uid integer,
            write_date timestamp,
            __last_update timestamp
        )
    """)
    _logger.info(f"Tabla creada: {table_name}")
    
    # Agregar campos específicos
    _ensure_column(cr, table_name, "folio_inicial", "integer", nullable=False)
    _ensure_column(cr, table_name, "resumido", "boolean")
    _ensure_column(cr, table_name, "fecha_desde", "date", nullable=False)
    _ensure_column(cr, table_name, "fecha_hasta", "date", nullable=False)
    _ensure_column(cr, table_name, "name", "varchar")
    _ensure_column(cr, table_name, "archivo", "bytea")
    
    # Tablas de relación many2many
    _create_m2m_table(cr, table_name, "diarios_id", "account_journal")
    _create_m2m_table(cr, table_name, "impuestos_id", "account_tax")


def _create_m2m_table(cr, model_table, field_name, rel_model):
    """Crea tabla de relación many2many"""
    m2m_table = f"{model_table}_{field_name}"
    rel_table = rel_model.replace('.', '_')
    
    if _table_exists(cr, m2m_table):
        return
    
    try:
        cr.execute(f"""
            CREATE TABLE "{m2m_table}" (
                id serial primary key,
                "{model_table}_id" integer NOT NULL REFERENCES "{model_table}"(id) ON DELETE CASCADE,
                "{rel_table}_id" integer NOT NULL,
                create_uid integer,
                create_date timestamp
            )
        """)
        _logger.info(f"Tabla many2many creada: {m2m_table}")
    except Exception as e:
        _logger.warning(f"Error creando {m2m_table}: {e}")


def migrate(cr, version):
    """Script de pre-migración que crea todas las tablas wizard"""
    _logger.info("Iniciando creación de tablas wizard...")
    
    try:
        _create_reporte_banco_wizard(cr)
        _create_reporte_compras_wizard(cr)
        _create_reporte_diario_wizard(cr)
        _create_reporte_inventario_wizard(cr)
        _create_reporte_mayor_wizard(cr)
        _create_reporte_ventas_wizard(cr)
        
        _logger.info("Tablas wizard creadas exitosamente")
    except Exception as e:
        _logger.error(f"Error creando tablas wizard: {e}")
        raise
