# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import json
import os
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

examples = [
    {"input": "List all accounts.", "query": "SELECT * FROM account_account;"},
    {
        "input": "Find all analytic lines for the account with ID 3.",
        "query": "SELECT * FROM account_analytic_line WHERE account_id = 3;",
    },
    {"input": "List all assets.", "query": "SELECT * FROM account_asset;"},
    {
        "input": "List all cash rounding methods.",
        "query": "SELECT * FROM account_cash_rounding;",
    },
    {
        "input": "Find all fiscal positions for the company with ID 2.",
        "query": "SELECT * FROM account_fiscal_position WHERE company_id = 2;",
    },
    {
        "input": "Count the number of invoices for each customer.",
        "query": "SELECT customer_id, COUNT(*) AS invoice_count FROM Invoice GROUP BY customer_id;",
    },
    {
        "input": "i need all tickets assing to Portal User Template from DB",
        "query": "SELECT * FROM helpdesk_ticket WHERE user_id IN (SELECT id FROM res_partner WHERE name = 'Portal User Template');",
    },
    {
        "input": "List the total amount of sales for each sales team.",
        "query": "SELECT team_id, SUM(amount_total) AS total_sales FROM sale_order GROUP BY team_id;",
    },
    {
        "input": "Find all customers.",
        "query": "SELECT * FROM res_partner WHERE customer = TRUE;",
    },
    {
        "input": "Find the total number of invoices.",
        "query": "SELECT COUNT(*) FROM Invoice;",
    },
    {
        "input": "i want sell order details of Gopal Jewellers",
        "query": "SELECT * FROM sale_order WHERE partner_id IN (SELECT id FROM res_partner WHERE name = 'Gopal Jewellers - New Delhi);",
    },
    {
        "input": "i want customer name according to sale order",
        "query": "SELECT so.name,rp.name from sale_order so join res_partner rp ON so.partner_id = rp.id",
    },
    {
        "input": "i want all tickets assing to Azure Interior",
        "query": "SELECT * FROM helpdesk_ticket WHERE user_id IN (SELECT id FROM res_partner WHERE name = 'Azure Interior')",
    },
    {
        "input": "i want top 10 selling product details in DB",
        "query": "SELECT product_template.name, SUM(sale_order_line.product_uom_qty) AS total_quantity_sold FROM product_template JOIN product_product ON product_template.id = product_product.product_tmpl_id JOIN sale_order_line ON product_product.id = sale_order_line.product_id GROUP BY product_template.name ORDER BY total_quantity_sold DESC LIMIT 10",
    },
    {
        "input": "i want last 20 product iD with product name",
        "query": "SELECT id, name FROM product_template ORDER BY id DESC LIMIT 20",
    },
    {
        "input": "i want total sell count of product saree in last month",
        "query": "SELECT COUNT(so.id) AS order_coun FROM sale_order_line sol JOIN sale_order so ON sol.order_id = so.id  JOIN product_product pp ON sol.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id WHERE pt.name::jsonb ->> 'en_US' = 'saree' AND so.state IN ('sale', 'done') AND so.date_order >= (CURRENT_DATE - INTERVAL '1 month');",
    },
    {
        "input": "i want all info of Large Desk",
        "query": "SELECT pp.id AS variant_id, pp.default_code AS internal_reference, pt.list_price AS list_price, pt.name::jsonb ->> 'en_US' AS product_name FROM product_product pp JOIN product_template pt ON pp.product_tmpl_id = pt.id WHERE pt.name::jsonb ->> 'en_US' = 'large desk' AND pp.active = TRUE;",
    },
    {
        "input": "i want last 10 sell order",
        "query": "SELECT rp.name AS partner_name, so.create_date, so.date_order, so.amount_total, so.id FROM sale_order so JOIN res_partner rp ON so.partner_id = rp.id ORDER BY so.create_date DESC LIMIT 10",
    },
    {
        "input": "i want last 10 sell order all details",
        "query": "SELECT rp.name AS partner_name, so.create_date, so.date_order, so.amount_total, so.id FROM sale_order so JOIN res_partner rp ON so.partner_id = rp.id ORDER BY so.create_date DESC LIMIT 10",
    },
    {
        "input": "i need some info of SO",
        "query": "SELECT rp.name AS partner_name, so.create_date, so.date_order, so.amount_total, so.id FROM sale_order so JOIN res_partner rp ON so.partner_id = rp.id ORDER BY so.create_date DESC LIMIT 10",
    },
    {
        "input": "i need last 10 Purchase order details",
        "query": "SELECT po.id, po.create_date, po.date_order, po.amount_total, rp.name AS partner_name FROM purchase_order po JOIN res_partner rp ON po.partner_id = rp.id ORDER BY po.create_date DESC LIMIT 10",
    },
    {
        "input": "Give me last 10 Purchase order details",
        "query": "SELECT po.id, po.create_date, po.date_order, po.amount_total, rp.name AS partner_name FROM purchase_order po JOIN res_partner rp ON po.partner_id = rp.id ORDER BY po.create_date DESC LIMIT 10",
    },
    {
        "input": "What are the specifics of the most recent 10 purchase orders I made?",
        "query": "SELECT po.id, po.create_date, po.date_order, po.amount_total, rp.name AS partner_name FROM purchase_order po JOIN res_partner rp ON po.partner_id = rp.id ORDER BY po.create_date DESC LIMIT 10",
    },
    {
        "input": "Could you retrieve the details for the last ten purchase orders in my account?",
        "query": "SELECT po.id, po.create_date, po.date_order, po.amount_total, rp.name AS partner_name FROM purchase_order po JOIN res_partner rp ON po.partner_id = rp.id ORDER BY po.create_date DESC LIMIT 10",
    },
    {"input": "How many leads are there", "query": "SELECT COUNT(*) FROM crm_lead"},
    {
        "input": "Give me last 10 created leads",
        "query": "SELECT id, name, email_from, create_date, stage_id FROM crm_lead ORDER BY create_date DESC LIMIT 10",
    },
    {
        "input": "Show total number of leads in the CRM",
        "query": "SELECT COUNT(*) FROM crm_lead",
    },
    {
        "input": "List the latest 10 leads created",
        "query": "SELECT id, name, email_from, create_date, stage_id FROM crm_lead ORDER BY create_date DESC LIMIT 10",
    },
    {
        "input": "How many opportunities are currently in progress",
        "query": "SELECT COUNT(*) FROM crm_lead WHERE type = 'opportunity' AND stage_id IS NOT NULL",
    },
    {
        "input": "Retrieve the most recent 10 sales orders",
        "query": "SELECT so.id, so.date_order, so.amount_total, rp.name AS customer_name FROM sale_order so JOIN res_partner rp ON so.partner_id = rp.id ORDER BY so.date_order DESC LIMIT 10;",
    },
    {
        "input": "Get top 5 products by total sales amount",
        "query": "SELECT pt.name AS product_name, SUM(sol.price_total) AS total_sales FROM sale_order_line sol JOIN product_product pp ON sol.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id GROUP BY pt.name ORDER BY total_sales DESC LIMIT 5;",
    },
    {
        "input": "Count of sales orders by customer",
        "query": "SELECT rp.name AS customer_name, COUNT(so.id) AS order_count FROM sale_order so JOIN res_partner rp ON so.partner_id = rp.id GROUP BY rp.name ORDER BY order_count DESC;",
    },
    {
        "input": "Monthly sales breakdown",
        "query": "SELECT DATE_TRUNC('month', so.date_order) AS month, SUM(so.amount_total) AS total_sales FROM sale_order so GROUP BY month ORDER BY month DESC;",
    },
    {
        "input": "List of sales orders in draft state",
        "query": "SELECT so.id, so.date_order, rp.name AS customer_name FROM sale_order so JOIN res_partner rp ON so.partner_id = rp.id WHERE so.state = 'draft' ORDER BY so.date_order DESC;",
    },
    {
        "input": "Show lead count per salesperson",
        "query": "SELECT ru.name AS salesperson, COUNT(cl.id) AS total_leads FROM crm_lead cl JOIN res_users ru ON cl.user_id = ru.id GROUP BY ru.name ORDER BY total_leads DESC",
    },
    {
        "input": "Show stock quantities per product across all warehouses",
        "query": "SELECT pt.name AS product_name, pp.default_code AS sku, sl.complete_name AS warehouse, SUM(sq.quantity) AS total_quantity FROM stock_quant sq JOIN product_product pp ON sq.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id JOIN stock_location sl ON sq.location_id = sl.id WHERE sl.usage = 'internal' GROUP BY pt.name, pp.default_code, sl.complete_name ORDER BY pt.name",
    },
    {
        "input": "List products with zero stock across all locations",
        "query": "SELECT pt.name AS product_name, pp.default_code AS sku FROM stock_quant sq JOIN product_product pp ON sq.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id WHERE sq.quantity = 0 GROUP BY pt.name, pp.default_code ORDER BY pt.name",
    },
    {
        "input": "Find products with negative stock in any location",
        "query": "SELECT pt.name AS product_name, pp.default_code AS sku, sl.complete_name AS location, sq.quantity FROM stock_quant sq JOIN product_product pp ON sq.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id JOIN stock_location sl ON sq.location_id = sl.id WHERE sq.quantity < 0 ORDER BY pt.name",
    },
    {
        "input": "Give me a list of overdue customer invoices over 30 days with customer names, invoice dates, amounts, and responsible salespersons.",
        "query": "SELECT rp.name AS customer_name, ai.invoice_date, ai.name AS invoice_number, ai.amount_total, ai.amount_residual, ru.login AS salesperson FROM account_move ai JOIN res_partner rp ON ai.partner_id = rp.id LEFT JOIN res_users ru ON ai.invoice_user_id = ru.id WHERE ai.move_type = 'out_invoice' AND ai.state = 'posted' AND ai.amount_residual > 0 AND ai.invoice_date <= (CURRENT_DATE - INTERVAL '30 days') ORDER BY ai.invoice_date ASC;",
    },
    {
        "input": "Show a sales performance report by salesperson for the last quarter, including total sales amount and number of orders",
        "query": "SELECT ru.login AS salesperson, COUNT(ai.id) AS number_of_orders, SUM(ai.amount_total) AS total_sales_amount FROM account_move ai JOIN res_users ru ON ai.invoice_user_id = ru.id WHERE ai.move_type = 'out_invoice' AND ai.state = 'posted' AND ai.invoice_date >= date_trunc('quarter', CURRENT_DATE) - INTERVAL '1 quarter' AND ai.invoice_date < date_trunc('quarter', CURRENT_DATE) GROUP BY ru.login ORDER BY total_sales_amount DESC;",
    },
    {
        "input": "Get list of top 10 most stocked products",
        "query": "SELECT pt.name AS product_name, pp.default_code AS sku, SUM(sq.quantity) AS total_quantity FROM stock_quant sq JOIN product_product pp ON sq.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id JOIN stock_location sl ON sq.location_id = sl.id WHERE sl.usage = 'internal' GROUP BY pt.name, pp.default_code ORDER BY total_quantity DESC LIMIT 10",
    },
    {
        "input": "Check incoming stock (stock moves to warehouse in future)",
        "query": "SELECT pt.name AS product_name, pp.default_code AS sku, sm.product_uom_qty, sm.date_expected, sl.complete_name AS destination FROM stock_move sm JOIN product_product pp ON sm.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id JOIN stock_location sl ON sm.location_dest_id = sl.id WHERE sm.state IN ('confirmed', 'assigned') AND sm.date_expected > NOW() ORDER BY sm.date_expected ASC",
    },
    {
        "input": "i want top 5 opportunities with highest expected revenue",
        "query": "SELECT name, expected_revenue FROM crm_lead WHERE type = 'opportunity' ORDER BY expected_revenue DESC LIMIT 5",
    },
    {
        "input": "I want all product name of sale order",
        "query": "SELECT so.name,rp.name, sol.id, pt.name::jsonb ->> 'en_US' FROM sale_order so JOIN res_partner rp ON so.partner_id = rp.id JOIN sale_order_line sol ON so.id = sol.order_id JOIN product_product pp ON sol.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id",
    },
    {
        "input": "List all products with quantity on hand less than 10",
        "query": "SELECT pt.name, sq.quantity FROM stock_quant sq JOIN product_product pp ON sq.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id GROUP BY pt.name, sq.quantity HAVING SUM(sq.quantity) < 10 LIMIT 10;",
    },
    {
        "input": "Get all internal transfers done this month",
        "query": "SELECT sp.* FROM stock_picking sp JOIN stock_picking_type spt ON sp.picking_type_id = spt.id WHERE spt.code = 'internal' AND sp.state = 'done' AND sp.scheduled_date::date >= date_trunc('month', current_date) ORDER BY sp.scheduled_date DESC LIMIT 10;",
    },
    {
        "input": "Find products with zero stock",
        "query": "SELECT pt.name FROM stock_quant sq JOIN product_product pp ON sq.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id GROUP BY pt.name HAVING SUM(sq.quantity) = 0 LIMIT 10;",
    },
    {
        "input": "get top 5 most stocked products",
        "query": "SELECT pt.name, SUM(sq.quantity) AS total_qty FROM stock_quant sq JOIN product_product pp ON sq.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id GROUP BY pt.name ORDER BY total_qty DESC LIMIT 5;",
    },
    {
        "input": "show all customer invoices in draft state",
        "query": "SELECT * FROM account_move WHERE move_type = 'out_invoice' AND state = 'draft' LIMIT 10",
    },
    {
        "input": "list overdue vendor bills",
        "query": "SELECT * FROM account_move WHERE move_type = 'in_invoice' AND invoice_date_due < current_date AND state = 'posted' LIMIT 10",
    },
    {
        "input": "get total balance of all accounts",
        "query": "SELECT SUM(balance) FROM account_move_line",
    },
    {
        "input": "fetch all journal entries for this year",
        "query": "SELECT * FROM account_move WHERE date >= date_trunc('year', current_date) LIMIT 10",
    },
    {
        "input": "list unpaid customer invoices",
        "query": "SELECT * FROM account_move WHERE move_type = 'out_invoice' AND payment_state != 'paid' LIMIT 10",
    },
    {
        "input": "Show all confirmed sales orders",
        "query": "SELECT so.id, so.name AS order_name, rp.id AS partner_id, rp.name AS partner_name, so.amount_total, so.date_order FROM sale_order so JOIN res_partner rp ON so.partner_id = rp.id WHERE so.state = 'sale' ORDER BY so.date_order DESC LIMIT 10;",
    },
    {
        "input": "Get top 5 customers by sales",
        "query": "SELECT rp.id AS partner_id, rp.name AS partner_name, SUM(so.amount_total) AS total_sales FROM sale_order so JOIN res_partner rp ON so.partner_id = rp.id WHERE so.state IN ('sale', 'done') GROUP BY rp.id, rp.name ORDER BY total_sales DESC LIMIT 5;",
    },
    {
        "input": "List sales orders above 5000 USD",
        "query": "SELECT so.id, so.name AS order_name, rp.id AS partner_id, rp.name AS partner_name, so.amount_total, so.date_order FROM sale_order so JOIN res_partner rp ON so.partner_id = rp.id WHERE so.amount_total > 5000 ORDER BY so.date_order DESC LIMIT 10;",
    },
    {
        "input": "Find sales orders for Azure Interior",
        "query": "SELECT so.id, so.name AS order_name, rp.id AS partner_id, rp.name AS partner_name, so.amount_total, so.date_order FROM sale_order so JOIN res_partner rp ON so.partner_id = rp.id WHERE rp.name = 'Azure Interior' ORDER BY so.date_order DESC LIMIT 10;",
    },
    {
        "input": "Get all quotations not yet confirmed",
        "query": "SELECT so.id, so.name AS order_name, rp.id AS partner_id, rp.name AS partner_name, so.amount_total, so.date_order FROM sale_order so JOIN res_partner rp ON so.partner_id = rp.id WHERE so.state = 'draft' ORDER BY so.date_order DESC LIMIT 10;",
    },
    {
        "input": "List all RFQs (Requests for Quotation)",
        "query": "SELECT po.id, po.name AS po_name, rp.id AS partner_id, rp.name AS partner_name, po.amount_total, po.date_order FROM purchase_order po JOIN res_partner rp ON po.partner_id = rp.id WHERE po.state = 'draft' ORDER BY po.date_order DESC LIMIT 10;",
    },
    {
        "input": "Get purchase orders for Deco Addict",
        "query": "SELECT po.id, po.name AS po_name, rp.id AS partner_id, rp.name AS partner_name, po.amount_total, po.date_order FROM purchase_order po JOIN res_partner rp ON po.partner_id = rp.id WHERE rp.name = 'Deco Addict' ORDER BY po.date_order DESC LIMIT 10;",
    },
    {
        "input": "Fetch received purchase orders (Confirmed POs)",
        "query": "SELECT po.id, po.name AS po_name, rp.id AS partner_id, rp.name AS partner_name, po.amount_total, po.date_order FROM purchase_order po JOIN res_partner rp ON po.partner_id = rp.id WHERE po.state = 'purchase' ORDER BY po.date_order DESC LIMIT 10;",
    },
    {
        "input": "Get top suppliers by total purchase",
        "query": "SELECT rp.id AS partner_id, rp.name AS partner_name, SUM(po.amount_total) AS total_purchase FROM purchase_order po JOIN res_partner rp ON po.partner_id = rp.id WHERE po.state IN ('purchase', 'done') GROUP BY rp.id, rp.name ORDER BY total_purchase DESC LIMIT 5;",
    },
    {
        "input": "List POs over 10,000",
        "query": "SELECT po.id, po.name AS po_name, rp.id AS partner_id, rp.name AS partner_name, po.amount_total, po.date_order FROM purchase_order po JOIN res_partner rp ON po.partner_id = rp.id WHERE po.amount_total > 10000 ORDER BY po.date_order DESC LIMIT 10;",
    },
    {
        "input": "list all active projects",
        "query": "SELECT * FROM project_project WHERE active = true LIMIT 10",
    },
    {
        "input": "get tasks under Office Design project",
        "query": "SELECT * FROM project_task WHERE project_id = (SELECT id FROM project_project WHERE name = 'Office Design') LIMIT 10",
    },
    {
        "input": "fetch high priority tasks",
        "query": "SELECT * FROM project_task WHERE priority = '3' LIMIT 10",
    },
    {
        "input": "get tasks assigned to Mitchell Admin",
        "query": "SELECT * FROM project_task WHERE user_id = (SELECT id FROM res_users WHERE name = 'Mitchell Admin') LIMIT 10",
    },
    {
        "input": "list overdue tasks",
        "query": "SELECT * FROM project_task WHERE date_deadline < current_date AND stage_id NOT IN (SELECT id FROM project_task_type WHERE name = 'Done') LIMIT 10",
    },
    {
        "input": "list all completed manufacturing orders",
        "query": "SELECT * FROM mrp_production WHERE state = 'done' LIMIT 10",
    },
    {
        "input": "get manufacturing orders for product Table",
        "query": "SELECT * FROM mrp_production WHERE product_id = (SELECT id FROM product_product WHERE name = 'Table') LIMIT 10",
    },
    {
        "input": "show pending manufacturing orders",
        "query": "SELECT * FROM mrp_production WHERE state NOT IN ('done', 'cancel') LIMIT 10",
    },
    {
        "input": "get MO created this month",
        "query": "SELECT * FROM mrp_production WHERE create_date >= date_trunc('month', current_date) LIMIT 10",
    },
    {
        "input": "find MOs with quantity > 100",
        "query": "SELECT * FROM mrp_production WHERE product_qty > 100 LIMIT 10",
    },
    {
        "input": "list open leads",
        "query": "SELECT * FROM crm_lead WHERE type = 'lead' AND stage_id NOT IN (SELECT id FROM crm_stage WHERE name = 'Won') LIMIT 10",
    },
    {
        "input": "get opportunities for Azure Interior",
        "query": "SELECT * FROM crm_lead WHERE partner_id = (SELECT id FROM res_partner WHERE name = 'Azure Interior') LIMIT 10",
    },
    {
        "input": "fetch top 5 salespeople by leads",
        "query": "SELECT user_id, COUNT(*) AS lead_count FROM crm_lead GROUP BY user_id ORDER BY lead_count DESC LIMIT 5",
    },
    {
        "input": "get won opportunities",
        "query": "SELECT * FROM crm_lead WHERE type = 'opportunity' AND stage_id IN (SELECT id FROM crm_stage WHERE name = 'Won') LIMIT 10",
    },
    {
        "input": "get leads created this week",
        "query": "SELECT * FROM crm_lead WHERE create_date >= date_trunc('week', current_date) LIMIT 10",
    },
    {
        "input": "list all delivery orders",
        "query": "SELECT * FROM stock_picking WHERE picking_type_id IN (SELECT id FROM stock_picking_type WHERE code = 'outgoing') LIMIT 10",
    },
    {
        "input": "get incoming shipments from this month",
        "query": "SELECT * FROM stock_picking WHERE picking_type_id IN (SELECT id FROM stock_picking_type WHERE code = 'incoming') AND scheduled_date >= date_trunc('month', current_date) LIMIT 10",
    },
    {
        "input": "get top 5 delivery destinations",
        "query": "SELECT partner_id, COUNT(*) AS total FROM stock_picking WHERE picking_type_id IN (SELECT id FROM stock_picking_type WHERE code = 'outgoing') GROUP BY partner_id ORDER BY total DESC LIMIT 5",
    },
    {
        "input": "list backorders",
        "query": "SELECT * FROM stock_picking WHERE backorder_id IS NOT NULL LIMIT 10",
    },
    {
        "input": "show late deliveries",
        "query": "SELECT * FROM stock_picking WHERE scheduled_date < now() AND state != 'done' LIMIT 10",
    },
    {
        "input": "List timesheet entries for Mitchell Admin",
        "query": "SELECT aal.id, aal.name AS task_description, pp.name AS project_name, aal.unit_amount, aal.date FROM account_analytic_line aal JOIN hr_employee he ON aal.employee_id = he.id LEFT JOIN project_project pp ON aal.project_id = pp.id WHERE he.name = 'Mitchell Admin' ORDER BY aal.date DESC LIMIT 10;",
    },
    {
        "input": "Get timesheets for this week",
        "query": "SELECT aal.id, aal.name AS task_description, pp.name AS project_name, aal.unit_amount, aal.date FROM account_analytic_line aal LEFT JOIN project_project pp ON aal.project_id = pp.id WHERE aal.create_date >= date_trunc('week', current_date) ORDER BY aal.date DESC LIMIT 10;",
    },
    {
        "input": "Get top 5 projects by logged hours",
        "query": "SELECT pp.id AS project_id, pp.name AS project_name, SUM(aal.unit_amount) AS total_hours FROM account_analytic_line aal JOIN project_project pp ON aal.project_id = pp.id GROUP BY pp.id, pp.name ORDER BY total_hours DESC LIMIT 5;",
    },
    {
        "input": " Get timesheets not yet validated",
        "query": "SELECT aal.id, aal.name AS task_description, pp.name AS project_name, aal.unit_amount, aal.date FROM account_analytic_line aal LEFT JOIN project_project pp ON aal.project_id = pp.id WHERE aal.validated = false ORDER BY aal.date DESC LIMIT 10;",
    },
    {
        "input": "Show timesheets over 8 hours",
        "query": "SELECT aal.id, aal.name AS task_description, pp.name AS project_name, aal.unit_amount, aal.date FROM account_analytic_line aal LEFT JOIN project_project pp ON aal.project_id = pp.id WHERE aal.unit_amount > 8 ORDER BY aal.date DESC LIMIT 10;",
    },
    {
        "input": "List all posted customer invoices",
        "query": "SELECT am.id, am.name AS invoice_number, rp.id AS partner_id, rp.name AS partner_name, am.amount_total, am.invoice_date FROM account_move am JOIN res_partner rp ON am.partner_id = rp.id WHERE am.move_type = 'out_invoice' AND am.state = 'posted' ORDER BY am.invoice_date DESC LIMIT 10;",
    },
    {
        "input": "Get unpaid vendor bills",
        "query": "SELECT am.id, am.name AS bill_number, rp.id AS partner_id, rp.name AS partner_name, am.amount_total, am.invoice_date, am.payment_state FROM account_move am JOIN res_partner rp ON am.partner_id = rp.id WHERE am.move_type = 'in_invoice' AND am.payment_state != 'paid' ORDER BY am.invoice_date DESC LIMIT 10;",
    },
    {
        "input": "Fetch invoices from this month",
        "query": "SELECT am.id, am.name AS invoice_number, rp.name AS partner_name, am.amount_total, am.invoice_date FROM account_move am LEFT JOIN res_partner rp ON am.partner_id = rp.id WHERE am.invoice_date >= date_trunc('month', current_date) ORDER BY am.invoice_date DESC LIMIT 10;",
    },
    {
        "input": "Get top 5 customers by invoiced amount",
        "query": "SELECT rp.id AS partner_id, rp.name AS partner_name, SUM(am.amount_total) AS total_invoiced FROM account_move am JOIN res_partner rp ON am.partner_id = rp.id WHERE am.move_type = 'out_invoice' GROUP BY rp.id, rp.name ORDER BY total_invoiced DESC LIMIT 5;",
    },
    {
        "input": "List draft invoices",
        "query": "SELECT am.id, am.name AS invoice_number, rp.name AS partner_name, am.amount_total, am.invoice_date FROM account_move am LEFT JOIN res_partner rp ON am.partner_id = rp.id WHERE am.state = 'draft' ORDER BY am.invoice_date DESC LIMIT 10;",
    },
    {
        "input": "Top 5 customers by ticket count",
        "query": "SELECT rp.id AS partner_id, rp.name AS partner_name, COUNT(*) AS ticket_count FROM helpdesk_ticket ht JOIN res_partner rp ON ht.partner_id = rp.id GROUP BY rp.id, rp.name ORDER BY ticket_count DESC LIMIT 5;",
    },
    {
        "input": "Tickets assigned to Mitchell Admin",
        "query": "SELECT ht.id, ht.name AS ticket_subject, rp.name AS partner_name, u.login AS assigned_user, ht.create_date FROM helpdesk_ticket ht LEFT JOIN res_partner rp ON ht.partner_id = rp.id JOIN res_users u ON ht.user_id = u.id WHERE u.login = 'Mitchell Admin' ORDER BY ht.create_date DESC LIMIT 10;",
    },
    {
        "input": "list all active employees",
        "query": "SELECT * FROM hr_employee WHERE active = true LIMIT 10",
    },
    {
        "input": "get employees hired this year",
        "query": "SELECT * FROM hr_employee WHERE create_date >= date_trunc('year', current_date) LIMIT 10",
    },
    {
        "input": "fetch employees in R&D department",
        "query": "SELECT * FROM hr_employee WHERE department_id = (SELECT id FROM hr_department WHERE name = 'Research & Development') LIMIT 10",
    },
    {
        "input": "list employees with no user account",
        "query": "SELECT * FROM hr_employee WHERE user_id IS NULL LIMIT 10",
    },
    {
        "input": "get top 5 departments by employee count",
        "query": "SELECT department_id, COUNT(*) AS total FROM hr_employee GROUP BY department_id ORDER BY total DESC LIMIT 5",
    },
]

