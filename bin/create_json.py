import json
import os
from dictionaryutils import dump_schemas_from_dir

# test

try:
    os.mkdir("artifacts")
except OSError:
    pass

with open(os.path.join("artifacts", "schema.json"), "w") as f:
    json.dump(dump_schemas_from_dir('../gdcdictionary/schemas/'), f)


