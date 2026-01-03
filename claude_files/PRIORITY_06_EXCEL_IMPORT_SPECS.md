# Priority #6: Excel Import for Sale Order Lines - Technical Specifications

**Priority**: #6 - CRITICAL  
**Estimated Effort**: 2-3 sessions  
**Status**: READY FOR DEVELOPMENT  
**Next Session**: To be assigned to RooCode

---

## Overview

Create a wizard that allows users to import sale order lines from Excel files using a simple Section|Model|Quantity format. This feature is designed for users with zero technical knowledge who need to quickly add multiple product lines to a sales order.

---

## Business Context

### User Story

**As a** Sales Representative  
**I want to** import product lines from Excel  
**So that** I can quickly create large sales orders without manually adding each line

### Use Cases

1. **Large Orders**: Customer sends Excel file with 50+ items
2. **Repeat Orders**: Customer orders same items monthly (template reuse)
3. **Catalog Orders**: Customer orders from product catalog sections
4. **Bulk Entry**: Faster than manual entry for 10+ lines

### Success Criteria

- ✅ Import completes in <5 seconds for 100 lines
- ✅ User can download template with one click
- ✅ Clear error messages for every validation failure
- ✅ All-or-nothing: Either all lines imported or none
- ✅ Works with zero training (intuitive)

---

## Excel File Format

### Required Format

**Columns** (exact order):
1. Section (Column A)
2. Model (Column B)  
3. Quantity (Column C)

**Example Excel File**:

| Section | Model | Quantity |
|---------|-------|----------|
| Electronics | iPhone 15 Pro | 5 |
| Electronics | iPad Air | 3 |
| Accessories | Apple Pencil | 8 |
| Accessories | Magic Keyboard | 3 |
| Office Supplies | Notebook A4 | 50 |
| Office Supplies | Pen Blue | 100 |

### Column Definitions

#### Section (Column A)
- **Purpose**: Organize products into logical groups
- **Type**: Text
- **Required**: YES
- **Format**: Free text (e.g., "Electronics", "Accessories")
- **Display**: Section headers shown in SO lines as separators
- **Example**: "Electronics", "Office Furniture", "Cleaning Supplies"

#### Model (Column B)
- **Purpose**: Product identifier
- **Type**: Text
- **Required**: YES
- **Format**: Product name or internal reference
- **Matching**: Search product by `name` OR `default_code` (case-insensitive)
- **Example**: "iPhone 15 Pro", "PROD-001", "Laptop Dell XPS"

#### Quantity (Column C)
- **Purpose**: Number of units to order
- **Type**: Number (integer or decimal)
- **Required**: YES
- **Format**: Positive number (e.g., 5, 10.5, 100)
- **Validation**: Must be > 0
- **Example**: 5, 10.5, 100

### File Requirements

- **Format**: .xlsx or .xls (Excel)
- **Size Limit**: 5 MB maximum
- **Row Limit**: 1,000 rows maximum
- **Header Row**: First row must contain headers (will be skipped)
- **Empty Rows**: Skip empty rows automatically
- **Encoding**: UTF-8 preferred, auto-detect if possible

---

## Validation Rules

### All-or-Nothing Principle

**CRITICAL**: Either the entire import succeeds OR the entire import fails. No partial imports.

**Process**:
1. Read entire Excel file
2. Validate ALL rows
3. Collect ALL errors
4. If ANY error exists → Stop, show all errors, import nothing
5. If NO errors → Import all rows

### Row-Level Validations

For each row, validate in this order:

#### 1. Required Fields
- Section: Must not be empty
- Model: Must not be empty  
- Quantity: Must not be empty

**Error Messages**:
- "Row 5: Section is required"
- "Row 8: Model is required"
- "Row 12: Quantity is required"

#### 2. Product Existence
- Model must match an existing product by `name` OR `default_code`
- Search is case-insensitive
- Partial matches are NOT allowed (must be exact)

