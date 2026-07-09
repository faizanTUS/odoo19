# Qweb Reports Custom Font - Configuration Guide

This module allows you to upload custom font files and apply them to all PDF reports in Odoo 18.

## Step-by-Step Configuration

### Step 1: Install the Module

1. Go to **Apps** menu
2. Remove the **Apps** filter to see all modules
3. Search for **"Qweb Reports Custom Font"**
4. Click **Install**

### Step 2: Upload Custom Font File

1. Go to **Settings** → **General Settings**
2. Scroll down to find **"Document Layout"** section
3. Click on **"Upload/Choose Font File"** button
   - OR go directly to **Settings** → **Custom Font Files** (under Administration section)

4. Click **Create** button to add a new font file

5. Fill in the form:
   - **Font Name**: Enter a descriptive name (e.g., "Custom-font", "My Company Font")
   - **Company**: Select the company (defaults to current company)
   - **Font File**: Click **Upload** and select your font file
     - Supported formats: `.ttf`, `.otf`, `.woff`, `.woff2`, `.eot`
   - **Active**: Keep checked to enable the font

6. Click **Save**

**Note**: The system will automatically:
   - Generate a CSS-safe font family name from your font name
   - Create an attachment for the font file
   - Make the font available for selection

### Step 3: Configure Document Layout

1. Go to **Settings** → **General Settings**
2. In the **"Document Layout"** section, click **"Configure Document Layout"** button

3. In the Document Layout configuration window:
   - **Font/Text**: You can keep a default font selected (e.g., "Lato")
   - **Custom Font File**: Select your uploaded custom font from the dropdown
     - This field appears below the Font selection
     - When you select a custom font file, it will automatically be used in reports

4. Configure other layout options as needed:
   - Layout style (Light, Bold, Striped, etc.)
   - Colors
   - Logo
   - Background
   - Company details

5. Click **Continue** to save the configuration

### Step 4: Verify Font Application

1. Go to any report that uses external layout (e.g., Invoice, Quotation, Purchase Order)
2. Click **Print** or **Download PDF**
3. The custom font should now be applied to the PDF report

### Step 5: Test with Different Reports

Test the custom font with various reports:
- **Sales**: Quotations, Sales Orders, Invoices
- **Purchase**: Purchase Orders, Vendor Bills
- **Inventory**: Delivery Slips, Receipts
- Any other report using external layout

## Additional Configuration Options

### Managing Multiple Font Files

1. Go to **Settings** → **Custom Font Files**
2. You can:
   - **Create** multiple font files for different purposes
   - **Edit** existing font files
   - **Archive/Unarchive** fonts using the Active toggle
   - **Delete** unused fonts

### Company-Specific Fonts

- Each company can have its own custom fonts
- Font files are company-specific
- When configuring document layout, only fonts for the current company are shown

### Font File Requirements

- **Supported formats**: `.ttf`, `.otf`, `.woff`, `.woff2`, `.eot`
- **Recommended**: Use `.ttf` or `.otf` for best compatibility
- **File size**: Keep font files reasonable in size for faster PDF generation

## Troubleshooting

### Font Not Appearing in Reports

1. **Check if font file is active**:
   - Go to Settings → Custom Font Files
   - Ensure the font has "Active" checkbox checked

2. **Verify font is selected in Document Layout**:
   - Go to Settings → Configure Document Layout
   - Ensure "Custom Font File" field has your font selected

3. **Check font file format**:
   - Ensure the uploaded file is a valid font file
   - Try re-uploading the font file

4. **Clear browser cache**:
   - Clear your browser cache and reload the page

### Font Not Loading in PDF

1. **Check font file accessibility**:
   - The font file should be publicly accessible
   - Verify the attachment was created correctly

2. **Verify @font-face injection**:
   - Check browser developer tools (Network tab) to see if font is loading
   - Ensure the font URL is accessible

3. **Test with different reports**:
   - Some reports might use internal layout instead of external layout
   - Custom fonts only apply to reports with external layout

## Technical Details

### How It Works

1. **Font Upload**: Font files are stored as `ir.attachment` records
2. **Font Selection**: Custom fonts are linked to companies via `custom_font_file_id` field
3. **CSS Injection**: `@font-face` declarations are injected into report templates
4. **Font Application**: The `styles_company_report` template uses custom font if selected, otherwise falls back to default font

