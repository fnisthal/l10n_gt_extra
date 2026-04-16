# -*- encoding: utf-8 -*-

from odoo import api, models
import logging

class ReporteBanco(models.AbstractModel):
    _name = 'report.l10n_gt_extra.reporte_banco'
    _description = 'Libro de Banco'
    
    def lineas(self, datos):
        cuenta = self.env['account.account'].browse(datos['cuenta_bancaria_id'][0])

        usar_balance_moneda = False
        lineas = []
        for linea in self.env['account.move.line'].search([('account_id', '=', cuenta.id), ('parent_state', '=', 'posted'), ('date', '>=', datos['fecha_desde']), ('date', '<=', datos['fecha_hasta']), ('company_id', '=', self.env.company.id)], order='date'):
            detalle = {
                'fecha': linea.date,
                'documento': linea.move_id.name if linea.move_id else '',
                'nombre': linea.partner_id.name or '',
                'concepto': (linea.ref if linea.ref else '') + (linea.name if linea.name else ''),
                'debito': linea.debit,
                'credito': linea.credit,
                'balance': 0,
                'tipo': '',
                'moneda': linea.company_id.currency_id,
            }

            if linea.amount_currency:
                detalle['moneda'] = linea.currency_id
                if linea.amount_currency > 0:
                    detalle['debito'] = linea.amount_currency
                else:
                    detalle['credito'] = -1 * linea.amount_currency

            # Si la cuenta no tiene moneda o la moneda de la cuenta es la misma de la compañía
            #if not cuenta.currency_id or (cuenta.currency_id.id == linea.company_id.currency_id.id):
            if not cuenta.currency_id or (cuenta.currency_id == self.env.company.currency_id):
                usar_balance_moneda = False
            
                # Se agregan lineas que no tiene moneda o tienen la misma moneda que la compañía
                #if not linea.currency_id or linea.currency_id.id == linea.company_id.currency_id.id:
                if not linea.currency_id or linea.currency_id == linea.company_id.currency_id:
                    lineas.append(detalle)
                    
            # Si no, si la cuenta si tienen moneda y la moneda de la cuenta es diferente que la de la compañía
            else:
                usar_balance_moneda = True
                
                # Se agregan lineas que tienen la moneda de la cuenta
                if linea.currency_id == cuenta.currency_id:
                    lineas.append(detalle)

        balance_inicial = self.balance_inicial(datos)
        if usar_balance_moneda:
            balance = balance_inicial['balance_moneda']
        else:
            balance = balance_inicial['balance']

        for linea in lineas:
            balance = balance + linea['debito'] - linea['credito']
            linea['balance'] = balance

        return lineas

    def balance_inicial(self, datos):
        cuenta = self.env['account.account'].browse(datos['cuenta_bancaria_id'][0])
        
        # Si la cuenta no tiene moneda o la moneda de la cuenta es la misma de la compañía
        if not cuenta.currency_id or (cuenta.currency_id == self.env.company.currency_id):
            usar_balance_moneda = False        
        # Si no, si la cuenta si tienen moneda y la moneda de la cuenta es diferente que la de la compañía
        else:
            usar_balance_moneda = True

        self.env.cr.execute("SELECT COALESCE(SUM(debit) - SUM(credit), 0) AS balance, COALESCE(SUM(amount_currency), 0) AS balance_moneda FROM account_move_line WHERE account_id = %s AND parent_state = %s AND date < %s AND company_id = %s", (cuenta.id, 'posted', datos['fecha_desde'], self.env.company.id))
        result = self.env.cr.dictfetchall()[0]
        result['usar_balance_moneda'] = usar_balance_moneda
        
        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'moneda': docs[0].cuenta_bancaria_id.currency_id or self.env.company.currency_id,
            'lineas': self.lineas,
            'balance_inicial': self.balance_inicial(data['form']),
            'current_company_id': self.env.company,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
