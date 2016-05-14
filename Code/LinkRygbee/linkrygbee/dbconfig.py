# import pyorient
# import sys
#
# client = pyorient.OrientDB("localhost", 2424)
# session_id = client.connect("root", "root@123")
# db_name = "studiodemo"
# db_username = "root"
# db_password = "root@123"
#
# if client.db_exists(db_name, pyorient.STORAGE_TYPE_MEMORY):
#     client.db_open(db_name, db_username, db_password)
#     print(db_name + " opened successfully")
# else:
#     print("database [" + db_name + "] does not exist! session ending...")
#     sys.exit()