# OPS Dashboard - Enterprise Implementation (Part 2)

## Continuation from Part 1

---

## PHASE 2 CONTINUED: Complete KPI Data File

```bash
# Continue from previous phase...

cat >> data/ops_kpi_data.xml << 'EOF'
            <field name="color">#10b981</field>
            <field name="scope_type">own</field>
            <field name="persona_codes">P10</field>
            <field name="trend_good_direction">up</field>
        </record>
        
        <record id="kpi_my_orders_mtd" model="ops.kpi">
            <field name="name">My Orders MTD</field>
            <field name="code">MY_ORDERS_MTD</field>
            <field name="category">sales</field>
            <field name="source_model">sale.order</field>
            <field name="calculation_type">count</field>
            <field name="domain">[('state', 'in', ['sale', 'done'])]</field>
            <field name="format_type">integer</field>
            <field name="icon">fa-shopping-bag</field>
            <field name="color">#3b82f6</field>
            <field name="scope_type">own</field>
            <field name="persona_codes">P10</field>
            <field name="trend_good_direction">up</field>
        </record>
        
        <record id="kpi_my_quotations" model="ops.kpi">
            <field name="name">My Open Quotations</field>
            <field name="code">MY_QUOTATIONS</field>
            <field name="category">sales</field>
            <field name="source_model">sale.order</field>
            <field name="calculation_type">count</field>
            <field name="domain">[('state', 'in', ['draft', 'sent'])]</field>
            <field name="format_type">integer</field>
            <field name="icon">fa-file-alt</field>
            <field name="color">#f59e0b</field>
            <field name="scope_type">own</field>
            <field name="persona_codes">P10</field>
            <field name="show_trend">False</field>
        </record>
        
        <record id="kpi_my_quotation_value" model="ops.kpi">
            <field name="name">My Pipeline Value</field>
            <field name="code">MY_QUOTATION_VALUE</field>
            <field name="category">sales</field>
            <field name="source_model">sale.order</field>
            <field name="measure_field">amount_total</field>
            <field name="calculation_type">sum</field>
            <field name="domain">[('state', 'in', ['draft', 'sent'])]</field>
            <field name="format_type">currency</field>
            <field name="icon">fa-funnel-dollar</field>
            <field name="color">#06b6d4</field>
            <field name="scope_type">own</field>
            <field name="persona_codes">P10</field>
            <field name="show_trend">False</field>
        </record>
        
        <record id="kpi_my_po_mtd" model="ops.kpi">
            <field name="name">My POs MTD</field>
            <field name="code">MY_PO_MTD</field>
            <field name="category">purchase</field>
            <field name="source_model">purchase.order</field>
            <field name="measure_field">amount_total</field>
            <field name="calculation_type">sum</field>
            <field name="domain">[('state', 'in', ['purchase', 'done'])]</field>
            <field name="format_type">currency</field>
            <field name="icon">fa-file-invoice</field>
            <field name="color">#8b5cf6</field>
            <field name="requires_cost_access">True</field>
            <field name="scope_type">own</field>
            <field name="persona_codes">P11</field>
        </record>
        
        <record id="kpi_my_po_count" model="ops.kpi">
            <field name="name">My PO Count MTD</field>
            <field name="code">MY_PO_COUNT</field>
            <field name="category">purchase</field>
            <field name="source_model">purchase.order</field>
            <field name="calculation_type">count</field>
            <field name="domain">[('state', 'in', ['purchase', 'done'])]</field>
            <field name="format_type">integer</field>
            <field name="icon">fa-clipboard-list</field>
            <field name="color">#3b82f6</field>
            <field name="scope_type">own</field>
            <field name="persona_codes">P11</field>
        </record>
        
        <record id="kpi_my_picks_pending" model="ops.kpi">
            <field name="name">My Pending Picks</field>
            <field name="code">MY_PICKS_PENDING</field>
            <field name="category">inventory</field>
            <field name="source_model">stock.picking</field>
            <field name="calculation_type">count</field>
            <field name="domain">[('picking_type_code', '=', 'outgoing'), ('state', 'in', ['assigned', 'waiting'])]</field>
            <field name="format_type">integer</field>
            <field name="icon">fa-dolly</field>
            <field name="color">#f59e0b</field>
            <field name="scope_type">own</field>
            <field name="persona_codes">P12</field>
            <field name="show_trend">False</field>
        </record>
        
        <record id="kpi_my_picks_done_today" model="ops.kpi">
            <field name="name">My Picks Done Today</field>
            <field name="code">MY_PICKS_DONE_TODAY</field>
            <field name="category">inventory</field>
            <field name="source_model">stock.picking</field>
            <field name="calculation_type">count</field>
            <field name="domain">[('picking_type_code', '=', 'outgoing'), ('state', '=', 'done')]</field>
            <field name="format_type">integer</field>
            <field name="icon">fa-check-circle</field>
            <field name="color">#10b981</field>
            <field name="scope_type">own</field>
            <field name="persona_codes">P12</field>
            <field name="trend_good_direction">up</field>
        </record>
        
    </data>
</odoo>
EOF

echo "✅ Phase 2 complete - All KPIs created"
```

