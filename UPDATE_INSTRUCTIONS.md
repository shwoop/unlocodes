# UPDATE INSTRUCTIONS

Once a list of ports has been curated and exported viat the unlocodes script
follow these instructions for applying them ao a zone.


*   gather the necessary details to psql into the environment

    `psql -h $host -U $user $database`

*   run the psql comment to get a db prompt, run it from this directory or please
    adjust the following commands to point to the csv.

*   Begin by taking a backup of the table

    `create table ps_voyage_port_backup as select * from ps_voyage_port;`

*   Sanity check to make sure our backup was successful.

    ```
    select count(*) from ps_voyage_port;
    select count(*) from ps_voyage_port_backup;
    select * from ps_voyage_port except (select * from ps_voyage_port_backup);
    ```

*   Perform the update

    `\copy ps_voyage_port (code, name, country_code_id, latitude, longitude, scale, polygon, position, iso_country_id, port_source, ihs_port_id, world_port_number) FROM 'output/ports_to_insert.csv' WITH DELIMITER ',' CSV HEADER;`

*   Check that the copy command hasn't overwritten the original records

    `select * from ps_voyage_port_backup except (select * from ps_voyage_port);`

*   If the above check fails, or if the environment goes haywire with the new
    data, we can roll back by running the following commands.

    `delete from ps_voyage_port where code not in (select code from ps_voyage_port_backup);`
