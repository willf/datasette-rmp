CREATE TABLE facilities_with_chemicals_and_naics AS
WITH facility_chemicals AS (
    SELECT
        "EPA Facility ID",
        group_concat(Chemical, ', ') AS Chemicals
    FROM (
        SELECT DISTINCT
            "EPA Facility ID",
            Chemical
        FROM
            facility_chemical
    )
    GROUP BY
        "EPA Facility ID"
),
facility_naics_names AS (
    SELECT
        "EPA Facility ID",
        group_concat(name, ', ') AS NAICS_Names
    FROM (
        SELECT DISTINCT
            fn."EPA Facility ID",
            nn.name
        FROM
            facility_naics fn
        LEFT JOIN
            naics_names nn
        ON
            fn."NAICS Code" = nn.code
    )
    GROUP BY
        "EPA Facility ID"
)
SELECT
    f."EPA Facility ID",
    f.Report,
    f."Facility Name",
    f."Facility Address",
    f.City,
    f.State,
    f.County,
    f.Zip,
    f."Facility DUNS",
    f.Latitude,
    f.Longitude,
    fc.Chemicals,
    fnn.NAICS_Names
FROM
    facilities f
LEFT JOIN
    facility_chemicals fc
ON
    f."EPA Facility ID" = fc."EPA Facility ID"
LEFT JOIN
    facility_naics_names fnn
ON
    f."EPA Facility ID" = fnn."EPA Facility ID";