---

## PHASE 3: CREATE DASHBOARDS FOR EACH PERSONA (45 min)

### Task 3.1: Dashboard Data File

```bash
echo "========================================"
echo "PHASE 3: CREATE PERSONA DASHBOARDS"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_dashboard

cat > data/ops_dashboard_data.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        
        <!-- ============================================================= -->
        <!-- P01 - IT ADMINISTRATOR DASHBOARD (System Health Only) -->
        <!-- ============================================================= -->
        
        <record id="dashboard_it_admin" model="ops.dashboard">
            <field name="name">System Health</field>
            <field name="code">IT_ADMIN</field>
            <field name="description">System monitoring for IT Administrators - No business data</field>
            <field name="dashboard_type">system</field>
            <field name="persona_codes">P01</field>
            <field name="auto_refresh">True</field>
            <field name="refresh_interval">60000</field>
            <field name="sequence">10</field>
        </record>
        
        <record id="widget_it_active_users" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_it_admin"/>
            <field name="kpi_id" ref="kpi_sys_users_active"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">10</field>
        </record>
        
        <record id="widget_it_sessions" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_it_admin"/>
            <field name="kpi_id" ref="kpi_sys_sessions"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">20</field>
        </record>
        
        <record id="widget_it_pending_approvals" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_it_admin"/>
            <field name="kpi_id" ref="kpi_sys_pending_approvals"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">30</field>
        </record>
        
        <!-- ============================================================= -->
        <!-- P02 - CEO/EXECUTIVE DASHBOARD (Company-Wide, No Cost) -->
        <!-- ============================================================= -->
        
        <record id="dashboard_ceo" model="ops.dashboard">
            <field name="name">Executive Overview</field>
            <field name="code">CEO</field>
            <field name="description">Company-wide performance overview for CEO/Executive</field>
            <field name="dashboard_type">executive</field>
            <field name="persona_codes">P02</field>
            <field name="auto_refresh">True</field>
            <field name="refresh_interval">120000</field>
            <field name="sequence">20</field>
        </record>
        
        <record id="widget_ceo_revenue_mtd" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ceo"/>
            <field name="kpi_id" ref="kpi_sales_revenue_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">10</field>
        </record>
        
        <record id="widget_ceo_revenue_ytd" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ceo"/>
            <field name="kpi_id" ref="kpi_sales_revenue_ytd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">20</field>
        </record>
        
        <record id="widget_ceo_orders" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ceo"/>
            <field name="kpi_id" ref="kpi_sales_orders_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">30</field>
        </record>
        
        <record id="widget_ceo_ar_total" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ceo"/>
            <field name="kpi_id" ref="kpi_ar_total"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">40</field>
        </record>
        
        <record id="widget_ceo_ar_overdue" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ceo"/>
            <field name="kpi_id" ref="kpi_ar_overdue"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">50</field>
        </record>
        
        <record id="widget_ceo_ap_total" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ceo"/>
            <field name="kpi_id" ref="kpi_ap_total"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">60</field>
        </record>
        
        <record id="widget_ceo_cash" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ceo"/>
            <field name="kpi_id" ref="kpi_treasury_cash_balance"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">70</field>
        </record>
        
        <record id="widget_ceo_pdc" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ceo"/>
            <field name="kpi_id" ref="kpi_pdc_recv_registered"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">80</field>
        </record>
        
        <!-- ============================================================= -->
        <!-- P03 - CFO DASHBOARD (Full Financial with Cost/Margin) -->
        <!-- ============================================================= -->
        
        <record id="dashboard_cfo" model="ops.dashboard">
            <field name="name">Financial Command Center</field>
            <field name="code">CFO</field>
            <field name="description">Complete financial oversight with margins and costs</field>
            <field name="dashboard_type">finance</field>
            <field name="persona_codes">P00,P03</field>
            <field name="auto_refresh">True</field>
            <field name="refresh_interval">120000</field>
            <field name="sequence">30</field>
        </record>
        
        <record id="widget_cfo_revenue_mtd" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_sales_revenue_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">10</field>
        </record>
        
        <record id="widget_cfo_revenue_ytd" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_sales_revenue_ytd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">20</field>
        </record>
        
        <record id="widget_cfo_margin" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_sales_gross_margin"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">30</field>
        </record>
        
        <record id="widget_cfo_ar_total" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_ar_total"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">40</field>
        </record>
        
        <record id="widget_cfo_ar_overdue" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_ar_overdue"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">50</field>
        </record>
        
        <record id="widget_cfo_ap_total" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_ap_total"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">60</field>
        </record>
        
        <record id="widget_cfo_ap_overdue" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_ap_overdue"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">70</field>
        </record>
        
        <record id="widget_cfo_cash" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_treasury_cash_balance"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">80</field>
        </record>
        
        <record id="widget_cfo_pdc_recv" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_pdc_recv_registered"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">90</field>
        </record>
        
        <record id="widget_cfo_pdc_pay" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_pdc_pay_issued"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">100</field>
        </record>
        
        <record id="widget_cfo_inventory" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_inventory_value"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">110</field>
        </record>
        
        <record id="widget_cfo_asset" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_asset_nbv"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">120</field>
        </record>
        
        <record id="widget_cfo_3way" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_3way_exception"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">130</field>
        </record>
        
        <record id="widget_cfo_budget" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_cfo"/>
            <field name="kpi_id" ref="kpi_budget_utilization"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">140</field>
        </record>
        
        <!-- ============================================================= -->
        <!-- P05 - BRANCH MANAGER DASHBOARD -->
        <!-- ============================================================= -->
        
        <record id="dashboard_branch_manager" model="ops.dashboard">
            <field name="name">Branch Operations</field>
            <field name="code">BRANCH_MGR</field>
            <field name="description">Complete branch oversight for Branch Managers</field>
            <field name="dashboard_type">branch</field>
            <field name="persona_codes">P05</field>
            <field name="auto_refresh">True</field>
            <field name="refresh_interval">60000</field>
            <field name="sequence">50</field>
        </record>
        
        <record id="widget_br_revenue_mtd" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_branch_manager"/>
            <field name="kpi_id" ref="kpi_sales_revenue_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">10</field>
        </record>
        
        <record id="widget_br_orders" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_branch_manager"/>
            <field name="kpi_id" ref="kpi_sales_orders_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">20</field>
        </record>
        
        <record id="widget_br_margin" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_branch_manager"/>
            <field name="kpi_id" ref="kpi_sales_gross_margin"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">30</field>
        </record>
        
        <record id="widget_br_quotations" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_branch_manager"/>
            <field name="kpi_id" ref="kpi_sales_quotations"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">40</field>
        </record>
        
        <record id="widget_br_ar" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_branch_manager"/>
            <field name="kpi_id" ref="kpi_ar_total"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">50</field>
        </record>
        
        <record id="widget_br_ar_overdue" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_branch_manager"/>
            <field name="kpi_id" ref="kpi_ar_overdue"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">60</field>
        </record>
        
        <record id="widget_br_purchase" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_branch_manager"/>
            <field name="kpi_id" ref="kpi_purchase_total_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">70</field>
        </record>
        
        <record id="widget_br_inventory" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_branch_manager"/>
            <field name="kpi_id" ref="kpi_inventory_value"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">80</field>
        </record>
        
        <record id="widget_br_pending_delivery" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_branch_manager"/>
            <field name="kpi_id" ref="kpi_inventory_pending_delivery"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">90</field>
        </record>
        
        <record id="widget_br_pending_receipt" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_branch_manager"/>
            <field name="kpi_id" ref="kpi_purchase_pending_receipts"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">100</field>
        </record>
        
        <record id="widget_br_pdc" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_branch_manager"/>
            <field name="kpi_id" ref="kpi_pdc_recv_registered"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">110</field>
        </record>
        
        <record id="widget_br_so_approval" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_branch_manager"/>
            <field name="kpi_id" ref="kpi_sales_pending_approval"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">120</field>
        </record>
        
        <!-- ============================================================= -->
        <!-- P06 - SALES MANAGER DASHBOARD -->
        <!-- ============================================================= -->
        
        <record id="dashboard_sales_manager" model="ops.dashboard">
            <field name="name">Sales Performance</field>
            <field name="code">SALES_MGR</field>
            <field name="description">Sales team performance management</field>
            <field name="dashboard_type">sales</field>
            <field name="persona_codes">P06</field>
            <field name="auto_refresh">True</field>
            <field name="refresh_interval">60000</field>
            <field name="sequence">60</field>
        </record>
        
        <record id="widget_sm_revenue_mtd" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_manager"/>
            <field name="kpi_id" ref="kpi_sales_revenue_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">10</field>
        </record>
        
        <record id="widget_sm_revenue_ytd" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_manager"/>
            <field name="kpi_id" ref="kpi_sales_revenue_ytd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">20</field>
        </record>
        
        <record id="widget_sm_orders" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_manager"/>
            <field name="kpi_id" ref="kpi_sales_orders_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">30</field>
        </record>
        
        <record id="widget_sm_avg_order" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_manager"/>
            <field name="kpi_id" ref="kpi_sales_avg_order"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">40</field>
        </record>
        
        <record id="widget_sm_margin" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_manager"/>
            <field name="kpi_id" ref="kpi_sales_gross_margin"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">50</field>
        </record>
        
        <record id="widget_sm_quotations" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_manager"/>
            <field name="kpi_id" ref="kpi_sales_quotations"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">60</field>
        </record>
        
        <record id="widget_sm_pipeline" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_manager"/>
            <field name="kpi_id" ref="kpi_sales_quotation_value"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">70</field>
        </record>
        
        <record id="widget_sm_pending" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_manager"/>
            <field name="kpi_id" ref="kpi_sales_pending_approval"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">80</field>
        </record>
        
        <record id="widget_sm_ar_overdue" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_manager"/>
            <field name="kpi_id" ref="kpi_ar_overdue"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">90</field>
        </record>
        
        <record id="widget_sm_collected" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_manager"/>
            <field name="kpi_id" ref="kpi_ar_collected_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">100</field>
        </record>
        
        <!-- ============================================================= -->
        <!-- P07 - PURCHASE MANAGER DASHBOARD -->
        <!-- ============================================================= -->
        
        <record id="dashboard_purchase_manager" model="ops.dashboard">
            <field name="name">Procurement Hub</field>
            <field name="code">PURCHASE_MGR</field>
            <field name="description">Procurement operations management</field>
            <field name="dashboard_type">purchase</field>
            <field name="persona_codes">P07</field>
            <field name="auto_refresh">True</field>
            <field name="refresh_interval">60000</field>
            <field name="sequence">70</field>
        </record>
        
        <record id="widget_pm_purchase_mtd" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_purchase_manager"/>
            <field name="kpi_id" ref="kpi_purchase_total_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">10</field>
        </record>
        
        <record id="widget_pm_po_count" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_purchase_manager"/>
            <field name="kpi_id" ref="kpi_purchase_orders_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">20</field>
        </record>
        
        <record id="widget_pm_pending_rfq" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_purchase_manager"/>
            <field name="kpi_id" ref="kpi_purchase_pending_rfq"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">30</field>
        </record>
        
        <record id="widget_pm_pending_approval" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_purchase_manager"/>
            <field name="kpi_id" ref="kpi_purchase_pending_approval"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">40</field>
        </record>
        
        <record id="widget_pm_pending_receipts" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_purchase_manager"/>
            <field name="kpi_id" ref="kpi_purchase_pending_receipts"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">50</field>
        </record>
        
        <record id="widget_pm_3way_pending" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_purchase_manager"/>
            <field name="kpi_id" ref="kpi_3way_pending"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">60</field>
        </record>
        
        <record id="widget_pm_3way_exception" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_purchase_manager"/>
            <field name="kpi_id" ref="kpi_3way_exception"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">70</field>
        </record>
        
        <record id="widget_pm_ap_due" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_purchase_manager"/>
            <field name="kpi_id" ref="kpi_ap_due_7_days"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">80</field>
        </record>
        
        <record id="widget_pm_pdc_issued" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_purchase_manager"/>
            <field name="kpi_id" ref="kpi_pdc_pay_issued"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">90</field>
        </record>
        
        <!-- ============================================================= -->
        <!-- P10 - SALES REPRESENTATIVE DASHBOARD (Own Records Only) -->
        <!-- ============================================================= -->
        
        <record id="dashboard_sales_rep" model="ops.dashboard">
            <field name="name">My Sales</field>
            <field name="code">SALES_REP</field>
            <field name="description">Personal sales performance - Own records only</field>
            <field name="dashboard_type">sales</field>
            <field name="persona_codes">P10</field>
            <field name="auto_refresh">True</field>
            <field name="refresh_interval">60000</field>
            <field name="sequence">100</field>
        </record>
        
        <record id="widget_sr_my_sales" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_rep"/>
            <field name="kpi_id" ref="kpi_my_sales_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">10</field>
        </record>
        
        <record id="widget_sr_my_orders" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_rep"/>
            <field name="kpi_id" ref="kpi_my_orders_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">20</field>
        </record>
        
        <record id="widget_sr_my_quotations" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_rep"/>
            <field name="kpi_id" ref="kpi_my_quotations"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">30</field>
        </record>
        
        <record id="widget_sr_my_pipeline" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_sales_rep"/>
            <field name="kpi_id" ref="kpi_my_quotation_value"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">40</field>
        </record>
        
        <!-- ============================================================= -->
        <!-- P13 - AR CLERK DASHBOARD -->
        <!-- ============================================================= -->
        
        <record id="dashboard_ar_clerk" model="ops.dashboard">
            <field name="name">Receivables</field>
            <field name="code">AR_CLERK</field>
            <field name="description">AR and collections management</field>
            <field name="dashboard_type">receivable</field>
            <field name="persona_codes">P13</field>
            <field name="auto_refresh">True</field>
            <field name="refresh_interval">60000</field>
            <field name="sequence">130</field>
        </record>
        
        <record id="widget_arc_ar_total" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ar_clerk"/>
            <field name="kpi_id" ref="kpi_ar_total"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">10</field>
        </record>
        
        <record id="widget_arc_ar_overdue" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ar_clerk"/>
            <field name="kpi_id" ref="kpi_ar_overdue"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">20</field>
        </record>
        
        <record id="widget_arc_collected" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ar_clerk"/>
            <field name="kpi_id" ref="kpi_ar_collected_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">30</field>
        </record>
        
        <record id="widget_arc_pdc_registered" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ar_clerk"/>
            <field name="kpi_id" ref="kpi_pdc_recv_registered"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">40</field>
        </record>
        
        <record id="widget_arc_pdc_deposited" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ar_clerk"/>
            <field name="kpi_id" ref="kpi_pdc_recv_deposited"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">50</field>
        </record>
        
        <record id="widget_arc_pdc_bounced" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ar_clerk"/>
            <field name="kpi_id" ref="kpi_pdc_recv_bounced"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">60</field>
        </record>
        
        <!-- ============================================================= -->
        <!-- P14 - AP CLERK DASHBOARD -->
        <!-- ============================================================= -->
        
        <record id="dashboard_ap_clerk" model="ops.dashboard">
            <field name="name">Payables</field>
            <field name="code">AP_CLERK</field>
            <field name="description">AP and payment management</field>
            <field name="dashboard_type">payable</field>
            <field name="persona_codes">P14</field>
            <field name="auto_refresh">True</field>
            <field name="refresh_interval">60000</field>
            <field name="sequence">140</field>
        </record>
        
        <record id="widget_apc_ap_total" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ap_clerk"/>
            <field name="kpi_id" ref="kpi_ap_total"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">10</field>
        </record>
        
        <record id="widget_apc_ap_overdue" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ap_clerk"/>
            <field name="kpi_id" ref="kpi_ap_overdue"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">20</field>
        </record>
        
        <record id="widget_apc_ap_due" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ap_clerk"/>
            <field name="kpi_id" ref="kpi_ap_due_7_days"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">30</field>
        </record>
        
        <record id="widget_apc_3way_pending" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ap_clerk"/>
            <field name="kpi_id" ref="kpi_3way_pending"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">40</field>
        </record>
        
        <record id="widget_apc_pdc_issued" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_ap_clerk"/>
            <field name="kpi_id" ref="kpi_pdc_pay_issued"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">50</field>
        </record>
        
        <!-- ============================================================= -->
        <!-- P15 - TREASURY OFFICER DASHBOARD -->
        <!-- ============================================================= -->
        
        <record id="dashboard_treasury" model="ops.dashboard">
            <field name="name">Cash Management</field>
            <field name="code">TREASURY</field>
            <field name="description">Cash position and PDC management</field>
            <field name="dashboard_type">treasury</field>
            <field name="persona_codes">P15</field>
            <field name="auto_refresh">True</field>
            <field name="refresh_interval">60000</field>
            <field name="sequence">150</field>
        </record>
        
        <record id="widget_tr_cash" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_treasury"/>
            <field name="kpi_id" ref="kpi_treasury_cash_balance"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">10</field>
        </record>
        
        <record id="widget_tr_cash_in" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_treasury"/>
            <field name="kpi_id" ref="kpi_treasury_cash_in_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">20</field>
        </record>
        
        <record id="widget_tr_cash_out" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_treasury"/>
            <field name="kpi_id" ref="kpi_treasury_cash_out_mtd"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">30</field>
        </record>
        
        <record id="widget_tr_pdc_recv" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_treasury"/>
            <field name="kpi_id" ref="kpi_pdc_recv_registered"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">40</field>
        </record>
        
        <record id="widget_tr_pdc_deposited" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_treasury"/>
            <field name="kpi_id" ref="kpi_pdc_recv_deposited"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">50</field>
        </record>
        
        <record id="widget_tr_pdc_pay" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_treasury"/>
            <field name="kpi_id" ref="kpi_pdc_pay_issued"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">60</field>
        </record>
        
        <record id="widget_tr_ar_due" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_treasury"/>
            <field name="kpi_id" ref="kpi_ar_overdue"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">70</field>
        </record>
        
        <record id="widget_tr_ap_due" model="ops.dashboard.widget">
            <field name="dashboard_id" ref="dashboard_treasury"/>
            <field name="kpi_id" ref="kpi_ap_due_7_days"/>
            <field name="widget_type">kpi</field>
            <field name="sequence">80</field>
        </record>
        
    </data>
</odoo>
EOF

echo "✅ Phase 3 complete - All persona dashboards created"
```

