SELECT
    CASE CAST(severity AS UInt8)
        WHEN 4 THEN 'Critical'
        WHEN 3 THEN 'High'
        WHEN 1 THEN 'Warning'
        ELSE 'Other'
    END AS severity,
    description,
    log_line,
    source_table
FROM
(
    -- fh_violations: log_line
    SELECT
        severity,
        description,
        log_line,
        'fh_violations' AS source_table
    FROM l1_app_db.fh_violations
    WHERE CAST(severity AS UInt8) IN (4, 3, 1)

    UNION ALL

    -- cp_up_coupling: cp_log + up_log as log_line
    SELECT
        severity,
        description,
        concat(cp_log, ' | ', up_log) AS log_line,
        'cp_up_coupling' AS source_table
    FROM l1_app_db.cp_up_coupling
    WHERE CAST(severity AS UInt8) IN (4, 3, 1)

    UNION ALL

    -- interference_splane: log_line
    SELECT
        severity,
        description,
        log_line,
        'interference_splane' AS source_table
    FROM l1_app_db.interference_splane
    WHERE CAST(severity AS UInt8) IN (4, 3, 1)
)
ORDER BY severity, source_table, log_line;
