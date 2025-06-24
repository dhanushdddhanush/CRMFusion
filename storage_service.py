import os
from azure.data.tables import TableServiceClient
from dotenv import load_dotenv

load_dotenv()


connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")


TABLE_NAME = "UserTokens"


table_service = TableServiceClient.from_connection_string(conn_str=connection_string)
table_client = table_service.get_table_client(table_name=TABLE_NAME)

def store_refresh_token(user_id, refresh_token, partition_key="zoho", extra_data={}):
    entity = {
        "PartitionKey": partition_key,
        "RowKey": user_id,
        "refresh_token": refresh_token
    }
    entity.update(extra_data)
    table_client.upsert_entity(entity)
def delete_refresh_token(user_id, partition_key="zoho"):
    try:
        table_client.delete_entity(partition_key=partition_key, row_key=user_id)
        print(f"Refresh token for user {user_id} in {partition_key} deleted.")
    except Exception as e:
        print(f"Error deleting refresh token for {user_id} in {partition_key}: {e}")
def get_refresh_token(user_id, partition_key="zoho"):
    try:
        entity = table_client.get_entity(partition_key=partition_key, row_key=user_id)
        return entity
    except Exception as e:
        print(f"Error retrieving token: {e}")
        return None
