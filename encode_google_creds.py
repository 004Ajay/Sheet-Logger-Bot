import json
import base64

service_key= YOUR_OAUTH2.0_CREDENTIALS_JSON_HERE

# convert json to a string
service_key = json.dumps(service_key)

# encode service key
encoded_service_key = base64.b64encode(service_key.encode('utf-8'))

print(encoded_service_key)
# output: b'many_characters_here'

# put this b'many_characters' in your .env file

# use that credential to call Sheets in bot.py (lines 17-28)