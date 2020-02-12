
import boto3, botocore, json, decimal
from typing import List, Dict, Set, Optional, Any

class DecimalEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

class GlobalUserTableAccessor(object):

    # region is hardcoded to us-east-1
    _resource = boto3.resource('dynamodb', region_name='us-east-1')

    @classmethod
    def _get_table(cls, table_name: str) -> Any:
        """
        This function will return a handle to a Table to perform operations on.
        """
        return cls._resource.Table(table_name)

    @classmethod
    def get_item(cls, table_name: str, request_specs: dict) -> Optional[Any]:
        """
        Retrieve the item that matches the request_specs from the table.
        Returns None if item is not found, or the Item object (dictionary) if it is.
        """
        table = cls._get_table(table_name)
        item_response = table.get_item(Key=request_specs)

        if 'Item' in item_response:
            return json.loads(json.dumps(item_response['Item'], cls=DecimalEncoder)) # to convert to python floats/ints, from DynamoDB decimals
        else:
            return None