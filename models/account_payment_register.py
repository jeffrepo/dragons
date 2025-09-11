from odoo import Command, models, fields, api, _
from odoo.exceptions import UserError

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    @api.depends('payment_type', 'company_id', 'can_edit_wizard')
    def _compute_available_journal_ids(self):
        # Primero obtener los diarios disponibles según Odoo
        super()._compute_available_journal_ids()
        
        for wizard in self:
            # Para usuarios admin, no filtrar
            if self.env.user.has_group('base.group_system'):
                continue
                
            user_journals = self.env.user.cash_diaries_ids
            
            # 1. Filtrar diarios del usuario que sean bank/cash y de la compañía correcta
            valid_user_journals = user_journals.filtered(
                lambda j: j.type in ('bank', 'cash') and 
                         j.company_id == wizard.company_id
            )
            
            # 2. Si no hay diarios válidos del usuario, mostrar error
            if not valid_user_journals:
                raise UserError("🎯 Diarios incompatibles\n\n"
                              "❌ No tienes diarios de Banco/Efectivo asignados\n"
                              "💼 Tipo de pago: %s\n"
                              "🏢 Compañía requerida: %s\n\n"
                              "✨ Pide a tu administrador que te asigne diarios válidos"
                              % (wizard.payment_type, wizard.company_id.name))
            
            # 3. Obtener los diarios disponibles según Odoo
            odoo_available_journals = wizard.available_journal_ids
            
            # 4. Forzar que los diarios disponibles sean los del usuario (prioridad)
            #    pero mantener solo los que también son válidos para Odoo
            final_available_journals = valid_user_journals & odoo_available_journals
            
            # 5. Si no hay intersección, usar los diarios del usuario (más importante)
            if not final_available_journals:
                final_available_journals = valid_user_journals
            
            wizard.available_journal_ids = [Command.set(final_available_journals.ids)]
            
            # 🚨 Debug info
            print("=== DEBUG WIZARD ===")
            print("User:", self.env.user.name)
            print("User journals:", valid_user_journals.mapped('name'))
            print("Odoo available:", odoo_available_journals.mapped('name'))
            print("Final available:", final_available_journals.mapped('name'))
            print("Payment type:", wizard.payment_type)
    
    @api.depends('available_journal_ids')
    def _compute_journal_id(self):
        super()._compute_journal_id()
        
        for wizard in self:
            if not self.env.user.has_group('base.group_system'):
                user_journals = self.env.user.cash_diaries_ids.filtered(
                    lambda j: j.type in ('bank', 'cash') and 
                             j.company_id == wizard.company_id
                )
                
                # Si el diario actual no es del usuario, asignar uno válido
                if wizard.journal_id not in user_journals and user_journals:
                    wizard.journal_id = user_journals[0]