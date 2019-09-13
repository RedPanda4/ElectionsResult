import requests, itertools
from pathlib import Path
import geopandas as gpd
import pickle

parties_s = 'https://www.eleicoes.mai.gov.pt/europeias2019/static-data/PARTIES.json'
children_s = "https://www.eleicoes.mai.gov.pt/europeias2019/static-data/territory-children/TERRITORY-CHILDREN-{0}.json"
results_s = "https://www.eleicoes.mai.gov.pt/europeias2019/static-data/territory-results/TERRITORY-RESULTS-{0}-EUR.json"


def load_or_save(file_p, function, force=False):
	"""
	Dado o ficheiro, verifica se existe
		se sim faz load dos dados
		senão corre a função para gerar os dados e guarda

	For
	:param file_p:
	:param function:
	:param force:
	:return:
	"""
	path = "VAR/{0}".format(file_p)
	if force:
		key = function()
	elif Path(path).exists():
		in_file = open(path, 'rb')
		key = pickle.load(in_file)
		in_file.close()
	else:
		key = function()
		out_file = open(path, 'wb')
		pickle.dump(key, out_file)
		out_file.close()
	return key


def get_children_code(father):
	print("FATHER: {0}".format(father))
	names = requests.get(children_s.format(father))
	return [name['territoryKey'] for name in names.json() if
	        name['territoryKey'] not in ('LOCAL-400000', 'LOCAL-300000')]


def get_all_children():
	keys = list(itertools.chain(*itertools.chain(
		*[[[freguesia for freguesia in get_children_code(concelho)] for concelho in get_children_code(distrito)] for
		  distrito in get_children_code('LOCAL-500000')])))
	return keys


def get_partie_acronym():
	return  ['VOTERS', 'BLANKS', 'NULL'] + [partie['acronym'] for partie in requests.get(parties_s).json()]

def fix_acronym(lis):
	for i in range(len(lis)):
		lis[i] = lis[i].replace('/', '-')
	return lis

def get_results():
	parties = load_or_save(*VAR.get('PARTIES'))
	head = ['Dicofre',]  + parties
	table = {head_v: [] for head_v in head}
	# table = pd.DataFrame(columns=(head))
	children = load_or_save(*VAR.get('DISCONFRE'))
	index = 0

	for discofre_http in children:
		index += 1
		print(index / len(children) * 100)
		data_j = requests.get(results_s.format(discofre_http)).json().get('currentResults')
		table['Dicofre'].append(discofre_http[6:])
		table['VOTERS'].append(data_j.get('percentageVoters'))
		table['BLANKS'].append(data_j.get('blankVotesPercentage'))
		table['NULL'].append(data_j.get('nullVotesPercentage'))
		# data = [int(discofre_http[6:]),
		#         data_j.get('percentageVoters'),
		#         data_j.get('blankVotesPercentage'),
		#         data_j.get('nullVotesPercentage')] + [0 for _ in parties]
		# print(data)
		for partie in data_j.get('resultsParty'):
			table[partie.get('acronym')].append(partie.get('validVotesPercentage'))
	# nao criar erro no nome das diretorias
	table['PCTP-MRPP'] = table['PCTP/MRPP']
	del table['PCTP/MRPP']
	table['PPM.PPV-CDC'] = table['PPM.PPV/CDC']
	del table['PPM.PPV/CDC']
	table['PPD-PSD'] = table['PPD/PSD']
	del table['PPD/PSD']
	return gpd.geodataframe.DataFrame(table)


VAR = {
	'DISCONFRE': ('DISCONFRE.key', get_all_children),
	'PARTIES': ('PARTIES.key', get_partie_acronym),
	'RESULTS': ('RESULTS.key', get_results)
}

if __name__ == '__main__':
	load_or_save(*VAR.get('RESULTS'))
# else:
	get_all_children = load_or_save(*VAR.get('RESULTS'))
	get_partie_acronym = fix_acronym(load_or_save(*VAR.get('PARTIES')))
	get_results = load_or_save(*VAR.get('RESULTS'))
