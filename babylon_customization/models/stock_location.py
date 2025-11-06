
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from random import randint


class StockLocation(models.Model):
    _name = 'stock.location.tags'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Tag Name', required=True, translate=True)
    color = fields.Integer(string='Color', default=_get_default_color)
    active = fields.Boolean(default=True, help="The active field allows you to hide the tags without removing it.")

class StockLocation(models.Model):
    _inherit = 'stock.location'

    location_tag_ids = fields.Many2many(
        'stock.location.tags', string='Locations Tags',
        help='To add the default locations tags while creating new locations')