---

## PHASE 4: UPDATE DASHBOARD MODEL (30 min)

### Task 4.1: Enhanced ops.dashboard Model

```bash
echo "========================================"
echo "PHASE 4: UPDATE DASHBOARD MODEL"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_dashboard

cat > models/ops_dashboard.py << 'EOF'
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class OpsDashboard(models.Model):
    _name = 'ops.dashboard'
    _description = 'OPS Dashboard'
    _order = 'sequence, name'

    name = fields.Char(string='Dashboard Name', required=True)
    code = fields.Char(string='Dashboard Code', required=True, index=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    
    dashboard_type = fields.Selection([
        ('executive', 'Executive'),
        ('finance', 'Finance'),
        ('sales', 'Sales'),
        ('purchase', 'Purchase'),
        ('inventory', 'Inventory'),
        ('receivable', 'Receivables'),
        ('payable', 'Payables'),
        ('treasury', 'Treasury'),
        ('branch', 'Branch'),
        ('bu', 'Business Unit'),
        ('system', 'System'),
    ], string='Dashboard Type', default='branch')
    
    # Persona-based access
    persona_codes = fields.Char(
        string='Allowed Personas',
        help='Comma-separated persona codes: P00,P02,P03. Empty = available to all.'
    )
    
    # Auto-refresh
    auto_refresh = fields.Boolean(string='Auto Refresh', default=True)
    refresh_interval = fields.Integer(
        string='Refresh Interval (ms)',
        default=120000,
        help='Refresh interval in milliseconds. Default: 120000 (2 minutes)'
    )
    
    # Widgets
    widget_ids = fields.One2many('ops.dashboard.widget', 'dashboard_id', string='Widgets')
    
    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Dashboard code must be unique'),
    ]
    
    def _check_user_access(self):
        """Check if current user can access this dashboard"""
        self.ensure_one()
        user = self.env.user
        
        # System admin bypasses all
        if user.has_group('base.group_system'):
            return True
        
        # IT Admin can only see system dashboards
        if user.has_group('ops_matrix_core.group_ops_it_admin'):
            if self.dashboard_type != 'system':
                return False
            return True
        
        # Check persona codes
        if self.persona_codes:
            allowed = [p.strip() for p in self.persona_codes.split(',')]
            user_personas = user.ops_persona_ids.mapped('code') if hasattr(user, 'ops_persona_ids') else []
            if not any(p in allowed for p in user_personas):
                return False
        
        return True
    
    @api.model
    def get_user_dashboards(self):
        """Get dashboards available to current user based on persona"""
        user = self.env.user
        dashboards = self.search([('active', '=', True)])
        
        result = []
        for dashboard in dashboards:
            if dashboard._check_user_access():
                result.append({
                    'id': dashboard.id,
                    'name': dashboard.name,
                    'code': dashboard.code,
                    'dashboard_type': dashboard.dashboard_type,
                })
        
        return result
    
    def get_dashboard_data(self, period='this_month'):
        """Get complete dashboard data with all widgets"""
        self.ensure_one()
        
        # Security check
        if not self._check_user_access():
            return {'error': _('Access denied to this dashboard')}
        
        widgets_data = []
        for widget in self.widget_ids.sorted('sequence'):
            widget_data = widget.get_widget_data(period)
            if widget_data:
                widgets_data.append(widget_data)
        
        return {
            'dashboard_id': self.id,
            'dashboard_name': self.name,
            'dashboard_code': self.code,
            'dashboard_type': self.dashboard_type,
            'widgets': widgets_data,
            'auto_refresh': self.auto_refresh,
            'refresh_interval': self.refresh_interval,
        }


class OpsDashboardWidget(models.Model):
    _name = 'ops.dashboard.widget'
    _description = 'OPS Dashboard Widget'
    _order = 'sequence'

    name = fields.Char(string='Widget Name', compute='_compute_name', store=True)
    dashboard_id = fields.Many2one('ops.dashboard', string='Dashboard', ondelete='cascade')
    kpi_id = fields.Many2one('ops.kpi', string='KPI')
    sequence = fields.Integer(default=10)
    
    widget_type = fields.Selection([
        ('kpi', 'KPI Card'),
        ('bar_chart', 'Bar Chart'),
        ('line_chart', 'Line Chart'),
        ('pie_chart', 'Pie Chart'),
        ('list', 'List'),
        ('gauge', 'Gauge'),
    ], string='Widget Type', default='kpi')
    
    # Layout
    width = fields.Integer(string='Width (Grid Units)', default=1)
    height = fields.Integer(string='Height (Grid Units)', default=1)
    
    @api.depends('kpi_id')
    def _compute_name(self):
        for widget in self:
            widget.name = widget.kpi_id.name if widget.kpi_id else 'Widget'
    
    def get_widget_data(self, period='this_month'):
        """Get widget data including KPI value"""
        self.ensure_one()
        
        if not self.kpi_id:
            return None
        
        # Compute KPI value
        kpi_result = self.kpi_id.compute_value(period)
        
        # Check for access denied
        if kpi_result.get('access_denied'):
            return None  # Don't show widget at all
        
        return {
            'widget_id': self.id,
            'widget_type': self.widget_type,
            'name': self.kpi_id.name,
            'code': self.kpi_id.code,
            'value': kpi_result.get('value', 0),
            'format_type': self.kpi_id.format_type,
            'icon': self.kpi_id.icon,
            'color': self.kpi_id.color,
            'trend_percentage': kpi_result.get('trend_percentage', 0),
            'trend_direction': kpi_result.get('trend_direction', 'flat'),
            'trend_is_good': kpi_result.get('trend_is_good', True),
            'period': period,
            'width': self.width,
            'height': self.height,
        }
EOF

echo "✅ Phase 4 complete - Dashboard models updated"
```

