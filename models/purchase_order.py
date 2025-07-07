# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tipo_compra = fields.Selection([ ('admin', 'Compra administrativa'),('proyecto', 'Compra proyecto')], string='Tipo de compra')

    def button_confirm(self):
        for order in self:
            res = super().button_confirm()
        return res