**Error Messages**:
- "Row 3: Product 'iPhone 99' not found. Check spelling or use Internal Reference."
- "Row 7: Product 'PROD-999' does not exist."

**Helpful Hint**: If multiple products have similar names, suggest using Internal Reference instead

#### 3. Quantity Validation
- Must be a valid number
- Must be greater than 0
- Decimals allowed (e.g., 10.5 for products sold by weight/length)

**Error Messages**:
- "Row 4: Quantity 'abc' is not a valid number."
- "Row 9: Quantity must be greater than 0."
- "Row 11: Quantity '-5' cannot be negative."

#### 4. Duplicate Detection (Optional)
- Warn if same product appears multiple times in different sections
- Don't block import, just warn

**Warning Messages**:
- "Warning: Product 'iPhone 15' appears in multiple sections (rows 3, 15). Quantities will be separate lines."

### File-Level Validations

#### 1. File Format
- Must be .xlsx or .xls
- File must be readable
- File must not be password-protected

**Error Messages**:
- "Invalid file format. Please upload .xlsx or .xls file."
- "File is corrupted or unreadable."
- "File is password-protected. Please remove protection and try again."

#### 2. File Size
- Maximum 5 MB

**Error Message**:
- "File size exceeds 5 MB limit. Please split into smaller files."

#### 3. Row Count
- Maximum 1,000 rows (excluding header)

**Error Message**:
- "File contains 1,500 rows. Maximum allowed is 1,000. Please split into multiple files."

#### 4. Column Structure
- Must have exactly 3 columns
- Column headers must match (case-insensitive): "Section", "Model", "Quantity"

**Error Messages**:
- "Invalid column structure. Expected columns: Section, Model, Quantity"
- "Missing column: 'Quantity'. Please use the template."

---

## User Experience Flow

### Step 1: Open Wizard

**Trigger**: Button on Sale Order form  
**Button Label**: "Import from Excel"  
**Location**: Header, next to "Add a line" button  
**Icon**: 📊 (spreadsheet icon)

### Step 2: Upload or Download Template

**Wizard Screen 1**:

```
┌─────────────────────────────────────────────────┐
│  Import Sale Order Lines from Excel             │
├─────────────────────────────────────────────────┤
│                                                 │
│  [📥 Download Template]                         │
│                                                 │
│  Upload your Excel file:                        │
│  [Choose File]  (No file chosen)                │
│                                                 │
│  Format: Section | Model | Quantity             │
│  Max size: 5 MB, Max rows: 1,000               │
│                                                 │
│            [Cancel]  [Validate & Import]        │
└─────────────────────────────────────────────────┘
```

### Step 3: Validation

**Processing Screen**:

```
┌─────────────────────────────────────────────────┐
│  Validating...                                  │
├─────────────────────────────────────────────────┤
│                                                 │
│  Reading file... ✓                              │
│  Validating 45 rows... ⏳                       │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Step 4A: Validation Errors (If Any)

**Error Screen**:

```
┌─────────────────────────────────────────────────┐
│  ⚠️ Import Failed - Please Fix Errors           │
├─────────────────────────────────────────────────┤
│                                                 │
│  Found 3 errors in your file:                   │
│                                                 │
│  ❌ Row 5: Product 'iPhone 99' not found       │
│  ❌ Row 12: Quantity must be greater than 0    │
│  ❌ Row 18: Section is required                │
│                                                 │
│  No lines were imported. Please fix the errors  │
│  and try again.                                 │
│                                                 │
│            [Close]  [Try Again]                 │
└─────────────────────────────────────────────────┘
```

### Step 4B: Success (If No Errors)

**Success Screen**:

```
┌─────────────────────────────────────────────────┐
│  ✅ Import Successful!                          │
├─────────────────────────────────────────────────┤
│                                                 │
│  Successfully imported 45 lines:                │
│                                                 │
│  📦 Electronics: 8 products                     │
│  📦 Accessories: 12 products                    │
│  📦 Office Supplies: 25 products                │
│                                                 │
│  Lines have been added to your sales order.     │
│                                                 │
│                  [Close]                        │
└─────────────────────────────────────────────────┘
```

### Step 5: View Imported Lines

**Sale Order Lines Tab** (after import):

```
════════════════════════════════════════════════════
  ELECTRONICS
