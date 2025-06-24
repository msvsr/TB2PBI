from tableauhyperapi import HyperProcess, Connection, Telemetry, TableName

# Path to your .hyper file
hyper_path = r"D:\EProjects\TB2PBI\POC\extracted_twbx_old\Data\TableauTemp\#TableauTemp_0a69a0e09daazz13n86ry0zuxojy.hyper"

with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
    with Connection(endpoint=hyper.endpoint, database=hyper_path) as connection:
        # List all tables in the "Extract" schema
        table_names = connection.catalog.get_table_names("Extract")

        for table in table_names:
            print(f"\n📄 Table: {table.name}")
            # Run SQL query to select all rows
            result = connection.execute_list_query(query=f"SELECT * FROM {table}")
            # Print each row
            for row in result:
                print(row)
