from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockLocationWizard(models.TransientModel):
    _name = 'stock.location.wizard'
    _description = 'Wizard para generar un reporte de ubicaciones personalizado'

    # Cambia estos campos a Many2one en lugar de Char para poder usar la vista lista
    location_id = fields.Many2one('stock.location', string="Ubicación")
    product_id = fields.Many2one('product.product', string="Producto")
    lot_id = fields.Many2one('stock.lot', string="Número de lote/serie")
    inventory_quantity_auto_apply = fields.Float(string="Cantidad real")
    reserved_quantity = fields.Float(string="Cantidad reservada")
    product_uom_id = fields.Many2one('uom.uom', string="Unidad de medida")
    product_categ_id = fields.Many2one('product.category', string="Categoría del producto")
    storage_category_id = fields.Many2one('stock.storage.category', string="Categoría de almacenamiento")
    available_quantity = fields.Float(string="Cantidad disponible")

    def get_values(self):
        """Obtener todos los stock.quants con sudo()"""
        # Buscar todos los stock.quants con sudo para bypassear restricciones
        user_location_ids = self.env.user.location_ids.ids if self.env.user.location_ids else []
        all_quants = self.env['stock.quant'].sudo().search([('location_id', 'in', user_location_ids)])
        
        # Crear registros en el wizard para cada quant
        wizard_records = []
        for quant in all_quants:
            wizard_records.append({
                'location_id': quant.location_id.id,
                'product_id': quant.product_id.id,
                'lot_id': quant.lot_id.id,
                'inventory_quantity_auto_apply': quant.inventory_quantity_auto_apply,
                'reserved_quantity': quant.reserved_quantity,
                'product_uom_id': quant.product_uom_id.id,
                'product_categ_id': quant.product_categ_id.id,
                'storage_category_id': quant.storage_category_id.id,
                'available_quantity': quant.available_quantity,
            })
        
        # Crear todos los registros de una vez
        if wizard_records:
            self.create(wizard_records)
        
        # Retornar acción para mostrar la vista lista
        return {
            'type': 'ir.actions.act_window',
            'name': 'Todas las Ubicaciones (Vista Completa)',
            'res_model': 'stock.location.wizard',
            'view_mode': 'list',
            'target': 'current',
            'domain': [],
        }