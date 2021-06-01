import sys
import os
import re
from typing import List, Tuple, Dict
import time

from metapub import PubMedFetcher
from metapub.exceptions import MetaPubError
from scholarly import scholarly
from scholarly._navigator import MaxTriesExceededException
from crossref.restful import Works

#import requests


def contains_minimal_information(article_dict) -> bool:
	'''This function takes a dictionary, checks if a minimum of information is included
	Necessary keys: "title", "authors", "year", "pages"
	Additionally one of the following keys: ("journal", "book_title")
	It checks if the corresponding values exist and returns a bool that indicates 
	the result.'''
	# TODO: Define minimal standard what information needs to be in there
	necessary_keys = ['title', 'authors', 'year']
	#one_of_key_tuples = [('journal', 'book_title')]
	one_of_key_tuples = []
	# Check that all necessary keys exist and have a value
	for key in necessary_keys:
		if key not in article_dict.keys():
			break
		elif not article_dict[key]:
			break
	# Check that one key from each one_of_key_tuple exists and has a value
	else:
		for key_tuple in one_of_key_tuples:
			key_1, key_2 = key_tuple
			if key_1 not in article_dict.keys():
				if key_2 not in article_dict.keys():
					break
				elif not article_dict[key_2]:
					break
			elif not article_dict[key_1]:
				break
		else:
			# If no "break" has been executed until here, the article_dict is complete
			return True 


def DOI_validity_check(article_dict: Dict, DOI: str) -> bool:
	'''This function takes a DOI string and a a dictionary. It checks if the key "doi" of the 
	dictionary has a value that is not None and that it and the given DOI are the same.'''
	if 'doi' in article_dict.keys():
		if article_dict['doi'] == DOI:
			return True


def normalize_scholarly_dict(article_dict: Dict) -> Dict:
	'''This function takes a dictionary as returned by scholarly (output['bib']) and returns
	the same dictionary with adapted keys so that they fit the metapub output'''
	# Per tuple, a key that matches the first element is replaced with the second element
	old_new_key_tuples = [('author', 'authors'), ('pub_year', 'year')]
	for key_tuple in old_new_key_tuples:
		if key_tuple[0] in article_dict.keys():
			article_dict[key_tuple[1]] = article_dict.pop(key_tuple[0])
	# Normalize author list
	article_dict['authors'] = get_normalized_author_list(article_dict['authors'], 'scholarly')
	return article_dict


def scholarly_request(search_string: str) -> Dict:
	'''This function takes a search keyword string and request information about the corresponding article
	via scholarly'''
	# Get all available information
	search_query = scholarly.search_pubs(search_string)
	article_info = next(search_query)
	scholarly.fill(article_info)
	article_dict = article_info['bib']
	article_dict = normalize_scholarly_dict(article_dict)
	article_dict = add_retrieval_information(article_dict, 'Scholarly', 'unstructured_ID', search_string)
	return article_dict


def crossrefAPI_query(keyword: str) -> Dict:
	'''This function takes a keyword str and sends an according GET request to the CrossRef API.
	A normalized version of the first (most 'relevant') result is returned.'''
	article_dict = False
	works = Works()
	# If there is a timeout, try again (5 times)
	for _ in range(5):
		try:
			result = works.query(keyword).sort("relevance")
			for entry in result:
				# Take first result
				article_dict = entry
				break
		except:
			pass
	if article_dict:
		article_dict = normalize_crossref_dict(article_dict)
		if contains_minimal_information(article_dict):
			article_dict = add_retrieval_information(article_dict, 'Crossref', 'unstructured_ID', keyword)
		return article_dict


