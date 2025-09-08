# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    warehouse_ids = fields.Many2many(string="Almacenes", comodel_name="stock.warehouse")
    location_ids = fields.Many2many(string="Ubicaciones", comodel_name="stock.location")
    authorize_cash_conciliation = fields.Boolean(string="Autorizar conciliación 'Efectivo' ", default=False)
    cash_diaries_ids = fields.Many2many(
        comodel_name="account.journal",
        relation="res_users_cash_journal_rel",
        column1="user_id",
        column2="journal_id",
        string="Diarios de Efectivo",
        domain=[('type', '=', 'cash')],
        default=lambda self: self.env['account.journal'].search([('type', '=', 'cash')]).ids,
    )

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_move_sms_validation = fields.Boolean(
        string="SMS Validation for Stock Moves",
        config_parameter='stock_move_sms_validation'
    )