────────────────────────────────────────────────────
  iPhone 15 Pro          5 units    $999.00  $4,995.00
  iPad Air               3 units    $599.00  $1,797.00
════════════════════════════════════════════════════
  ACCESSORIES  
────────────────────────────────────────────────────
  Apple Pencil           8 units    $129.00  $1,032.00
  Magic Keyboard         3 units    $299.00    $897.00
════════════════════════════════════════════════════
```

---

## Technical Implementation

### Files to Create

1. **Wizard Model**
   - File: `addons/ops_matrix_core/wizard/sale_order_import_wizard.py`
   - Model: `sale.order.import.wizard`
   - Type: `models.TransientModel`

2. **Wizard View**
   - File: `addons/ops_matrix_core/wizard/sale_order_import_wizard_views.xml`
   - Form view with file upload field

3. **Template Generator**
   - Method: `action_download_template()`
   - Returns: Excel file with headers and sample data

### Key Methods

#### 1. `action_download_template(self)`

**Purpose**: Generate and download Excel template

**Returns**: Excel file with:
- Headers: Section | Model | Quantity
- Sample rows (3-5 examples)
- Instructions sheet (optional)

**Implementation**:
```python
import xlsxwriter
import base64
from io import BytesIO

def action_download_template(self):
    # Create Excel file in memory
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Import Template')
    
    # Write headers
    worksheet.write(0, 0, 'Section')
    worksheet.write(0, 1, 'Model')
    worksheet.write(0, 2, 'Quantity')
    
    # Write sample data
    worksheet.write(1, 0, 'Electronics')
    worksheet.write(1, 1, 'iPhone 15 Pro')
    worksheet.write(1, 2, 5)
    
    workbook.close()
    
    # Return as download
    return {
        'type': 'ir.actions.act_url',
        'url': f'/web/content?model=sale.order.import.wizard&id={self.id}&field=template_file&download=true&filename=SO_Import_Template.xlsx',
        'target': 'self',
    }
```

#### 2. `action_validate_and_import(self)`

**Purpose**: Main import logic

**Process**:
1. Read uploaded Excel file
2. Parse rows (skip header)
3. Validate all rows
4. Collect errors
5. If errors → Display error wizard
6. If no errors → Create SO lines
7. Display success wizard

**Pseudo-code**:
```python
def action_validate_and_import(self):
    # 1. Read file
    file_data = base64.b64decode(self.import_file)
    workbook = openpyxl.load_workbook(BytesIO(file_data))
    sheet = workbook.active
    
    # 2. Validate file structure
    errors = self._validate_file_structure(sheet)
    if errors:
        return self._show_error_wizard(errors)
    
    # 3. Parse and validate rows
    rows = []
    for idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
        section = row[0].value
        model = row[1].value
        quantity = row[2].value
        
        # Validate row
        row_errors = self._validate_row(idx, section, model, quantity)
        if row_errors:
            errors.extend(row_errors)
        else:
            rows.append({
                'section': section,
                'model': model,
                'quantity': quantity,
            })
    
    # 4. All-or-nothing check
    if errors:
        return self._show_error_wizard(errors)
    
    # 5. Import all rows
    self._create_order_lines(rows)
    
    # 6. Show success
    return self._show_success_wizard(len(rows))
