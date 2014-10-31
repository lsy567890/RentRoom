# -*- encoding:utf-8 -*-

from openerp import fields, models, api
from datetime import *
from dateutil.relativedelta import relativedelta

class house(models.Model):
    _name = 'rentroom.house'

    name = fields.Char('房屋名称', required=True)
    address = fields.Char('地址')
    price = fields.Float('租金', required=True)
    record_ids = fields.One2many('rentroom.record', 'house_id', string='记录', invisible=False)

    # 房屋名称不可重复
    @api.constrains('name')
    def check_name(self):
        pass

    # 续租一个月,提供给view中的button调用
    @api.one
    def add_rent_record(self):
        latest_set = self.record_ids.search([('house_id','=',self.name)], order='end_date')
        if len(latest_set)== 0:
            pass
        else:
            latest = latest_set[len(latest_set)-1]
            new_start =latest.end_date
            new_end = fields.Date.from_string(latest.end_date) +relativedelta(months=1)
            latest.copy(default={'start_date':new_start,'end_date': new_end})  # 'start_date': self.end_date, 'end_date': self.end_date})


class record(models.Model):
    _name = 'rentroom.record'
    _order = 'end_date desc'
    _rec_name = 'house_id'

    start_date = fields.Date('开始日期', required=True)
    end_date = fields.Date('结束日期', required=True)
    house_id = fields.Many2one('rentroom.house', string='房屋名称', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='房客')
    house_price = fields.Float('租金')
    fee_ids = fields.One2many('rentroom.fee', 'record_id', string='杂费', invisible=False)
    total = fields.Float('总计', compute='_compute_total')

    # 选择房屋后就把房屋价格传过来
    @api.onchange('house_id')
    def _onchange_house(self):
        self.house_price = self.house_id.price

    # 计算总金额
    @api.one
    @api.depends('house_price', 'fee_ids')
    def _compute_total(self):
        totalfee = 0
        for id in self.fee_ids:
            totalfee = totalfee + id.price
        self.total = self.house_price + totalfee


class fee(models.Model):
    _name = 'rentroom.fee'

    name = fields.Char('费用名称', required=True)
    price = fields.Float('金额', required=True)
    record_id = fields.Many2one('rentroom.record', string=' ',ondelete='cascade', readonly=True)