def get_info_by_DOI(DOI: str) -> Dict:
	'''This function takes a DOI str, requests information about the corresponding
	article via metapub or crossref and checks if all necessary information has been retrieved.'''
	article_dict = {}
	fetch = PubMedFetcher()
	try:
		article = fetch.article_by_doi(DOI)
		# Save information in Dict
		for info in dir(article):
			if info[0] != '_':
				# Normalize author list
				if info == 'authors':
					article_dict[info] = get_normalized_author_list(eval('article.' + info), 'metapub')
				else:
					article_dict[info] = eval('article.' + info)
		# Add data retrieval info to the dict
		article_dict = add_retrieval_information(article_dict, 'MetaPub', 'DOI', DOI)
	except MetaPubError:
		# If it does not work via Metapub, do it via Crossref Api
		# If there is a timeout, try again (5 times)
		for _ in range(5):
			try:
				works = Works()
				article_dict = works.doi(DOI)
				break
			except:
				pass
		article_dict = normalize_crossref_dict(article_dict)
		# Add data retrieval info to the dict
		article_dict = add_retrieval_information(article_dict, 'Crossref', 'DOI', DOI)
	if contains_minimal_information(article_dict):
		return article_dict


def get_info_by_PMID(PMID: str) -> Dict:
	'''This function takes a PMID str, requests information about the corresponding
	article via metapub and checks if all necessary information has been retrieved.'''
	article_dict = {}
	fetch = PubMedFetcher()
	try:
		article = fetch.article_by_pmid(PMID)
		# Save information in Dict
		for info in dir(article):
			if info[0] != '_':
				# Normalize author list
				if info == 'authors':
					article_dict[info] = get_normalized_author_list(eval('article.' + info), 'metapub')
				else:
					article_dict[info] = eval('article.' + info)
	except MetaPubError:
		pass
	if contains_minimal_information(article_dict):
		# Add data retrieval info to the dict and return it
		article_dict = add_retrieval_information(article_dict, 'MetaPub', 'PMID', PMID)
		return article_dict


def add_retrieval_information(reference_dict: Dict, retrieved_from: str, query_str_type: str, query_str: str) -> Dict:
	'''This function takes a reference_dict (Dict) and information about where the reference data was retrieved from,
	what type of query str and what exact query str have been used to retrieve the information. It adds this data to
	the dictionary and returns the modified dictionary.'''
	reference_dict['reference_retrieved_from'] = retrieved_from
	reference_dict['query_str_type'] = query_str_type
	reference_dict['query_str'] = query_str
	return reference_dict


def contains_DOI(ID: str) -> str:
	'''This function takes a string, checks if it contains a DOI and returns
	a string that only contains the DOI if that is the case.'''
	doi_pattern = '(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)'
	match = re.search(doi_pattern, ID)
	if match:
		return match.group()


def normalize_name_spelling(name: str) -> str:
	'''This function takes a string and returns the same string with normalized
	upper- and lowercase spelling ('MUSTERMANN, MAX-MORITZ' -> 'Mustermann, Max-Moritz').'''
	normalized_name = ''
	for letter_index in range(len(name)):
		# Uppercase for first name
		if letter_index == 0:
			normalized_name += name[letter_index].upper()
		# Uppercase after space or hyphen
		elif name[letter_index-1] in [' ', '-']:
			normalized_name += name[letter_index].upper()
		#elif re.search('[\w\-\s]', author[letter_index]): # Filter everything that is not a letter and add as lowercase character

		else:
			normalized_name += name[letter_index].lower()
	return normalized_name


