# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_
import logging
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class InheritedSaleOrder(models.Model):
    _inherit = 'sale.order'

    def create_purchase_order(self):
        if not self:
            raise UserError("Please select at least one Sale Order.")

        purchase_order_obj = self.env['purchase.order']
        product_dict = {}


        for sale in self:
            for line in sale.order_line:
                product = line.product_id
                if not product:
                    continue

                # Determine vendor for this product (first available seller)
                vendor = product.seller_ids[0].partner_id if product.seller_ids else None
                if not vendor:
                    raise UserError(f"No vendor found for product {product.display_name}.")

                # Use (product, vendor) as the key
                key = (product, vendor)

                # Initialize dictionary entry if not exists
                if key not in product_dict:
                    product_dict[key] = {
                        'product_qty': 0.0,
                        'product_uom': line.product_uom,
                        'price_unit': 0.0,
                        'sale_orders': self.env['sale.order'],
                    }

                # Accumulate quantities and sale orders
                product_dict[key]['product_qty'] += line.product_uom_qty
                product_dict[key]['sale_orders'] |= sale

                # Use vendor price if available, else sale line price
                if product.seller_ids:
                    product_dict[key]['price_unit'] = product.seller_ids[0].price
                else:
                    product_dict[key]['price_unit'] = line.price_unit

        if not product_dict:
            raise UserError("No products found in selected Sale Orders.")


        vendor_products = {}
        for (product, vendor), vals in product_dict.items():
            if vendor.id not in vendor_products:
                vendor_products[vendor.id] = []
            vendor_products[vendor.id].append((product, vals))


        purchase_orders = self.env['purchase.order']
        for vendor_id, products in vendor_products.items():
            po_vals = {
                'partner_id': vendor_id,
                'origin': ', '.join(str(sale.name) for sale in self) if self else '',
                'order_line': [],
            }

            po_lines = []
            for product, vals in products:
                po_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': product.display_name,
                    'product_qty': vals['product_qty'],
                    'product_uom': vals['product_uom'].id,
                    'price_unit': vals['price_unit'],
                    'date_planned': fields.Datetime.now(),
                    'sale_order_ids': [(6, 0, vals['sale_orders'].ids)],
                }))

            po_vals['order_line'] = po_lines
            purchase_order = purchase_order_obj.create(po_vals)
            for product, vals in products:
                related_lines = vals['sale_orders'].mapped('order_line').filtered(lambda l: l.product_id == product)
                related_lines.write({'purchase_order_ids': [(4, purchase_order.id)]})



        return purchase_orders


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sale_order_ids = fields.Many2many(
        'sale.order',
        'purchase_line_sale_rel',
        'purchase_line_id',
        'sale_order_id',
        string='Related Sale Orders'
    )


class InheritedSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    purchase_order_ids = fields.Many2many(
        'purchase.order',
        string='Purchase Orders',
        help='Purchase Orders created for this Sale Order Line.'
    )