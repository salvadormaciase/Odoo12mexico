'''
Created on Jun 30, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api
import odoo
from datetime import timedelta
import socket
import os
import time

class Session(models.Model):
    _name = 'ir.session'
    _description = 'Session'
    _log_access = False
    
    name = fields.Char(required = True, string='Session ID')
    user_id = fields.Many2one('res.users', required = True)
    start_date = fields.Datetime()
    last_request_time = fields.Datetime()
    remote_addr = fields.Char()
    user_agent = fields.Char()
    hostname = fields.Char()
    
    _sql_constraints = [
        ('uk_name', 'unique(name)', 'Session ID should be unique!'),
        ]    
    
    @api.model
    def update_session(self, session, httprequest):
        now = fields.Datetime.now()
        hostname = socket.gethostname()
        cr = self.env.cr
        cr.execute("update ir_session set last_request_time=%s, user_id=%s, hostname=%s where name=%s", [now, session.uid, hostname, session.sid])
        if cr.rowcount:
            return        
        vals = {
            'last_request_time' : now,
            'remote_addr' : httprequest.remote_addr,
            'user_agent' : httprequest.user_agent,
            'name' : session.sid,
            'start_date' : now,
            'user_id' : session.uid,
            'hostname' : hostname         
            }
        self.create(vals)                      
            
    @api.multi
    def unlink(self):
        session_store = odoo.http.root.session_store
        for record in self:
            session = session_store.get(record.name)
            session_store.delete(session)
        return super(Session, self).unlink()
    
    @api.model
    def _session_gc(self):
        session_timeout = float(self.env['ir.config_parameter'].get_param('session_timeout', 60))
        dt= fields.Datetime.now() - timedelta(minutes = session_timeout)
        self.search([('last_request_time', '<', dt)]).unlink()            
        session_store = odoo.http.root.session_store
        if hasattr(session_store, 'list'):
            session_timeout = time.time() - 60 * session_timeout
            for sid in session_store.list():
                if self.search([('name','=', sid)]):
                    continue
                filename=session_store.get_session_filename(sid)
                try:
                    if os.path.getmtime(filename) < session_timeout:
                        os.unlink(filename)
                except OSError:
                    pass                