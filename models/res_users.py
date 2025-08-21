# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    warehouse_ids = fields.Many2many(string="Almacenes", comodel_name="stock.warehouse")
    location_ids = fields.Many2many(string="Ubicaciones", comodel_name="stock.location")