def get_normalized_author_list(authors, input_type: str) -> List[str]:
	'''This function takes a author str as returned by Scholarly,
	an author list as returned by the Crossref API
	or an author list as returned by Metapub and
	return list of normalized author strings.
	The input_type has to be specified as 'scholarly', 'metapub' or 'crossref'.
	-> ['Doe, J.', 'Mustermann, M.']'''
	# SCHOLARLY OUTPUT
	# 'Rajan, Kohulan and Brinkhaus, Henning Otto and SOROKINA, MARIA and Zielesny, Achim and Steinbeck, Christoph'
	author_list = []
	if input_type == 'scholarly':
		if ' And ' in authors:
			orig_author_list = authors.split(' And ')
		elif ' and ' in authors:
			orig_author_list = authors.split(' and ')
		# Normalize upper- and lowercase spelling
		for author in orig_author_list:
			normalized_author = ''

			for split_subname_index in range(len(author.split(', '))):
				# Copy complete surname with normalized spelling
				if split_subname_index == 0:
					normalized_author += normalize_name_spelling(author.split(', ')[split_subname_index])
				# Only copy abbreviated first names
				else:
					normalized_author += ', '
					for letter_index in range(len(author.split(', ')[split_subname_index])):
						if authors[letter_index-1] in [' ', '-']:
							normalized_author += author[letter_index].upper()  
							if split_subname_index != len(author.split(', ')):
								normalized_author += '., '
			author_list.append(normalized_author)

	# METAPUB OUTPUT ['Lustig, P', 'Mueller, HO', ...]
	elif input_type == 'metapub':
		for name in authors:
			normalized_author = ''
			for sub_name in name.split(' '):
				# abbreviated first name(s)
				if sub_name.isupper():
					for char in sub_name:
						normalized_author += char + '., '
				# surname
				else:
					normalized_author += sub_name + '., '
			author_list.append(normalized_author)

	# CROSSREF OUTPUT: [{'given': 'Kohulan', 'family': 'Rajan', 'sequence': 'first', 'affiliation': []}, {'given': 'Henning Otto', 'family': 'Brinkhaus', 'sequence': 'additional', 'affiliation': []}]
	elif input_type == 'crossref':
		for author_dict in authors:
			normalized_author = ''
			try:
				# Personal name format
				normalized_author += normalize_name_spelling(author_dict['family']) +', '
				first_names = author_dict['given'].split()
				for first_name_index in range(len(first_names)):
					normalized_author += first_names[first_name_index][0].upper() + '.'
					if first_name_index != len(first_names) - 1:
						normalized_author += ', '
			except KeyError:
				# Organisation name format
				normalized_author = author_dict['name']
			author_list.append(normalized_author)

	return author_list


def normalize_title(title: str, only_if_homogeneous: bool = True) -> str:
	'''This function takes a string and returns the same string where the first character of every
	word that is not on an exception-list is an upper-case character.
	If only_if_homogeneous, the string is only changed if it is completely composed of upper- or lowercase characters.'''
	# TODO: Find a better solution for this.
	lowercase_list = ['of', 'a', 'from', 'the', 'an', 'not', 'is', 'that', 'as', 'and', 'are']
	if title.isupper() or title.islower() or not only_if_homogeneous:
		split_str = title.split(' ')
		title = ''
		for word in split_str:
			if word.lower() not in lowercase_list: 
				title += word[0].upper()
				for char in word[1:]:
					title += char.lower()
			else:
				title += word
			title += ' '
		title = title[:-1]
	return title


def normalize_crossref_dict(crossref_dict: Dict) -> Dict:
	'''This function takes a dict with publication metadata as returned by the 
	Crossref API and returns a dict which contains the essential information in 
	the same format as returned by Metapub.'''
	normalized_dict = {}
	normkeys = ['title', 'abstract', 'DOI', 'issue', 'volume']
	for normkey in normkeys:
		if normkey in crossref_dict.keys():
			content = crossref_dict[normkey]
			if type(content) == list:
				normalized_dict[normkey] = content[0]
			else:
				normalized_dict[normkey] = content
	# year
	if 'issued' in crossref_dict.keys():
		if 'date-parts' in crossref_dict['issued']:
			normalized_dict['year'] = crossref_dict['issued']['date-parts'][0][0]
			
	# journal/book
	if 'type' in crossref_dict.keys():
		if crossref_dict['type'] == 'journal-article':
			normalized_dict['journal'] = crossref_dict['container-title'][0]
	# author list
	if 'author' in crossref_dict.keys(): 
		normalized_dict['authors'] = get_normalized_author_list(crossref_dict['author'], 'crossref')
	return normalized_dict