MEMORY_FILE = "sql_agent_memory.json"


def save_memory_to_json(memory, filename="memory.json"):
    """Save conversation memory to a JSON file."""
    memory_data = memory.load_memory_variables({})

    # Convert messages to a serializable format
    if "history" in memory_data:
        memory_data["history"] = [
            {"type": type(msg).__name__, "content": msg.content}
            for msg in memory_data["history"]
        ]

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(memory_data, f, indent=4)


def load_memory_from_json(filename=MEMORY_FILE):
    """Load conversation memory from a JSON file and return a ConversationBufferMemory object."""

    memory = ConversationBufferMemory(memory_key="history", return_messages=True)

    try:
        with open(filename, "r", encoding="utf-8") as f:
            memory_data = json.load(f)

        if "history" in memory_data:
            formatted_history = []
            for msg in memory_data["history"]:
                if msg["type"] == "HumanMessage":
                    formatted_history.append(HumanMessage(content=msg["content"]))
                elif msg["type"] == "AIMessage":
                    formatted_history.append(AIMessage(content=msg["content"]))

            # Instead of modifying directly, use `save_context` to properly store history
            for i in range(0, len(formatted_history), 2):
                human_msg = formatted_history[i]
                ai_msg = (
                    formatted_history[i + 1]
                    if i + 1 < len(formatted_history)
                    else AIMessage(content="")
                )

                memory.save_context(
                    {"input": human_msg.content}, {"output": ai_msg.content}
                )

    except FileNotFoundError:
        pass

    return memory


