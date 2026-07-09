# Troubleshooting Custom Fonts in PDF Reports

## Current Implementation

The module uses **data URIs** to embed fonts directly in the CSS for PDF generation. This is necessary because wkhtmltopdf (the PDF renderer) may not be able to access external URLs.

## Verification Steps

1. **Check if font is loaded in HTML source:**
   - Go to a Sale Order
   - Right-click → View Page Source
   - Search for `@font-face` - you should see your custom font declaration
   - Search for `font-family` - you should see your custom font name

2. **Check font data URI:**
   - The data URI should start with `data:font/truetype;base64,` (or similar)
   - It should be a very long string (the base64 encoded font)

3. **Verify font selection:**
   - Go to Settings → Configure Document Layout
   - Ensure "Custom Font File" field has your font selected
   - Save the configuration

4. **Check company settings:**
   - Go to Settings → Companies → Your Company
   - Verify `custom_font_file_id` field has your font selected

## Common Issues

### Font not appearing in PDF

**Possible causes:**
1. Font file format not supported by wkhtmltopdf
2. Data URI too large (some PDF renderers have limits)
3. Font-family name mismatch between @font-face and CSS usage
4. Font not properly base64 encoded

**Solutions:**
- Try using a `.ttf` font file (most compatible)
- Ensure font file size is reasonable (< 2MB recommended)
- Check browser console for font loading errors
- Verify the font-family name matches exactly

### Font appears in preview but not in PDF

This suggests the font is loading correctly but wkhtmltopdf can't use it.

**Solutions:**
- Try a different font file format
- Reduce font file size
- Check wkhtmltopdf version and compatibility

## Testing

To test if fonts are working:

1. Upload a simple, small TTF font
2. Select it in Document Layout
3. Generate a PDF report
4. Check if the font is applied

If still not working, the issue might be with wkhtmltopdf's font support. In that case, you may need to:
- Use system fonts instead
- Or configure wkhtmltopdf to support custom fonts differently

