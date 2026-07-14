
import orjson
import cordelia.path
 
# ---------------------------------------------------------------------------- #
#                                     DATA                                     #
# ---------------------------------------------------------------------------- #
# data is basically only json
data = {
	f.stem: orjson.loads(f.read_bytes())
	for f in cordelia.path.corpus_json_dir.glob("*.json")
}

