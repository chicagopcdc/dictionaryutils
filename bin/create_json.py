import json
import os
from dictionaryutils import dump_schemas_from_dir

# test

try:
    os.mkdir("artifacts")
except OSError:
    pass

# make sure timing.yaml occurs first in output schema json
yaml_schemas = dump_schemas_from_dir('../../gdcdictionary/schemas/')
yaml_schemas_with_timing = {k: v for k, v in yaml_schemas.items() if k == 'timing.yaml'}
yaml_schemas_without_timing = {k: v for k, v in yaml_schemas.items() if k != 'timing.yaml'}
yaml_schemas = {**yaml_schemas_with_timing, **yaml_schemas_without_timing}
with open(os.path.join("../artifacts", "schema.json"), "w", encoding='utf-8') as f:
    json.dump(yaml_schemas, f)