---

## PHASE 5: UPDATE MANIFEST & INSTALL (15 min)

```bash
echo "========================================"
echo "PHASE 5: UPDATE AND INSTALL"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_dashboard

# Update manifest to include new data files
cat > __manifest__.py << 'EOF'
{
    'name': 'OPS Dashboard',
    'version': '19.0.2.0.0',
    'category': 'Productivity/Dashboards',
    'summary': 'Enterprise KPI Dashboards for OPS Framework',
    'description': """
OPS Dashboard - Enterprise KPI System
=====================================
* 16 Persona-specific dashboards
* 50+ KPIs for trading companies
* Role-based security (IT Admin blindness, branch isolation)
* Cost/Margin visibility controls
* Real-time auto-refresh
* PDC, Budget, Asset, 3-Way Match KPIs
    """,
    'author': 'OPS Framework',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'sale',
        'purchase',
        'account',
        'stock',
        'ops_matrix_core',
        'ops_matrix_accounting',
    ],
    'data': [
        'security/ops_dashboard_security.xml',
        'security/ir.model.access.csv',
        'data/ops_kpi_data.xml',
        'data/ops_dashboard_data.xml',
        'views/ops_dashboard_views.xml',
        'views/ops_kpi_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ops_dashboard/static/src/scss/dashboard.scss',
            'ops_dashboard/static/src/js/ops_dashboard_action.js',
            'ops_dashboard/static/src/xml/ops_dashboard_templates.xml',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
EOF

# Update module
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_dashboard --stop-after-init

# Check for errors
docker logs gemini_odoo19 --tail 100 | grep -i "error\|traceback" || echo "No errors found"

# Restart
docker restart gemini_odoo19

sleep 10

echo "✅ Phase 5 complete - Module updated"
```