```

#### 3. `_validate_row(self, row_num, section, model, quantity)`

**Purpose**: Validate a single row

**Returns**: List of error messages (empty if valid)

**Logic**:
```python
def _validate_row(self, row_num, section, model, quantity):
    errors = []
    
    # Required fields
    if not section:
        errors.append(f"Row {row_num}: Section is required")
    if not model:
        errors.append(f"Row {row_num}: Model is required")
    if not quantity:
        errors.append(f"Row {row_num}: Quantity is required")
        return errors  # Can't validate further
    
    # Product exists
    product = self.env['product.product'].search([
        '|',
        ('name', '=ilike', model),
        ('default_code', '=ilike', model)
    ], limit=1)
    
    if not product:
        errors.append(f"Row {row_num}: Product '{model}' not found")
    
    # Quantity validation
    try:
        qty = float(quantity)
        if qty <= 0:
            errors.append(f"Row {row_num}: Quantity must be greater than 0")
    except (ValueError, TypeError):
        errors.append(f"Row {row_num}: Quantity '{quantity}' is not a valid number")
    
    return errors
```

#### 4. `_create_order_lines(self, rows)`

**Purpose**: Create sale order lines from validated rows

**Process**:
1. Group rows by section
2. Create section headers (display_type='line_section')
3. Create product lines under each section

**Logic**:
```python
def _create_order_lines(self, rows):
    sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
    
    # Group by section
    sections = {}
    for row in rows:
        section = row['section']
        if section not in sections:
            sections[section] = []
        sections[section].append(row)
    
    # Create lines
    for section_name, section_rows in sections.items():
        # Create section header
        sale_order.order_line.create({
            'order_id': sale_order.id,
            'display_type': 'line_section',
            'name': section_name.upper(),
        })
        
        # Create product lines
        for row in section_rows:
            product = self.env['product.product'].search([
                '|',
                ('name', '=ilike', row['model']),
                ('default_code', '=ilike', row['model'])
            ], limit=1)
            
            sale_order.order_line.create({
                'order_id': sale_order.id,
                'product_id': product.id,
                'product_uom_qty': float(row['quantity']),
            })
```

---

## Wizard Model Fields

```python
class SaleOrderImportWizard(models.TransientModel):
    _name = 'sale.order.import.wizard'
    _description = 'Sale Order Import from Excel Wizard'
    
    import_file = fields.Binary(
        string='Excel File',
        required=True,
        help='Upload your Excel file with columns: Section, Model, Quantity'
    )
    
    import_filename = fields.Char(
        string='Filename'
    )
    
    # Template generation (computed field for download)
    template_file = fields.Binary(
        string='Template',
        compute='_compute_template_file'
    )
    
    # Results (for success/error wizards)
    import_result = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('error', 'Error'),
    ], default='pending')
    
    error_message = fields.Text(
        string='Error Messages'
    )
    
    success_message = fields.Text(
        string='Success Summary'
    )
    
    lines_imported = fields.Integer(
        string='Lines Imported'
    )
```

---

## Wizard View Structure

### Upload Screen (Step 1)

```xml
<record id="view_sale_order_import_wizard_form" model="ir.ui.view">
    <field name="name">sale.order.import.wizard.form</field>
    <field name="model">sale.order.import.wizard</field>
    <field name="arch" type="xml">
        <form string="Import Sale Order Lines">
            <group>
                <div class="alert alert-info" role="alert">
                    <strong>How to use:</strong>
                    <ul>
                        <li>Download the template below or use your own Excel file</li>
                        <li>Fill in: Section, Model (product name), Quantity</li>
                        <li>Upload the completed file</li>
                    </ul>
                </div>
                
                <button name="action_download_template" 
                        type="object" 
                        string="📥 Download Template" 
                        class="btn-primary"/>
                
                <field name="import_file" filename="import_filename"/>
                <field name="import_filename" invisible="1"/>
            </group>
            
            <footer>
                <button name="action_validate_and_import" 
                        type="object" 
                        string="Validate & Import" 
                        class="btn-primary"/>
                <button string="Cancel" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

### Error Screen (Step 2 - If Errors)

