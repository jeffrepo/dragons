# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _search_default_journal(self):
        print("Hiiii")
        # Mantener lógica original para statement lines
        if self.statement_line_ids.statement_id.journal_id:
            return self.statement_line_ids.statement_id.journal_id[:1]

        journal_types = self._get_valid_journal_types()
        company = self.company_id or self.env.company
        
        # Filtrar diarios del usuario por compañía y tipo
        user_journals = self.env.user.cash_diaries_ids.filtered(
            lambda j: j.company_id == company and j.type in journal_types
        )
        
        # Si hay diarios del usuario, aplicar prioridad
        if user_journals:
            # Filtrar por currency si es necesario
            currency_id = None
            if self.env.cache.contains(self, self._fields['currency_id']):
                currency_id = self.currency_id.id or self._context.get('default_currency_id')
            
            if currency_id and currency_id != company.currency_id.id:
                currency_journal = user_journals.filtered(
                    lambda j: j.currency_id.id == currency_id
                )
                if currency_journal:
                    return currency_journal[0]
            
            return user_journals[0]
        
        # Si no hay diarios del usuario, usar lógica original
        return super()._search_default_journal()