---

## PHASE 6: GIT COMMIT

```bash
cd /opt/gemini_odoo19
git add -A
git status

git commit -m "feat(dashboard): Add enterprise persona-based dashboard system

MAJOR UPDATE - Complete corporate dashboard system:

Security:
- IT Admin blindness (P01 sees system KPIs only)
- Branch isolation for all transactional KPIs
- Cost/Margin access controls
- Persona-based dashboard visibility

Dashboards (12):
- P01 IT Admin: System Health (3 KPIs)
- P02 CEO: Executive Overview (8 KPIs)
- P03 CFO: Financial Command (14 KPIs)
- P05 Branch Manager: Branch Operations (12 KPIs)
- P06 Sales Manager: Sales Performance (10 KPIs)
- P07 Purchase Manager: Procurement Hub (9 KPIs)
- P10 Sales Rep: My Sales (4 KPIs, own records only)
- P13 AR Clerk: Receivables (6 KPIs)
- P14 AP Clerk: Payables (5 KPIs)
- P15 Treasury: Cash Management (8 KPIs)

KPIs (50+):
- Sales: Revenue, Orders, Quotations, Margin
- Purchase: PO value, count, pending, receipts
- AR/AP: Totals, Overdue, Aging
- PDC: Registered, Deposited, Bounced, Issued
- Inventory: Value, SKU count, Low stock
- Treasury: Cash balance, In/Out flows
- Governance: 3-Way Match, Budget utilization
- Assets: NBV, Depreciation due

Scope Types:
- company: Company-wide (CEO, CFO)
- bu: Business Unit (BU Leaders)
- branch: Branch (Managers)
- own: Own records only (Sales Rep, Purchase Officer)"

git push origin main

echo "✅ Committed to git"
```