```xml
<record id="view_sale_order_import_error_form" model="ir.ui.view">
    <field name="name">sale.order.import.wizard.error.form</field>
    <field name="model">sale.order.import.wizard</field>
    <field name="arch" type="xml">
        <form string="Import Errors">
            <div class="alert alert-danger" role="alert">
                <h4>⚠️ Import Failed - Please Fix Errors</h4>
            </div>
            
            <group>
                <field name="error_message" nolabel="1" readonly="1"/>
            </group>
            
            <div class="alert alert-warning" role="alert">
                No lines were imported. Please fix the errors and try again.
            </div>
            
            <footer>
                <button string="Close" class="btn-secondary" special="cancel"/>
                <button string="Try Again" 
                        type="object" 
                        name="action_reset" 
                        class="btn-primary"/>
            </footer>
        </form>
    </field>
</record>
```

### Success Screen (Step 2 - If Success)

```xml
<record id="view_sale_order_import_success_form" model="ir.ui.view">
    <field name="name">sale.order.import.wizard.success.form</field>
    <field name="model">sale.order.import.wizard</field>
    <field name="arch" type="xml">
        <form string="Import Success">
            <div class="alert alert-success" role="alert">
                <h4>✅ Import Successful!</h4>
            </div>
            
            <group>
                <field name="lines_imported" readonly="1"/>
                <field name="success_message" nolabel="1" readonly="1"/>
            </group>
            
            <div class="alert alert-info" role="alert">
                Lines have been added to your sales order.
            </div>
            
            <footer>
                <button string="Close" class="btn-primary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

---

## Sale Order Integration

### Add Button to Sale Order Form

**File**: `addons/ops_matrix_core/views/sale_order_views.xml` (existing file)

**Add to sale.order form header**:

```xml
<xpath expr="//form/header" position="inside">
    <button name="%(action_sale_order_import_wizard)d" 
            type="action" 
            string="Import from Excel" 
            icon="fa-file-excel-o"
            class="btn-secondary"
            attrs="{'invisible': [('state', 'not in', ['draft', 'sent'])]}"/>
