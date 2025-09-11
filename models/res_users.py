# -*- coding: utf-8 -*-
from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    warehouse_ids = fields.Many2many(string="Almacenes", comodel_name="stock.warehouse")
    location_ids = fields.Many2many(string="Ubicaciones", comodel_name="stock.location")
    # authorize_cash_conciliation = fields.Boolean(string="Autorizar conciliación 'Efectivo' ", default=False)
    cash_diaries_ids = fields.Many2many(
        comodel_name="account.journal",
        relation="res_users_cash_journal_rel",
        column1="user_id",
        column2="journal_id",
        string="Diarios de Efectivo y otros",
    )

    def write(self, vals):
        # Lista de reglas que necesitan desactivarse temporalmente
        rules_to_disable = [
            'dragons.rule_cash_journal_user',
            'dragons.rule_warehouse_user',  
            'dragons.rule_location_user'    
        ]
        
        # Guardar estado original de las reglas y desactivarlas
        original_states = {}
        for rule_xml_id in rules_to_disable:
            rule = self.env.ref(rule_xml_id, raise_if_not_found=False)
            if rule:
                original_states[rule_xml_id] = rule.active
                rule.active = False
        
        try:
            # Ejecutar el write original
            result = super().write(vals)
            
            # Reactivar las reglas a su estado original
            for rule_xml_id, original_active in original_states.items():
                rule = self.env.ref(rule_xml_id, raise_if_not_found=False)
                if rule and original_active:
                    rule.active = True
                    
            return result
            
        except Exception as e:
            # En caso de error, asegurarse de reactivar todas las reglas
            for rule_xml_id, original_active in original_states.items():
                rule = self.env.ref(rule_xml_id, raise_if_not_found=False)
                if rule and original_active:
                    rule.active = True
            raise e

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_move_sms_validation = fields.Boolean(
        string="SMS Validation for Stock Moves",
        config_parameter='stock_move_sms_validation'
    )