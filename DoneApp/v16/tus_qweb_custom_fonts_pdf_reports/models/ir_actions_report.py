# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

import os
import re
import base64
import tempfile
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

# Also try to get the base logger to ensure messages appear
_base_logger = logging.getLogger('odoo.addons.base.models.ir_actions_report')


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _run_wkhtmltopdf(
            self,
            bodies,
            report_ref=False,
            header=None,
            footer=None,
            landscape=False,
            specific_paperformat_args=None,
            set_viewport_size=False):
        """Override to save custom fonts to temporary files for wkhtmltopdf"""
        
        try:
            _logger.info("=" * 80)
            _logger.info("PDF Generation: _run_wkhtmltopdf OVERRIDE CALLED - processing custom fonts")
            _logger.info("=" * 80)
            _base_logger.info("PDF Generation: _run_wkhtmltopdf OVERRIDE CALLED - processing custom fonts")
        except Exception as e:
            _logger.warning("PDF Generation: logging failed: %s", e)
        
        # Process bodies, header, and footer to replace data URIs with file:// URLs
        font_files = {}  # Map of data URI to file path
        temporary_font_files = []
        
        def replace_font_data_uri(content):
            """Replace font data URIs with file:// URLs"""
            _logger.info(f"PDF Generation: replace_font_data_uri called (content length: {len(content) if content else 0})")
            if not content:
                return content
            
            # Debug: Check if content contains data URIs
            has_data = 'data:' in content
            has_base64 = 'base64' in content
            has_font_sfnt = 'application/font-sfnt' in content
            _logger.info(f"PDF Generation: replace_font_data_uri - has 'data:': {has_data}, has 'base64': {has_base64}, has 'font-sfnt': {has_font_sfnt}")
            if has_data and has_base64:
                _logger.debug("Found potential data URI in content")
                # Log a sample to see the format
                sample_match = re.search(r"url\(['\"]?(data:[^'\"\)]+)['\"]?\)", content)
                if sample_match:
                    _logger.debug(f"Sample data URI found: {sample_match.group(1)[:150]}...")
            
            # Pattern to match data URIs for fonts in CSS url() declarations
            # Matches: url('data:...') or url("data:...") or url(data:...)
            # Use a simpler approach: match font MIME types and then everything until the closing quote
            # Use greedy match to capture the entire base64 string until the quote
            pattern = r"url\((['\"]?)data:(application/font-sfnt|font/(woff|woff2|opentype)|application/vnd\.ms-fontobject);base64,([^'\"]+)\1\)"
            
            def replace_match(match):
                # Reconstruct the full data URI from groups
                quote = match.group(1) or ''
                mime_type = match.group(2)
                base64_data = match.group(3)
                data_uri = f"data:{mime_type};base64,{base64_data}"
                
                # If we've already created a file for this data URI, reuse it
                if data_uri in font_files:
                    file_path = font_files[data_uri]
                    # Use absolute path with forward slashes for file:// URL
                    file_url = os.path.abspath(file_path).replace('\\', '/')
                    return f"url('file:///{file_url}')"
                
                try:
                    # Extract base64 data from data URI
                    # Format: data:mime/type;base64,<base64_data>
                    mime_part = mime_type
                    
                    # Decode base64 data
                    font_bytes = base64.b64decode(base64_data)
                    
                    if len(font_bytes) == 0:
                        _logger.warning("Empty font data after base64 decode")
                        return match.group(0)
                    
                    # Determine file extension from MIME type
                    if 'woff2' in mime_part.lower():
                        ext = '.woff2'
                    elif 'woff' in mime_part.lower():
                        ext = '.woff'
                    elif 'opentype' in mime_part.lower() or 'otf' in mime_part.lower():
                        ext = '.otf'
                    elif 'eot' in mime_part.lower():
                        ext = '.eot'
                    else:
                        ext = '.ttf'  # Default to TTF
                    
                    # Create temporary font file
                    font_file_fd, font_file_path = tempfile.mkstemp(suffix=ext, prefix='report.font.tmp.')
                    os.close(font_file_fd)  # Close file descriptor, we'll write using open()
                    
                    # Write font data to file
                    with open(font_file_path, 'wb') as font_file:
                        font_file.write(font_bytes)
                    
                    _logger.info(f"Created temporary font file: {font_file_path} (size: {len(font_bytes)} bytes)")
                    
                    # Store mapping and add to cleanup list
                    font_files[data_uri] = font_file_path
                    temporary_font_files.append(font_file_path)
                    
                    # Return file:// URL (use absolute path with forward slashes)
                    file_url = os.path.abspath(font_file_path).replace('\\', '/')
                    return f"url('file:///{file_url}')"
                    
                except Exception as e:
                    _logger.warning(f"Failed to process font data URI: {e}", exc_info=True)
                    return match.group(0)  # Return original on error
            
            # Replace all font data URIs in the content
            # Use DOTALL flag to allow matching across newlines if data URI is split
            matches_before = len(re.findall(pattern, content, flags=re.IGNORECASE | re.DOTALL))
            if matches_before > 0:
                _logger.info(f"Found {matches_before} font data URI(s) in content")
            else:
                # Try to find font data URIs with a simpler pattern
                simple_pattern = r"url\(['\"]?data:application/font-sfnt;base64,[^'\"]+['\"]?\)"
                simple_matches = re.findall(simple_pattern, content, flags=re.IGNORECASE | re.DOTALL)
                if simple_matches:
                    _logger.warning(f"Found {len(simple_matches)} font data URI(s) with simpler pattern")
                    _logger.info(f"Sample match: {simple_matches[0][:200]}...")
                else:
                    # Check if @font-face exists with data URIs
                    font_face_pattern = r"@font-face[^}]*src:\s*url\([^)]+\)"
                    font_face_matches = re.findall(font_face_pattern, content, flags=re.IGNORECASE | re.DOTALL)
                    if font_face_matches:
                        _logger.warning(f"Found {len(font_face_matches)} @font-face rule(s) but pattern not matching")
                        _logger.info(f"Sample @font-face: {font_face_matches[0][:300]}...")
                    else:
                        # Try a more permissive pattern to see if data URIs exist but aren't matching
                        alt_pattern = r"data:application/font-sfnt;base64,"
                        alt_count = content.count(alt_pattern)
                        if alt_count > 0:
                            _logger.warning(f"Found {alt_count} font data URI(s) with string search, but regex not matching")
                            # Find the position and context
                            pos = content.find(alt_pattern)
                            if pos >= 0:
                                start = max(0, pos - 100)
                                end = min(len(content), pos + 200)
                                _logger.info(f"Context around font data URI: ...{content[start:end]}...")
            result = re.sub(pattern, replace_match, content, flags=re.IGNORECASE | re.DOTALL)
            if matches_before > 0:
                _logger.info(f"Processed {len(font_files)} unique font file(s) from {matches_before} data URI(s)")
            return result
        
        try:
            # Debug: Check if custom fonts exist
            custom_fonts = self.env['custom.font.file'].search([('active', '=', True)])
            _logger.info(f"PDF Generation: Found {len(custom_fonts)} active custom font file(s)")
            for font in custom_fonts:
                _logger.info(f"  - Font: {font.name} (ID: {font.id}, Family: {font.font_family_name})")
            
            # Debug: Check company font setting
            company = self.env.company
            if company.custom_font_file_id:
                _logger.info(f"PDF Generation: Company {company.name} (ID: {company.id}) has custom font: {company.custom_font_file_id.name}")
            else:
                _logger.info(f"PDF Generation: Company {company.name} (ID: {company.id}) has NO custom font selected")
            
            # Debug: Check HTML content for data URIs
            sample_body = bodies[0] if bodies else ""
            if 'data:' in sample_body:
                _logger.info("PDF Generation: Found 'data:' in HTML content")
                # Find all data URIs
                data_uri_matches = re.findall(r"data:[^'\"\)\s]+", sample_body)
                _logger.info(f"PDF Generation: Found {len(data_uri_matches)} data URI(s) in HTML (sample: {data_uri_matches[0][:100] if data_uri_matches else 'none'}...)")
            else:
                _logger.warning("PDF Generation: NO 'data:' found in HTML content - fonts may not be injected!")
                # Check if @font-face exists
                if '@font-face' in sample_body:
                    _logger.info("PDF Generation: Found @font-face in HTML but no data URIs")
                else:
                    _logger.warning("PDF Generation: NO @font-face found in HTML - template may not be rendering!")
            
            # Inject font CSS directly into HTML if not present
            def inject_font_css(content):
                """Inject @font-face CSS if not already present"""
                if not content:
                    return content
                
                # Check if @font-face with data URIs already exists
                if '@font-face' in content and 'data:application/font-sfnt;base64,' in content:
                    _logger.debug("@font-face with font data URIs already present in content")
                    return content
                
                # Get active custom fonts
                custom_fonts = self.env['custom.font.file'].search([('active', '=', True)])
                if not custom_fonts:
                    return content
                
                # Build @font-face CSS
                font_css_parts = []
                for font_file in custom_fonts:
                    font_data_uri = font_file.get_font_data_uri()
                    _logger.info(f"PDF Generation: Font {font_file.name} (ID: {font_file.id}) - get_font_data_uri() returned: {bool(font_data_uri)} (length: {len(font_data_uri) if font_data_uri else 0})")
                    if font_data_uri:
                        _logger.info(f"PDF Generation: Font {font_file.name} data URI preview: {font_data_uri[:100]}...")
                        # Determine format
                        if font_file.font_filename and font_file.font_filename.endswith('.woff'):
                            font_format = 'woff'
                        elif font_file.font_filename and font_file.font_filename.endswith('.woff2'):
                            font_format = 'woff2'
                        elif font_file.font_filename and font_file.font_filename.endswith('.otf'):
                            font_format = 'opentype'
                        else:
                            font_format = 'truetype'
                        
                        font_css_parts.append(f"""
@font-face {{
    font-family: {font_file.font_family_name};
    src: url('{font_data_uri}') format('{font_format}');
    font-weight: normal;
    font-style: normal;
    font-display: swap;
}}""")
                
                if not font_css_parts:
                    return content
                
                font_css = '\n'.join(font_css_parts)
                
                # Debug: Log a sample of the CSS to verify format
                _logger.info(f"PDF Generation: Generated font CSS (length: {len(font_css)} chars)")
                # Extract a sample showing the url() format
                url_match = re.search(r"src:\s*url\([^)]+\)", font_css, re.IGNORECASE)
                if url_match:
                    sample_url = url_match.group(0)
                    _logger.info(f"PDF Generation: Sample CSS url() format: {sample_url[:200]}...")
                
                # Always inject as a <style> tag at the beginning to ensure it's present
                # Check if CSS is already present to avoid duplicates
                if 'data:application/font-sfnt;base64,' in content:
                    _logger.debug("Font CSS with data URIs already present, skipping injection")
                    return content
                
                # Inject at the very beginning of content - this ensures it's always present
                content = f'<style>{font_css}</style>{content}'
                _logger.info(f"Injected font CSS at beginning of content (new length: {len(content)} chars)")
                
                # Verify injection worked
                if 'data:application/font-sfnt;base64,' in content:
                    _logger.info("✓ Verified: Font data URIs are now in content")
                else:
                    _logger.warning("✗ Warning: Font data URIs NOT found in content after injection!")
                
                # Also try to inject into <head> if it exists (for proper HTML structure)
                if '<head>' in content and '</head>' in content:
                    # Check if we already injected (to avoid duplicate)
                    if f'<style>{font_css}</style>' not in content[:content.find('</head>')]:
                        content = content.replace('</head>', f'<style>{font_css}</style></head>', 1)
                        _logger.info("Also injected font CSS into <head> section")
                
                return content
            
            # Inject font CSS into bodies, header, and footer
            bodies_with_fonts = [inject_font_css(body) for body in bodies]
            header_with_fonts = inject_font_css(header) if header else None
            footer_with_fonts = inject_font_css(footer) if footer else None
            
            # Debug: Check if data URIs are now present after injection
            sample_body_after = bodies_with_fonts[0] if bodies_with_fonts else ""
            _logger.info(f"PDF Generation: Checking injected content (length: {len(sample_body_after)} chars)")
            has_data = 'data:' in sample_body_after
            has_base64 = 'base64' in sample_body_after
            has_font_sfnt = 'application/font-sfnt' in sample_body_after
            _logger.info(f"PDF Generation: Content check - has 'data:': {has_data}, has 'base64': {has_base64}, has 'font-sfnt': {has_font_sfnt}")
            if has_data and has_base64:
                _logger.info("PDF Generation: Data URIs found in HTML after injection")
                # Find a sample data URI to verify format - use a more flexible pattern
                sample_match = re.search(r"url\(['\"]?(data:[^'\"\)]+)['\"]?\)", sample_body_after, re.DOTALL)
                if sample_match:
                    sample_uri = sample_match.group(1)
                    _logger.info(f"PDF Generation: Sample data URI format: {sample_uri[:100]}...")
                else:
                    # Try to find the actual format in the CSS
                    style_match = re.search(r"<style>.*?@font-face.*?src:\s*url\(['\"]?(data:[^'\"\)]+)['\"]?\)", sample_body_after, re.DOTALL | re.IGNORECASE)
                    if style_match:
                        _logger.info(f"PDF Generation: Found data URI in @font-face: {style_match.group(1)[:100]}...")
                    else:
                        _logger.warning("PDF Generation: Data URIs present but regex not matching - checking CSS format")
                        # Extract a sample of the CSS around @font-face
                        font_face_match = re.search(r"@font-face\s*\{[^}]{0,500}", sample_body_after, re.DOTALL | re.IGNORECASE)
                        if font_face_match:
                            _logger.info(f"PDF Generation: Sample @font-face CSS: {font_face_match.group(0)[:200]}...")
            else:
                _logger.warning("PDF Generation: NO data URIs found after injection!")
            
            # Process bodies, header, and footer to replace data URIs with file:// URLs
            processed_bodies = [replace_font_data_uri(body) for body in bodies_with_fonts]
            processed_header = replace_font_data_uri(header_with_fonts) if header_with_fonts else None
            processed_footer = replace_font_data_uri(footer_with_fonts) if footer_with_fonts else None
            
            # Log summary
            if font_files:
                _logger.info(f"PDF Generation: Processed {len(font_files)} custom font(s) for wkhtmltopdf")
            else:
                _logger.info("PDF Generation: No font data URIs found to process")
            
            # Call parent method with processed content
            result = super()._run_wkhtmltopdf(
                processed_bodies,
                report_ref=report_ref,
                header=processed_header,
                footer=processed_footer,
                landscape=landscape,
                specific_paperformat_args=specific_paperformat_args,
                set_viewport_size=set_viewport_size
            )
            
            return result
            
        except Exception as e:
            _logger.error(f"ERROR in _run_wkhtmltopdf override: {e}", exc_info=True)
            _base_logger.error(f"ERROR in _run_wkhtmltopdf override: {e}", exc_info=True)
            # Fall back to parent method on error
            return super()._run_wkhtmltopdf(
                bodies,
                report_ref=report_ref,
                header=header,
                footer=footer,
                landscape=landscape,
                specific_paperformat_args=specific_paperformat_args,
                set_viewport_size=set_viewport_size
            )
        finally:
            # Clean up temporary font files
            for font_file_path in temporary_font_files:
                try:
                    if os.path.exists(font_file_path):
                        os.unlink(font_file_path)
                except (OSError, IOError) as e:
                    _logger.error(f'Error when trying to remove font file {font_file_path}: {e}')