</xpath>
```

---

## Python Dependencies

**Required Libraries**:
- `openpyxl` - Read Excel files
- `xlsxwriter` - Generate Excel files

**Add to requirements.txt** (if not already present):
```
openpyxl>=3.0.0
xlsxwriter>=3.0.0
```

**Install in Docker container**:
```bash
docker exec gemini_odoo19 pip install openpyxl xlsxwriter --break-system-packages
```

---

## Testing Checklist

### Happy Path Tests

- [ ] Download template → File downloads with correct headers
- [ ] Upload valid file → Import succeeds, lines created
- [ ] Section headers → Display as line_section in SO
- [ ] Product names → Match by name
- [ ] Internal references → Match by default_code
- [ ] Decimal quantities → Accepted (e.g., 10.5)
- [ ] Multiple sections → All imported correctly
- [ ] Empty rows → Skipped automatically

### Error Handling Tests

- [ ] Missing section → Error displayed with row number
- [ ] Missing model → Error displayed
- [ ] Missing quantity → Error displayed
- [ ] Invalid product → "Product not found" error
- [ ] Negative quantity → "Must be greater than 0" error
- [ ] Text quantity → "Not a valid number" error
- [ ] Wrong file format (.pdf) → "Invalid file format" error
- [ ] Corrupted file → "File unreadable" error
- [ ] File too large → "Exceeds 5 MB" error
- [ ] Too many rows → "Maximum 1,000 rows" error
- [ ] Multiple errors → All errors displayed at once

### Edge Cases

- [ ] Duplicate products in different sections → Both imported
- [ ] Product name with special characters → Handled correctly
- [ ] Very long section names → Displayed properly
- [ ] Case-insensitive matching → Works
- [ ] Unicode characters → Supported
- [ ] Empty file → Appropriate error
- [ ] Only headers (no data) → Appropriate error

---

## Error Messages Reference

### File-Level Errors

```
Invalid file format. Please upload .xlsx or .xls file.
File is corrupted or unreadable.
File is password-protected. Please remove protection and try again.
File size exceeds 5 MB limit. Please split into smaller files.
File contains {count} rows. Maximum allowed is 1,000.
Invalid column structure. Expected: Section, Model, Quantity
Missing column: '{column_name}'. Please use the template.
```

### Row-Level Errors

```
Row {n}: Section is required
Row {n}: Model is required
Row {n}: Quantity is required
Row {n}: Product '{name}' not found. Check spelling or use Internal Reference.
Row {n}: Quantity '{value}' is not a valid number.
Row {n}: Quantity must be greater than 0.
Row {n}: Quantity '{value}' cannot be negative.
```

### Success Messages

```
Successfully imported {count} lines:
📦 {section1}: {count1} products
📦 {section2}: {count2} products
📦 {section3}: {count3} products
```

---

## Performance Considerations

### Optimization Strategies

1. **Batch Product Search**: Search all products once, cache results
2. **Bulk Create**: Create all lines in one operation
3. **Memory Efficient**: Process large files in chunks if needed
4. **Progress Indicator**: Show progress for files >100 rows

### Expected Performance

- **10 rows**: <1 second
- **100 rows**: <5 seconds
- **1,000 rows**: <30 seconds

---

## Future Enhancements (Not in Scope Now)

- [ ] Support for price override column
- [ ] Support for discount column
- [ ] Support for description/notes column
- [ ] Multiple file upload (batch import)
- [ ] Import history/audit trail
- [ ] Undo last import
- [ ] Import from CSV format
- [ ] Import validation preview before commit
- [ ] Excel file with formulas support
- [ ] Auto-complete suggestions for products

---

## Estimated Development Timeline

### Session 1 (2-3 hours)
- Create wizard model with fields
- Implement template download
- Create basic wizard view
- Test template generation

### Session 2 (2-3 hours)
- Implement file upload and parsing
- Implement validation logic
- Create error/success views
- Test validation

### Session 3 (1-2 hours)
- Implement line creation logic
- Add button to sale order form
- Full integration testing
- Bug fixes and polish

**Total Estimated Time**: 5-8 hours over 2-3 sessions

---

## Success Metrics

**Feature is successful if**:
- ✅ Users can import 50+ lines in <1 minute
- ✅ Zero support tickets about "how to use"
- ✅ 95%+ success rate on valid files
- ✅ Error messages are actionable
- ✅ No manual data fixes needed after import

---

## Documentation Deliverables

### For Users
- [ ] Quick Start Guide (1-page)
- [ ] Excel template with instructions
- [ ] Error message reference
- [ ] FAQ document

### For Developers
- [ ] Code comments in wizard model
- [ ] Update technical documentation
- [ ] Add to developer guide

---

## Security Considerations

- ✅ File upload validation (format, size)
- ✅ No code execution from uploaded files
- ✅ Sanitize product names before search
- ✅ Respect user permissions (can only import to own SO)
- ✅ Audit trail via chatter ("Imported X lines from Excel")

---

## Questions for User Decision

**Before development starts, confirm**:

1. **Price Override**: Should users be able to override prices in Excel?
   - Current: No (use product default price)
   - Alternative: Add "Price" column

2. **Discount**: Should discount column be supported?
   - Current: No (use product default discount rules)
   - Alternative: Add "Discount %" column

3. **Product Not Found**: What should happen?
   - Current: Show error, block import
   - Alternative: Skip line with warning

4. **Duplicate Detection**: What should happen?
   - Current: Allow duplicates (create separate lines)
   - Alternative: Combine quantities

5. **Section Grouping**: Required or optional?
   - Current: Required
   - Alternative: Optional (all in "General" section)

**Default Answers**: Use "Current" for all (simpler, safer)

---

## READY FOR DEVELOPMENT

**Status**: ✅ SPECIFICATIONS COMPLETE  
**Next Step**: Assign to RooCode for development  
**Estimated Completion**: 2-3 sessions  

**All requirements defined, ready to code!** 🚀
