# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    limit = fields.Float(string="Limite")