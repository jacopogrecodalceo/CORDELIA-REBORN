from pathlib import Path

core = Path(__file__).parent
main_dir = core.parent

csound = core / 'csound'
include = csound / 'orc' / 'include.orc'

templates = core / 'templates'

config = main_dir / 'config'
adc_dev_list = config / 'adc'
dac_dev_list = config / 'dac'

# corpus directories
corpus = main_dir / 'corpus' # this is the main directory corpus

corpus_json_dir = corpus / '_json'

func_corpus_dir = corpus / 'func'

instr_corpus_dir = corpus / 'instr'
instr_corpus_json = corpus_json_dir / 'instrument.json'

env_corpus_dir = corpus / 'env'
env_corpus_json = corpus_json_dir / 'env.json'

modifier_corpus_dir = corpus / 'mod'
modifier_corpus_json = corpus_json_dir / 'modifier.json'

scala_corpus_dir = corpus / 'scala'
scala_corpus_json = corpus_json_dir / 'scala.json'

intervals_corpus_json = corpus_json_dir / 'intervals.json'

qualities_corpus_dir = corpus / 'qualities' 

