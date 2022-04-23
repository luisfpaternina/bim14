import xmlrpc
import logging

from odoo import fields, models
from odoo.exceptions import ValidationError

COMMON_URL = '/xmlrpc/2/common'
OBJECT_URL = '/xmlrpc/2/object'
FIELDS = ['name', 'title', 'obs', 'entry_date', 'obs_calificacion', 'prioridad',
          'end_will_end', 'numero_veces', 'comprobante_01_name', 'obs_solucion',
          'comprobante_01', 'state', 'clasificacion', 'calificacion', 'end_date']


class TicketServer(models.Model):
    _name = 'ticket.server'
    _description = 'Servidor de tickets'
    _rec_name = 'url'
    _order = 'sequence, id'
    _inherit = ['mail.thread']
    _logger = logging.getLogger(__name__)

    active = fields.Boolean(default=True, copy=False, tracking=True)
    sequence = fields.Integer(default=10)
    url = fields.Char(required=True, tracking=True)
    database = fields.Char(required=True, tracking=True)
    login = fields.Char(required=True, tracking=True)
    password = fields.Char(required=True, copy=False)
    state = fields.Selection([('offline', 'Offline'), ('online', 'Online')],
                             default='offline', copy=False, tracking=True)
    remote_uid = fields.Integer(readonly=True, copy=False)

    def check_state(self):
        # Comprobamos el servidor
        try:
            common_proxy = xmlrpc.client.ServerProxy(self.url + COMMON_URL)
            uid = common_proxy.login(self.database, self.login, self.password)
            self.write({'state': 'online', 'remote_uid': uid})
        except Exception as exc:
            self._logger.error('Error conectando con el servidor', exc_info=True)
            if not self.env.context.get('no_raise_exc'):
                raise ValidationError('Error conectando con el servidor')
            self.write({'state': 'offline'})
            return False
        # Comprobamos que el usuario tenga permisos de usuario ticket al menos
        object_proxy = xmlrpc.client.ServerProxy(self.url + OBJECT_URL)
        result = object_proxy.execute(*self.credentials, 'res.users',
                                      'has_group',
                                      'ticket_pro.tiket_pro_user_group')
        if result:
            self.write({'state': 'online', 'remote_uid': uid})
            return result
        # Comprobamos por último si tiene el de administrador de tickets
        object_proxy = xmlrpc.client.ServerProxy(self.url + OBJECT_URL)
        result = object_proxy.execute(*self.credentials, 'res.users',
                                      'has_group',
                                      'ticket_pro.tiket_pro_manager_group')
        if not result and not self.env.context.get('no_raise_exc'):
            raise ValidationError('El usuario no tiene permisos para tickets')
        state = 'online' if result else 'offline'
        self.write({'state': state, 'remote_uid': uid})
        return result

    @property
    def credentials(self):
        return (self.database, self.remote_uid, self.password)

    def _clear_nones(self, values):
        fixed = {}
        for key, value in values.items():
            if value is None:
                fixed[key] = False
            else:
                fixed[key] = value
        return fixed

    def create_remote_tickets(self, ticket):
        remote_ids = {}
        for record in self:
            if not record.with_context(no_raise_exc=True).check_state():
                continue
            object_proxy = xmlrpc.client.ServerProxy(record.url + OBJECT_URL)
            values = {att: getattr(ticket, att) for att in FIELDS}
            values['category_id'] = record._get_category(ticket.category_id)
            values['user_error_id'] = False
            values = self._clear_nones(values)
            remote_id = object_proxy.execute_kw(*record.credentials,
                                                'ticket.pro',
                                                'create', [values])
            remote_ids[record] = remote_id
        return remote_ids

    def _get_category(self, category):
        if not self.check_state():
            return False
        xml_id = (category.get_xml_id() or {}).get(category.id)
        if not xml_id:
            return False
        module, name = xml_id.split('.')
        object_proxy = xmlrpc.client.ServerProxy(self.url + OBJECT_URL)
        result = object_proxy.execute_kw(*self.credentials, 'ir.model.data',
                                         'search_read', [[
                                             ('model', '=', 'ticket.category'),
                                             ('module', '=', module),
                                             ('name', '=', name)
                                         ], ['res_id']])
        if not result:
            return False
        return result[0].get('res_id')
