# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import pytz
from odoo.exceptions import UserError
import logging

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tipo_compra = fields.Selection([ ('admin', 'Compra administrativa'),('proyecto', 'Compra proyecto')], string='Tipo de compra')
    estado_autorizado = fields.Selection([('esperando_solicitud_aut','Esperando solicitud autorizacion'),
                                          ('solicitud_aut','Solicitar autorizacion') ,('admin', 'Autorizado admin'),
                                          ('aut_pago', 'Autorizacion pago'),
                                          ('pago_autorizado','Pago autorizad'),
                                          ('firma_gestor_proyecto','Firma gestor proyecto'),
                                         ('solicitud_firma_jefep','Solicitud firma jefe proyecto'),
                                          ('solicitud_firma_op','Solicitud firma direccion operaciones'),
                                         ('solicitud_firma_legal','Solicitud firma direccion legal'),
                                          ('solicitud_firma_direccion_admin','Solicitud firma direccion administrativa'),
                                         ('solicitud_firma_direccion_general','Solicitud firma direccion general'),
                                         ('direccion_general_firmado','Direccion general firmado')],string='Estado autorizado')
    
    prepared_manager_date_job = fields.Char(string="Elabora gestor Fecha, hora y puesto", readonly=True)
    review_project_manager_date_job = fields.Char(string="Jefe de proyecto Fecha, hora y puesto", readonly=True)
    op_managment_date_job = fields.Char(string="Dirección de operaciones Fecha, hora y puesto", readonly=True)
    legal_address_date_job = fields.Char(string="dirección legal Fecha, hora y puesto", readonly=True)
    administrative_address_date_job = fields.Char(string="dirección administrativ Fecha, hora y puesto", readonly=True)
    au_gnrl_date_job = fields.Char(string="Autoriza dirección general Fecha, hora y puesto", readonly=True)

    def get_delivery_time_breakdown(self):
        self.ensure_one()
        if not self.create_date or not self.date_planned:
            return " "
        
        # Convertir a zonas horarias aware si es necesario
        create_date = self.create_date
        date_planned = self.date_planned
        
        # Calcular diferencia
        difference = date_planned - create_date
        total_seconds = difference.total_seconds()
        
        # Calcular semanas, días y horas
        total_hours = total_seconds / 3600
        weeks = int(total_hours // (24 * 7))
        remaining_hours = total_hours % (24 * 7)
        days = int(remaining_hours // 24)
        hours = int(remaining_hours % 24)
        
        # Construir el resultado
        result = []
        if weeks > 0:
            result.append(f"{weeks} week{'s' if weeks != 1 else ''}")
        if days > 0:
            result.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0 or (weeks == 0 and days == 0):
            result.append(f"{hours} hour{'s' if hours != 1 else ''}")
        
        return " ".join(result) if result else "0 hours"
        
    @api.onchange('tipo_compra')
    def _onchange_tipo_compra(self):
        for compra in self:
            if compra.tipo_compra == 'admin':
                compra.estado_autorizado = 'esperando_solicitud_aut'
            if compra.tipo_compra == 'proyecto':
                compra.estado_autorizado = 'firma_gestor_proyecto'

    def solicitar_autorizacion_aa(self):
        group = self.env.ref('dragons.group_dragon_admin')
        self.estado_autorizado = 'solicitud_aut'
        users_in_group = group.users
        if users_in_group:
            mensaje = "Solicita autorización de compra"
            self.message_post(partner_ids=users_in_group.mapped('partner_id').ids,body= mensaje, subject="Autorizacion", email_from=False)

    def autorizar_admin(self):
        self.estado_autorizado = 'admin'
        group = self.env.ref('dragons.group_dragon_auxiliar')
        users_in_group = group.users
        if users_in_group:
            mensaje = "Autorizado"
            self.message_post(partner_ids=users_in_group.mapped('partner_id').ids,body= mensaje, subject="Autorizado", email_from=False)

    def solicitar_autorizar_pago(self):
        self.estado_autorizado = 'aut_pago'
        group = self.env.ref('dragons.group_dragon_admin')
        users_in_group = group.users
        if users_in_group:
            mensaje = "Solicitud pago"
            self.message_post(partner_ids=users_in_group.mapped('partner_id').ids,body= mensaje, subject="Solicitu pago", email_from=False)

    def autorizar_pago(self):
        self.estado_autorizado = 'pago_autorizado'
        group = self.env.ref('dragons.group_dragon_cxp')
        users_in_group = group.users
        if users_in_group:
            mensaje = "Pago autorizado"
            self.message_post(partner_ids=users_in_group.mapped('partner_id').ids,body= mensaje, subject="Pago autorizado", email_from=False)

    def firma_gestor_proyecto(self):
        group = self.env.ref('dragons.group_dragon_gestor_proyecto')
        group_jefe = self.env.ref('dragons.group_dragon_jefe_proyecto')
        users_in_group_gestor = group.users
        users_in_group_jefe = group_jefe.users
        if self.env.user.partner_id.id in users_in_group_gestor.mapped('partner_id').ids:
            self.estado_autorizado = 'solicitud_firma_jefep'
            mensaje_autorizado = "Firma " + group.name + ' por ' + self.env.user.name
            self.message_post(partner_ids=users_in_group_jefe.mapped('partner_id').ids,body= mensaje_autorizado, subject="Firmado", email_from=False)

            mensaje = "Solicitud de firma"
            self.message_post(partner_ids=users_in_group_jefe.mapped('partner_id').ids,body= mensaje, subject="Firmar documento", email_from=False)
            
            ahora_utc = fields.Datetime.now()

            user_tz = self.env.user.tz or 'UTC'
            tz = pytz.timezone(user_tz)

            ahora_local = ahora_utc.astimezone(tz)

            fecha_hora_actual = ahora_local.strftime('%d/%m/%Y %H:%M:%S')
            
            puesto_trabajo = self.create_uid.partner_id.function or '  '

            name = self.env.user.name
            
            texto_completo = f"{fecha_hora_actual} \n {puesto_trabajo}"
            
            self.prepared_manager_date_job = texto_completo
        else:
            raise UserError('No tiene permiso para firmar')

    def firma_jefe_proyecto(self):
        group = self.env.ref('dragons.group_dragon_jefe_proyecto')
        group_dir = self.env.ref('dragons.group_dragon_direccion_operaciones')
        users_in_group_gestor = group.users
        users_in_group_dir = group_dir.users
        if self.env.user.partner_id.id in users_in_group_gestor.mapped('partner_id').ids:
            self.estado_autorizado = 'solicitud_firma_op'
            mensaje_autorizado = "Firma " + group.name + ' por ' + self.env.user.name
            self.message_post(partner_ids=users_in_group_dir.mapped('partner_id').ids,body= mensaje_autorizado, subject="Firmado", email_from=False)
            
            mensaje = "Solicitud de firma"
            self.message_post(partner_ids=users_in_group_dir.mapped('partner_id').ids,body= mensaje, subject="Firmar documento", email_from=False)

            ahora_utc = fields.Datetime.now()

            user_tz = self.env.user.tz or 'UTC'
            tz = pytz.timezone(user_tz)

            ahora_local = ahora_utc.astimezone(tz)

            fecha_hora_actual = ahora_local.strftime('%d/%m/%Y %H:%M:%S')
            
            puesto_trabajo = self.create_uid.partner_id.function or '  '

            name = self.env.user.name
            
            texto_completo = f"{fecha_hora_actual} \n {puesto_trabajo}"
            
            self.review_project_manager_date_job = texto_completo
        else:
            raise UserError('No tiene permiso para firmar')

    def firma_direccion_operaciones(self):
        group = self.env.ref('dragons.group_dragon_direccion_operaciones')
        group_legal = self.env.ref('dragons.group_dragon_direccion_legal')
        users_in_group_oper = group.users
        users_in_group_legal = group_legal.users
        if self.env.user.partner_id.id in users_in_group_oper.mapped('partner_id').ids:
            self.estado_autorizado = 'solicitud_firma_legal'
            mensaje_autorizado = "Firma " + group.name + ' por ' + self.env.user.name
            self.message_post(partner_ids=users_in_group_legal.mapped('partner_id').ids,body= mensaje_autorizado, subject="Firmado", email_from=False)
            
            
            mensaje = "Solicitud de firma"
            self.message_post(partner_ids=users_in_group_legal.mapped('partner_id').ids,body= mensaje, subject="Firmar documento", email_from=False)
            
            ahora_utc = fields.Datetime.now()

            user_tz = self.env.user.tz or 'UTC'
            tz = pytz.timezone(user_tz)

            ahora_local = ahora_utc.astimezone(tz)

            fecha_hora_actual = ahora_local.strftime('%d/%m/%Y %H:%M:%S')
            
            puesto_trabajo = self.create_uid.partner_id.function or '  '
            
            name = self.env.user.name
            
            texto_completo = f"{fecha_hora_actual} \n {puesto_trabajo}"
            
            self.op_managment_date_job = texto_completo
        else:
            raise UserError('No tiene permiso para firmar')

    def firma_direccion_legal(self):
        group = self.env.ref('dragons.group_dragon_direccion_legal')
        group_gen = self.env.ref('dragons.group_dragon_direccion_admin')
        users_in_group_admin = group.users
        users_in_group_gen = group_gen.users
        if self.env.user.partner_id.id in users_in_group_admin.mapped('partner_id').ids:
            self.estado_autorizado = 'solicitud_firma_direccion_admin'
            mensaje_autorizado = "Firma " + group.name + ' por ' + self.env.user.name
            self.message_post(partner_ids=users_in_group_gen.mapped('partner_id').ids,body= mensaje_autorizado, subject="Firmado", email_from=False)
                        
            mensaje = "Solicitud de firma"
            self.message_post(partner_ids=users_in_group_gen.mapped('partner_id').ids,body= mensaje, subject="Firmar documento", email_from=False)
            
            ahora_utc = fields.Datetime.now()

            user_tz = self.env.user.tz or 'UTC'
            tz = pytz.timezone(user_tz)

            ahora_local = ahora_utc.astimezone(tz)

            fecha_hora_actual = ahora_local.strftime('%d/%m/%Y %H:%M:%S')
            
            puesto_trabajo = self.create_uid.partner_id.function or '  '
            
            name = self.env.user.name
            
            texto_completo = f"{fecha_hora_actual} \n {puesto_trabajo}"
            
            self.legal_address_date_job = texto_completo
        else:
            raise UserError('No tiene permiso para firmar')

    def firma_direccion_admin(self):
        group = self.env.ref('dragons.group_dragon_direccion_admin')
        group_gen = self.env.ref('dragons.group_dragon_direccion_general')
        users_in_group_admin = group.users
        users_in_group_gen = group_gen.users
        if self.env.user.partner_id.id in users_in_group_admin.mapped('partner_id').ids:
            self.estado_autorizado = 'solicitud_firma_direccion_general'
            mensaje_autorizado = "Firma " + group.name + ' por ' + self.env.user.name
            self.message_post(partner_ids=users_in_group_gen.mapped('partner_id').ids,body= mensaje_autorizado, subject="Firmado", email_from=False)
            
            mensaje = "Solicitud de firma"
            self.message_post(partner_ids=users_in_group_gen.mapped('partner_id').ids,body= mensaje, subject="Firmar documento", email_from=False)

            ahora_utc = fields.Datetime.now()

            user_tz = self.env.user.tz or 'UTC'
            tz = pytz.timezone(user_tz)

            ahora_local = ahora_utc.astimezone(tz)

            fecha_hora_actual = ahora_local.strftime('%d/%m/%Y %H:%M:%S')
            
            puesto_trabajo = self.create_uid.partner_id.function or '  '
            
            name = self.env.user.name
            
            texto_completo = f"{fecha_hora_actual} \n {puesto_trabajo}"
            
            self.administrative_address_date_job = texto_completo
            
        else:
            raise UserError('No tiene permiso para firmar')

    def firma_direccion_general(self):
        group = self.env.ref('dragons.group_dragon_direccion_general')
        users_in_group_gen = group.users
        if self.env.user.partner_id.id in users_in_group_gen.mapped('partner_id').ids:
            self.estado_autorizado = 'direccion_general_firmado'

            mensaje = "Orden de compra autorizada " + group.name + ' por ' + self.env.user.name
            self.message_post(partner_ids=users_in_group_gen.mapped('partner_id').ids,body= mensaje, subject="Firmar documento", email_from=False)
            
            ahora_utc = fields.Datetime.now()

            user_tz = self.env.user.tz or 'UTC'
            tz = pytz.timezone(user_tz)

            ahora_local = ahora_utc.astimezone(tz)

            fecha_hora_actual = ahora_local.strftime('%d/%m/%Y %H:%M:%S')
            
            puesto_trabajo = self.create_uid.partner_id.function or '  '
            
            name = self.env.user.name
            
            texto_completo = f"{fecha_hora_actual} \n {puesto_trabajo}"
            
            self.au_gnrl_date_job = texto_completo
            self.button_confirm()
        else:
            raise UserError('No tiene permiso para firmar')
    
    def button_confirm(self):
        res = super().button_confirm()
        for orden in self:
            if orden.tipo_compra == 'admin':
                if orden.estado_autorizado not in ['admin','aut_pago','pago_autorizado']:
                    logging.warning('retornar error')
                    raise UserError('Flujo de aprobación incompleto')
            elif orden.tipo_compra == 'proyecto':
                if orden.estado_autorizado != 'direccion_general_firmado':
                   raise UserError('No se puede confirmar, hasta terminar el flujo de autorizaciones')
                else:
                    group = self.env.ref('dragons.group_dragon_direccion_general')
                    users_in_group_gen = group.users
                    if self.env.user.partner_id.id not in users_in_group_gen.mapped('partner_id').ids:
                        raise UserError('Solo puede confirmar direccion general')
                    else:
                        pass
            else:
                pass
        return res

    def compras_pendientes_email(self):
        PurchaseOrder = self.env['purchase.order']
    
        # Map estado_autorizado to group XML IDs
        grupos = {
            'solicitud_firma_jefep': 'dragons.group_dragon_jefe_proyecto',
            'solicitud_firma_op': 'dragons.group_dragon_direccion_operaciones',
            'solicitud_firma_legal': 'dragons.group_dragon_direccion_legal',
            'solicitud_firma_direccion_admin': 'dragons.group_dragon_direccion_admin',
            'solicitud_firma_direccion_general': 'dragons.group_dragon_direccion_general',
        }
    
        # Step 1: Group purchase orders by estado_autorizado
        groups = PurchaseOrder.read_group(
            domain=[
                ('state', '=', 'draft'),
                ('estado_autorizado', '!=', 'direccion_general_firmado')
            ],
            fields=['estado_autorizado'],
            groupby=['estado_autorizado'],
            lazy=False
        )
    
        for group in groups:
            estado = group['estado_autorizado']
            if not estado:
                continue  # Skip undefined estado_autorizado
    
            domain = group['__domain']
            orders = PurchaseOrder.search(domain)
            order_names = orders.mapped('name')
    
            # Step 2: Get group XML ID and users
            group_xml_id = grupos.get(estado)
            if not group_xml_id:
                logging.warning(f"No group configured for estado_autorizado: {estado}")
                continue
    
            try:
                user_group = self.env.ref(group_xml_id)
            except ValueError:
                logging.warning(f"Group XML ID '{group_xml_id}' not found.")
                continue
    
            users = user_group.users
            emails = users.mapped('email')
            emails = [email for email in emails if email]  # Filter out empty emails
    
            if not emails:
                logging.warning(f"No emails found for group {group_xml_id}")
                continue
    
            # Step 3: Send email
            body = f"""
            <p>Hola,</p>
            <p>Hay órdenes de compra pendientes para tu autorización (<strong>{estado}</strong>):</p>
            <ul>
                {''.join(f'<li>{name}</li>' for name in order_names)}
            </ul>
            <p>Por favor, ingresa a Odoo para revisarlas.</p>
            """
    
            mail_values = {
                'subject': f'Órdenes de Compra Pendientes - Estado: {estado}',
                'body_html': body,
                'email_to': ','.join(emails),
            }
            self.env['mail.mail'].create(mail_values).send()
    
            logging.warning(f"Correo enviado a {emails} para estado {estado} con órdenes: {order_names}")
