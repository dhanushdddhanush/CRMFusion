def store_refresh_token(user_id, refresh_token, partition_key="zoho", extra_data={}):
    entity = {
        "PartitionKey": partition_key,
        "RowKey": user_id,
        "refresh_token": refresh_token
    }
    entity.update(extra_data)
    table_client.upsert_entity(entity)

def get_refresh_token(user_id, partition_key="zoho"):
    try:
        entity = table_client.get_entity(partition_key=partition_key, row_key=user_id)
        return entity
    except Exception as e:
        print(f"Error retrieving token: {e}")
        return None
