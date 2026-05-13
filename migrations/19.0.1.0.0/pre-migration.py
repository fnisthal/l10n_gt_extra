import logging


_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1
        FROM ir_model_fields
        WHERE model = 'account.move'
          AND name = 'uuid_pos_fel'
        """
    )
    if not cr.fetchone():
        _logger.info("account_move.uuid_pos_fel no está definido en ir.model.fields; no se crea la columna")
        return

    cr.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'account_move'
          AND column_name = 'uuid_pos_fel'
        """
    )
    if cr.fetchone():
        _logger.info("account_move.uuid_pos_fel ya existe")
        return

    cr.execute("ALTER TABLE account_move ADD COLUMN uuid_pos_fel varchar")
    _logger.info("Se creó account_move.uuid_pos_fel para compatibilidad con FEL")