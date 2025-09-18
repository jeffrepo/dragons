# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError

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
        self.estado_autorizado = 'grupo3'
        self.action_post()
        self.action_validate()
        if self.invoice_ids:
            for factura in self.invoice_ids:
                payment_lines = self.move_id.line_ids.filtered(lambda line: line.account_id.account_type == 'liability_payable' and not line.reconciled)
                factura.js_assign_outstanding_line(payment_lines.id)