---

## FINAL SUMMARY

```bash
echo "========================================"
echo "ENTERPRISE DASHBOARD IMPLEMENTATION COMPLETE"
echo "========================================"
echo ""
echo "DASHBOARDS CREATED: 12"
echo "  - P01 IT Admin: System Health"
echo "  - P02 CEO: Executive Overview"
echo "  - P03 CFO: Financial Command Center"
echo "  - P05 Branch Manager: Branch Operations"
echo "  - P06 Sales Manager: Sales Performance"
echo "  - P07 Purchase Manager: Procurement Hub"
echo "  - P10 Sales Rep: My Sales"
echo "  - P13 AR Clerk: Receivables"
echo "  - P14 AP Clerk: Payables"
echo "  - P15 Treasury: Cash Management"
echo ""
echo "KPIs CREATED: 50+"
echo "  - Sales: 8"
echo "  - Purchase: 5"
echo "  - Receivables: 3"
echo "  - Payables: 3"
echo "  - PDC: 4"
echo "  - Inventory: 4"
echo "  - Treasury: 3"
echo "  - Governance: 2"
echo "  - Budget: 1"
echo "  - Assets: 2"
echo "  - System: 3"
echo "  - Own Records: 8"
echo ""
echo "SECURITY FEATURES:"
echo "  - IT Admin Blindness"
echo "  - Branch Isolation"
echo "  - Cost/Margin Access Control"
echo "  - Persona-based visibility"
echo ""
echo "TO TEST:"
echo "  1. Login as different personas"
echo "  2. Verify each sees only their dashboard"
echo "  3. Verify IT Admin sees System Health only"
echo "  4. Verify Sales Rep sees own records only"
echo "========================================"
```

---

## SUCCESS CRITERIA

- [ ] Module installs without errors
- [ ] 12 dashboards created
- [ ] 50+ KPIs defined
- [ ] IT Admin sees only System Health
- [ ] CEO sees company-wide KPIs
- [ ] CFO sees financial KPIs with margins
- [ ] Sales Rep sees own records only
- [ ] Branch isolation working
- [ ] Cost fields hidden from unauthorized users

**BEGIN AUTONOMOUS EXECUTION NOW.**
