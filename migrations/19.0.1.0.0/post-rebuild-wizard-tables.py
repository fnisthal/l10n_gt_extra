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


def _ensure_wizard_table(cr, model):
    """Asegura que la tabla del wizard exista con todas sus columnas"""
    table_name = model._table
    
    # Crear tabla base si no existe
    if not _table_exists(cr, table_name):
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
        _logger.info("Tabla base creada: %s", table_name)
    
    # Agregar campos específicos del modelo
    for field_name, field_obj in model._fields.items():
        if field_name in ('id', 'create_uid', 'create_date', 'write_uid', 'write_date', '__last_update'):
            continue
        
        # Saltar Many2many ya que usan tablas separadas
        if field_obj.type == 'many2many':
            _ensure_m2m_table(cr, model, field_name, field_obj)
            continue
        
        if _column_exists(cr, table_name, field_name):
            continue
        
        # Determinar tipo SQL según el tipo de campo Odoo
        field_type = 'text'  # default
        nullable = 'NULL' if not field_obj.required else 'NOT NULL'
        
        if field_obj.type == 'boolean':
            field_type = 'boolean'
        elif field_obj.type == 'integer':
            field_type = 'integer'
        elif field_obj.type == 'float':
            field_type = 'numeric'
        elif field_obj.type == 'date':
            field_type = 'date'
        elif field_obj.type == 'datetime':
            field_type = 'timestamp'
        elif field_obj.type == 'binary':
            field_type = 'bytea'
        elif field_obj.type == 'many2one':
            field_type = 'integer'
        
        try:
            cr.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{field_name}" {field_type} {nullable}')
            _logger.info("Columna agregada: %s.%s (%s)", table_name, field_name, field_type)
        except Exception as e:
            _logger.warning("Error al agregar columna %s.%s: %s", table_name, field_name, e)


def _ensure_m2m_table(cr, model, field_name, field_obj):
    """Asegura que la tabla many2many exista"""
    # Construir nombre de tabla de relación: {modelo}_{campo}_{rel_model}
    # En Odoo: l10n_gt_extra_reporte_banco_wizard_account_journal_diarios_id
    model_table = model._table
    rel_model_table = field_obj.comodel_name.replace('.', '_')
    
    # Nombre de tabla de relación (según convención Odoo)
    m2m_table = f"{model_table}_{field_name}"
    
    if _table_exists(cr, m2m_table):
        return
    
    try:
        cr.execute(f"""
            CREATE TABLE "{m2m_table}" (
                id serial primary key,
                "{model_table}_id" integer NOT NULL,
                "{rel_model_table}_id" integer NOT NULL,
                create_uid integer,
                create_date timestamp
            )
        """)
        _logger.info("Tabla many2many creada: %s", m2m_table)
    except Exception as e:
        _logger.warning("Error creando tabla many2many %s: %s", m2m_table, e)


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
            missing_models.append((model_name, model))

    if not missing_models:
        _logger.info("Todas las tablas de wizards ya existen")
        return

    _logger.warning("Se reconstruyen %d tablas faltantes de wizards", len(missing_models))
    
    for model_name, model in missing_models:
        try:
            _ensure_wizard_table(cr, model)
            _logger.info("Tabla lista para usar: %s (%s)", model._table, model_name)
        except Exception as e:
            _logger.error("Error preparando tabla para %s: %s", model_name, e)