memory = ConversationBufferMemory(
    k=10, memory_key="history", input_key="input", return_messages=True
)
loaded_memory = load_memory_from_json(MEMORY_FILE)
if loaded_memory:
    memory.chat_memory.messages = (
        loaded_memory.chat_memory.messages
    )  # Correct way to restore memory


class Response:
    def __init__(self, api_key, connection_str):
        os.environ["GOOGLE_API_KEY"] = api_key
        self.db = SQLDatabase.from_uri(connection_str)
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        self.example_selector = SemanticSimilarityExampleSelector.from_examples(
            examples,
            embeddings,
            FAISS,
            k=5,
            input_keys=["input"],
        )

        system_prefix = """You are an agent designed to interact with a SQL database.
                Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
                Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
                You have access to the following tables: {table_names}

                You can order the results by a relevant column to return the most interesting examples in the database.
                Never query for all the columns from a specific table — only request the relevant columns given the question.

                You have access to tools for interacting with the database.
                Only use the given tools. Only use the information returned by the tools to construct your final answer.
                DO NOT make statements that modify the database.
                DO NOT make any DML statements (CREATE, INSERT, UPDATE, DELETE, DROP, etc.).
                You MUST double-check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

                If the question does not seem related to the database, respond with:
                "Could you please rephrase your query in a different way?"

                Strictly return all answers in **valid JSON format**.

                ** Additional Rule **:
                - If the table or module contains an 'active' field, you MUST include `WHERE active = TRUE` (or the appropriate alias, e.g. `table_alias.active = TRUE`) in the WHERE clause of every query.
                - If multiple tables in the query have an 'active' field, ensure that each of them is filtered with `active = TRUE`.
                - This ensures only active records are retrieved from the database.
                - If the user is looking for **Sales Orders**, include:state = 'sale'
                - If the user is looking for **Quotations**, include:state NOT IN ('sale', 'cancel') 

                Here are some examples of user inputs and their corresponding SQL queries:
                """

        self.few_shot_prompt = FewShotPromptTemplate(
            example_selector=self.example_selector,
            example_prompt=PromptTemplate.from_template(
                "User input: {input}\nSQL query: {query}"
            ),
            input_variables=["input", "dialect", "top_k"],
            prefix=self.system_prefix,
            suffix="",
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.full_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate(prompt=self.few_shot_prompt),
                MessagesPlaceholder(variable_name="history"),  # Add memory
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        self.agent_executor = create_sql_agent(
            llm=self.llm,
            toolkit=SQLDatabaseToolkit(db=self.db, llm=self.llm),
            # verbose=True,
            agent_executor_kwargs={"memory": memory},
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        )

    def classify_intent(self, user_input):

        template2 = """ User Input: {text}
        Criteria:
        - If the input suggests a typical conversation or a text generation task, assign 'Discovery' to 'true' in the JSON response.If the input was normal question assign 'Discovery' to 'true' in the JSON response.
        - If the input resembles a own database query, assign 'Discovery' to 'false' in the JSON response.
        Put your true or false value in this JSON data, and give me that JSOn data only: ('Discovery':true/false)
        important note: Make sure your return proper JSON data with curly braces and key-value pairs.Do not return except json data.This is my stric instruction.
        """

        prompt = PromptTemplate.from_template(template2)
        llm_chain = prompt | self.llm
        text = llm_chain.invoke({"text": user_input})
        text = text.content.replace("```json", "").replace("```", "")

        Discovery = json.loads(text)
        return Discovery

    # Process the user input
    def process_user_input(self, user_input):
        # Classify the intent of the user input
        intent = self.classify_intent(user_input)
        # Template for discovery-related queries
        template = """Question: {text}\nYou are an expert Odoo assistant. Help users with navigating, configuring, and troubleshooting various Odoo modules like Sales, Inventory, Accounting, CRM, Purchase, and more. Respond in a clear, concise manner and provide step-by-step guidance when needed."""
        prompt = PromptTemplate.from_template(template)
        llm_chain = prompt | self.llm
        if intent.get("Discovery") is True:
            response = llm_chain.invoke({"text": user_input})
            return (
                response.content
                if hasattr(response, "content")
                else response.get("text", response)
            )
        else:
            response = self.agent_executor.invoke({"input": user_input + " , IN json"})
            response = response.get("output").replace("```json", "").replace("```", "")
            try:
                response = json.loads(response)
            except:
                response = None
            if response is None or response == "I don't know" or response == []:
                response = llm_chain.invoke({"text": user_input})
                return (
                    response.content
                    if hasattr(response, "content")
                    else response.get("text", response)
                )
            return response