def create_normalized_reference_str(article_dict: Dict) -> str:
	'''This function takes a dictionary with information about a publication (as returned by
	get_info_by_DOI() or scholarly_request()) and returns a normalized reference string.'''
	reference_str = ''
	# Add authors
	for author in article_dict['authors']:
		reference_str += author + ', '
	# If the journal name is known: Create something with the pattern
	# #Smith, J et al, J. Odd Results, 1968, 10, 1020-30
	if 'journal' in article_dict.keys():
		reference_str += normalize_title(article_dict['journal'], only_if_homogeneous=False) + ', '
		reference_str += str(article_dict['year']) + ', '
		if 'volume' in article_dict.keys():
			reference_str += article_dict['volume'] + ', '
		if 'pages' in article_dict.keys():
			reference_str += article_dict['pages'].replace('--', '-') + ', '
	else:
		reference_str += normalize_title(article_dict['title']) + ', '
		reference_str += str(article_dict['year']) + ', '
	reference_str = reference_str[:-2]
	if 'DOI' in article_dict.keys():
		reference_str += ' - DOI: ' + article_dict['DOI']
	return reference_str


def reference_quality_assurance(reference_dict: Dict) -> bool:
	'''This function checks the retrieved reference dict to make sure that the retrieved
	information matches the original input string. It returns a corresponding bool.'''
	# If the query was based on a PMID or a DOI, there is no reason to not to trust the retrieved information.
	if reference_dict['query_str_type'] in ['DOI', 'PMID']:
		return True
	# If the query was based on some keyword str, the result might be flawed.
	else:
		# Make sure that the year and the last name of the first author appear in the original query str
		# TODO: Think about a better solution for this.
		query_str = reference_dict['query_str']
		if str(reference_dict['year']) in query_str:
			first_author_surname = reference_dict['authors'][0].split()[0]
			if first_author_surname.lower() in query_str.lower():
				return True



def get_structured_reference(unstructured_publication_ID: str) -> Dict:
	'''This function takes a string that contains a reference to a publication.
	It uses
	- Metapub (PubMed API)
	- Crossref API
	- scholarly (Google Scholar API) [for now removed because of CAPTCHAS]
	to request more information and returns a Dict that contains
	all gathered information about the publication in a structured format.'''
	
	# If there is a DOI in the input str, try to use Metapub and 
	article_dict = False
	DOI = contains_DOI(unstructured_publication_ID)
	if DOI:
		article_dict = get_info_by_DOI(DOI)
	# If no DOI is available or the queries have not returned anything reasonable, 
	#check if the given ID only consists of numbers. If that is the case, interpret 
	# it as a PMID for a Metapub query.
	if not article_dict:
		if unstructured_publication_ID.isdigit():
			article_dict = get_info_by_PMID(unstructured_publication_ID)
	# If it has not worked until now, use crossref API and take most 'relevant' result
	# TODO: Some sort of validation that we get the right result here
	if not article_dict:
		article_dict = crossrefAPI_query(unstructured_publication_ID)
		
	# If we still have not gotten a sufficient result, try Google Scholar and take most 'relevant' result
	if not contains_minimal_information(article_dict):
		try:
			article_dict = scholarly_request(unstructured_publication_ID)
		except StopIteration:
			article_dict = False
		except MaxTriesExceededException:
			article_dict = False
	return article_dict


#def WOS_query(keyword: str):
#	'''Does not work'''
#	with WosClient('john.doe@uni-jena.de', 'insert_password_here') as client:
#		result = wos.utils.query(client, keyword)
#		return result



if __name__ == '__main__':
	if len(sys.argv) == 2:
		get_structured_reference(sys.argv[1])
	else:
		print('Usage: ' + sys.argv[0] + 'unstructured_publication_ID')
