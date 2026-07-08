# -*- coding: utf-8 -*-


def migrate(cr, version):
    """Remove legacy split RingCentral privileges from earlier module versions."""
    cr.execute(
        """
        SELECT res_id
          FROM ir_model_data
         WHERE module = 'ringcentral_integration'
           AND model = 'res.groups.privilege'
           AND name = 'res_groups_privilege_ringcentral'
         LIMIT 1
        """
    )
    unified = cr.fetchone()
    if not unified:
        return
    unified_id = unified[0]

    cr.execute(
        """
        SELECT res_id, name
          FROM ir_model_data
         WHERE module = 'ringcentral_integration'
           AND model = 'res.groups.privilege'
           AND name IN (
               'res_groups_privilege_ringcentral_admin',
               'res_groups_privilege_ringcentral_user'
           )
        """
    )
    legacy_rows = cr.fetchall()
    if not legacy_rows:
        return

    legacy_ids = [row[0] for row in legacy_rows]
    cr.execute(
        """
        UPDATE res_groups
           SET privilege_id = %s
         WHERE privilege_id = ANY(%s)
        """,
        (unified_id, legacy_ids),
    )
    cr.execute(
        """
        DELETE FROM ir_model_data
         WHERE module = 'ringcentral_integration'
           AND model = 'res.groups.privilege'
           AND name IN (
               'res_groups_privilege_ringcentral_admin',
               'res_groups_privilege_ringcentral_user'
           )
        """
    )
    cr.execute(
        "DELETE FROM res_groups_privilege WHERE id = ANY(%s)",
        (legacy_ids,),
    )
