# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    warehouse_ids = fields.Many2many(string="Almacenes", comodel_name="stock.warehouse")
    location_ids = fields.Many2many(string="Ubicaciones", comodel_name="stock.location")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_move_sms_validation = fields.Boolean(
        string="SMS Validation for Stock Moves",
        config_parameter='stock_move_sms_validation'
    )