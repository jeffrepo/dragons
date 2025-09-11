# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    limit = fields.Float(string="Limite")

    @api.model
    def create(self, vals):
        # Desactivar temporalmente la regla de seguridad
        rule = self.env.ref('dragons.rule_cash_journal_user', raise_if_not_found=False)
        original_active = False
        if rule:
            original_active = rule.active
            rule.active = False
        
        try:
            # Crear el diario primero
            journal = super().create(vals)
            print("Diario creado: %s", journal.name)
            
            # Asignar el nuevo diario al usuario que lo creó
            if self.env.user.has_group('base.group_user'):
                # Usar sudo() para evitar problemas de permisos
                self.env.user.sudo().write({
                    'cash_diaries_ids': [(4, journal.id)]  # ✅ Usar journal.id
                })
                print("Diario %s asignado al usuario %s", journal.name, self.env.user.name)
            
            return journal
            
        finally:
            # Reactivar la regla si estaba activa
            if rule and original_active:
                rule.active = True
    