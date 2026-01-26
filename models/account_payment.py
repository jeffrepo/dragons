# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError
import logging
from odoo.tools.float_utils import float_is_zero

class AccountPayment(models.Model):
    _inherit = "account.payment"

    estado_autorizado = fields.Selection([('grupo1','Grupo 1'),
                                          ('grupo2','Grupo 2') ,('grupo3', 'Grupo3')],string='Estado autorizado')
    
    def action_validate(self):
        res = super().action_validate()
        
        if self.payment_type == 'outbound' and self.estado_autorizado != 'grupo3':
            raise UserError('Flujo de aprobación incompleto')
        return res

    def action_post(self):
        res = super().action_post()
        
        if self.payment_type == 'outbound' and self.estado_autorizado != 'grupo3':
            raise UserError('Flujo de aprobación incompleto')
        return res
    
    def autorizar_grupo1(self):
        self.estado_autorizado = 'grupo1'

    def autorizar_grupo2(self):
        self.estado_autorizado = 'grupo2'

    def autorizar_grupo3(self):
        for pay in self:
            pay.estado_autorizado = 'grupo3'

            # 1) Si el pago está en borrador, postearlo
            if pay.state == 'draft':
                pay.action_post()

            pay = self.browse(pay.id)

            # 2) Debe existir asiento
            if not pay.move_id:
                raise UserError(_(
                    "El pago %s no generó asiento contable."
                ) % pay.display_name)

            # 3) Si el asiento quedó en draft, POSTEARLO
            if pay.move_id.state == 'draft':
                pay.move_id.action_post()

            # 4) Facturas vinculadas
            if not pay.invoice_ids:
                raise UserError(_(
                    "El pago %s no tiene facturas vinculadas."
                ) % pay.display_name)

            # 5) Líneas 201 del pago (proveedores)
            pay_payable = pay.move_id.line_ids.filtered(lambda l:
                l.account_id.account_type == 'liability_payable'
                and not float_is_zero(
                    l.amount_residual,
                    precision_rounding=l.currency_id.rounding
                )
            )

            if not pay_payable:
                raise UserError(_(
                    "El pago %s no tiene saldo pendiente en Proveedores (201)."
                ) % pay.display_name)

            # 6) Conciliar contra cada factura
            for inv in pay.invoice_ids:
                inv_payable = inv.line_ids.filtered(lambda l:
                    l.account_id.account_type == 'liability_payable'
                    and not float_is_zero(
                        l.amount_residual,
                        precision_rounding=l.currency_id.rounding
                    )
                )

                if not inv_payable:
                    continue

                # Conciliar por cuenta común
                common_accounts = inv_payable.account_id & pay_payable.account_id
                for acc in common_accounts:
                    (inv_payable.filtered(lambda l: l.account_id == acc) +
                     pay_payable.filtered(lambda l: l.account_id == acc)
                    ).reconcile()

        return True
