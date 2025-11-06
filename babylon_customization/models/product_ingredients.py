from odoo import api, models, _, fields,tools
from odoo.exceptions import ValidationError
import re

class ProductIngredients(models.Model):
    _inherit = 'product.product'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res['is_storable'] = True
        res['lot_valuated'] = True
        res['tracking'] = 'lot'
        res['use_expiration_date'] = True
        res['expiration_time'] = 365
        res['alert_time'] = 60
        return res

    @api.onchange('default_code')
    def _onchange_default_code(self):
        pass



    def action_update_quantity_on_hand(self):
        return self.product_tmpl_id.with_context(default_product_id=self.id, create=True).action_update_quantity_on_hand()



class StockLot(models.Model):
    _inherit = 'stock.lot'

    def _manufature_ids_domain(self):
        manufacture_tag = self.env['res.partner.category'].search([('name', '=', 'Manufacture')], limit=1)
        if manufacture_tag:
            return [('category_id', 'in', manufacture_tag.ids)]
        else:
            return [('category_id', '=', -2)]

    def _customer_ids_domain(self):
        customer_tag = self.env['res.partner.category'].search([('name','=','Customer')],limit=1)
        if customer_tag:
         return [('category_id','in',customer_tag.ids)]
        else:
            return [('category_id', '=',-2)]

    def _vendor_ids_domain(self):
        customer_tag = self.env['res.partner.category'].search([('name','=','Vendor')],limit=1)
        if customer_tag:
         return [('category_id','in',customer_tag.ids)]
        else:
            return [('category_id', '=',-2)]

    incl = fields.Char(related='product_id.product_tmpl_id.incl')
    active = fields.Boolean(default=True)
    default_code = fields.Char(related='product_id.product_tmpl_id.default_code')
    is_ingredient = fields.Boolean(related='product_id.product_tmpl_id.is_ingredient',store=True)
    is_component = fields.Boolean(related='product_id.product_tmpl_id.is_component', store=True)
    is_finished_goods = fields.Boolean(related='product_id.product_tmpl_id.is_finished_goods', store=True)
    vendor_id = fields.Many2one('res.partner',domain=_vendor_ids_domain,string='Vendor Name')
    manufacture_id = fields.Many2one('res.partner',domain=_manufature_ids_domain, string='Manufacture Name')
    customer_id = fields.Many2one('res.partner',domain=_customer_ids_domain, string='Customer Name')
    vmc_code = fields.Char(compute='_compute_vmc_code')
    purchase_qty = fields.Float()
    price_unit = fields.Float()
    move_id = fields.Many2one('stock.move')

    @api.depends('vendor_id', 'manufacture_id', 'customer_id')
    def _compute_vmc_code(self):
        for record in self:
            vendor_initials = ''
            if record.vendor_id:
                words = re.split(r'[^A-Za-z]+', record.vendor_id.name)
                vendor_initials = ''.join([w[0].upper() for w in words if w])

            manufacture_initials = ''
            if record.manufacture_id:
                words = re.split(r'[^A-Za-z]+', record.manufacture_id.name)
                manufacture_initials = ''.join([w[0].upper() for w in words if w])

            customer_initials = ''
            if record.customer_id:
                words = re.split(r'[^A-Za-z]+', record.customer_id.name)
                customer_initials = ''.join([w[0].upper() for w in words if w])

            # Generate the VMC code
            record.vmc_code = f"{vendor_initials}-{manufacture_initials}-{customer_initials}"


class InheritedPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _manufature_ids_domain(self):
        manufacture_tag = self.env['res.partner.category'].search([('name','=','Manufacture')],limit=1)
        if manufacture_tag:
         return [('category_id','in',manufacture_tag.ids)]
        else:
            return [('category_id', '=',-2)]

    def _customer_ids_domain(self):
        customer_tag = self.env['res.partner.category'].search([('name','=','Customer')],limit=1)
        if customer_tag:
         return [('category_id','in',customer_tag.ids)]
        else:
            return [('category_id', '=',-2)]

    manufacture_id = fields.Many2one('res.partner',domain=_manufature_ids_domain,string='Partner Names')
    customer_id = fields.Many2one('res.partner',domain=_customer_ids_domain, string='Customer Name')
    pack_size = fields.Integer()
    pack_count = fields.Integer()
    pack_uom_id = fields.Many2one('uom.uom',string='Unit of Measure')

    @api.onchange('pack_size','pack_count')
    def compute_qty(self):
        for rec in self:
            if rec.pack_size and rec.pack_count:
                rec.product_qty = rec.pack_size * rec.pack_count
            else:
                rec.product_qty =0.0

    @api.onchange('pack_uom_id')
    def compute_Uom(self):
        for rec in self:
            if rec.pack_uom_id:
                rec.product_uom = rec.pack_uom_id
            else:
                rec.product_uom = rec.product_id.uom_po_id








    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        res = super(InheritedPurchaseOrderLine, self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty,product_uom)
        print(res)
        res['manufacture_id'] = self.manufacture_id.id
        res['customer_id'] = self.customer_id.id
        res['pack_size'] = self.pack_size
        res['pack_count'] = self.pack_count
        res['pack_uom_id'] = self.pack_uom_id.id


        return res





class StockMove(models.Model):
    """Inherited StockMove class to super the functions"""
    _inherit = 'stock.move'

    manufacture_id = fields.Many2one('res.partner', string='Partner Names')
    customer_id = fields.Many2one('res.partner', string='Customer Name')
    vendor_id = fields.Many2one('res.partner', string='Vendor Name',related='picking_id.partner_id')
    purchase_id = fields.Many2one('purchase.order',compute='purchase_order')
    pack_size = fields.Integer()
    pack_count = fields.Integer()
    pack_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')

    @api.depends('origin')
    def purchase_order(self):
        for rec in self:
            po_id = self.env['purchase.order'].search([('name','=',rec.origin)])
            rec.purchase_id = po_id



class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    manufacture_id = fields.Many2one('res.partner',string='Partner Names',related='move_id.manufacture_id')
    customer_id = fields.Many2one('res.partner', string='Customer Name',related='move_id.customer_id')
    vendor_id = fields.Many2one('res.partner', string='Vendor Name', related='move_id.vendor_id')
    price_subtotal = fields.Float()
    is_ingredient = fields.Boolean(related='product_id.product_tmpl_id.is_ingredient',store=True)
    is_component = fields.Boolean(related='product_id.product_tmpl_id.is_component',store=True)
    po_id = fields.Many2one('purchase.order',related='move_id.purchase_id')
    price_unit = fields.Float(
        string="Subtotal Price",
        compute="_compute_price_subtotal",
        store=True,
        help='Computed as quantity_done * price_unit from the stock move.'
    )

    @api.depends('po_id', 'product_id')
    def _compute_price_subtotal(self):
        for line in self:
            if line.po_id and line.product_id:
                # Search for purchase lines in the specific PO matching the product
                po_lines = self.env['purchase.order.line'].search([
                    ('order_id', '=', line.po_id.id),
                    ('product_id', '=', line.product_id.id)
                ])
                # Sum their subtotals
                line.price_unit = sum(po_line.price_unit for po_line in po_lines)
            # else:
            #     line.price_unit = 0.0




    def _prepare_new_lot_vals(self):
        vals = super()._prepare_new_lot_vals()
        print(self.price_subtotal)
        vals['manufacture_id'] = self.manufacture_id.id
        vals['customer_id'] = self.customer_id.id
        vals['vendor_id'] = self.vendor_id.id
        vals['purchase_qty'] = self.quantity
        # vals['price_unit'] = self.price_unit,
        # vals['move_id'] = self.move_id

        return vals

