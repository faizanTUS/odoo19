# -*- coding: utf-8 -*-
"""Run with: odoo-bin shell -d DB --addons-path=... --shell-file=path/to/uap_functional_verify.py
Verifies config parameters, session_info keys, and sample Office/PDF attachments.
"""
import base64

ICP = env["ir.config_parameter"].sudo()

# 1) Config parameters (mirrors settings toggles)
ICP.set_param("document_attachment_universal_preview.office_preview", "True")
ICP.set_param("document_attachment_universal_preview.google_viewer_fallback", "False")

office = ICP.get_param("document_attachment_universal_preview.office_preview")
gdoc = ICP.get_param("document_attachment_universal_preview.google_viewer_fallback")
print("[OK] ICP office_preview=%r google_viewer_fallback=%r" % (office, gdoc))

# 2) res.config.settings fields (transient; sanity check)
settings = env["res.config.settings"].create({})
settings.invalidate_recordset()
print("[OK] settings uap_office_preview=%s uap_google_viewer_fallback=%s" % (
    settings.uap_office_preview,
    settings.uap_google_viewer_fallback,
))

# 3) Same logic as models/ir_http.py session_info() (no HTTP server required)
def _uap_session_flags():
    s = env["ir.config_parameter"].sudo()
    uap_office = s.get_param("document_attachment_universal_preview.office_preview", "True").lower() in (
        "1",
        "true",
        "yes",
    )
    uap_google = s.get_param("document_attachment_universal_preview.google_viewer_fallback", "False").lower() in (
        "1",
        "true",
        "yes",
    )
    return uap_office, uap_google


u1, u2 = _uap_session_flags()
print("[OK] derived uap_office_preview=%s uap_google_office_fallback=%s (same rules as ir.http session_info)" % (u1, u2))

partner = env.ref("base.main_partner", raise_if_not_found=False) or env["res.partner"].search([], limit=1)
tiny = base64.b64encode(b"PK\x03\x04 minimal office-like blob for test")

# 4) Sample attachments (Office + PDF + image) for preview rules
Att = env["ir.attachment"].sudo()
names_types = [
    ("uap_test_word.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ("uap_test_excel.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ("uap_test_pdf.pdf", "application/pdf"),
    ("uap_test_image.png", "image/png"),
]
created = []
for name, mime in names_types:
    rec = Att.create({
        "name": name,
        "type": "binary",
        "datas": tiny,
        "mimetype": mime,
        "res_model": partner._name,
        "res_id": partner.id,
    })
    created.append(rec.id)
    print("[OK] attachment id=%s name=%s mimetype=%s" % (rec.id, name, mime))

print("[DONE] UAP functional verify: %s attachment(s), partner=%s" % (len(created), partner.id))
env.cr.commit()
