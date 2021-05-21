import sys
import os
import re
from typing import List, Tuple, Dict

from metapub import PubMedFetcher
from metapub.exceptions import MetaPubError
from scholarly import scholarly, ProxyGenerator



def contains_all_information(article_dict) -> bool:
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
		elif len(article_dict[key]) <= 1:
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
	return article_dict


def scholarly_request(search_string: str) -> Dict:
	'''This function takes a search keyword string and request information about the corresponding article
	via scholarly'''
	# TODO: Make Proxy usage work. 
	# Use proxy so that we are not blocked by Google Scholar
	#pg = ProxyGenerator()
	#pg.FreeProxies()
	#tor_path = os.path.normpath('C:/Users/Otto Brinkhaus/Downloads/Tor Browser/Browser/TorBrowser/Tor/tor.exe')
	#pg.Tor_Internal(tor_cmd = tor_path)
	#scholarly.use_proxy(pg)
	# Get all available information
	search_query = scholarly.search_pubs(search_string)
	article_info = next(search_query)
	scholarly.fill(article_info)
	article_dict = article_info['bib']
	article_dict = normalize_scholarly_dict(article_dict)
	return article_dict


def get_info_by_DOI(DOI: str) -> Dict:
	'''This function takes a DOI str, requests information about the corresponding
	article via metapub or scholarly and checks if all necessary information has been retrieved.'''
	article_dict = {}
	fetch = PubMedFetcher()
	try:
		article = fetch.article_by_doi(DOI)
		# Save information in Dict
		for info in dir(article):
			if info[0] != '_':
				article_dict[info] = eval('article.' + info)
	except MetaPubError:
		article_dict = scholarly_request(DOI)
	if contains_all_information(article_dict):
		return article_dict


def contains_DOI(ID: str) -> str:
	'''This function takes a string, checks if it contains a DOI and returns
	a string that only contains the DOI if that is the case.'''
	doi_pattern = '(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)'
	match = re.search(doi_pattern, ID)
	if match:
		return match.group()


def get_normalized_author_list(authors) -> str:
	'''This function takes a author str as returned by Scholarly
	or an author list as returned by Metapub and
	return a normalized string.'''
	output_str = ''
	# SCHOLARLY OUTPUT
	if type(authors) == str:
		modified_authors = ""
		# Normalize upper- and lowercase spelling
		for letter_index in range(len(authors)):
			# Uppercase for first name
			if letter_index == 0:
				modified_authors += authors[letter_index].upper()
			# Uppercase after space or hyphen
			elif authors[letter_index-1] in [' ', '-']:
				modified_authors += authors[letter_index].upper()
			# Filter everything that is not a letter and add as lowercase character
			elif re.search('[\w\-\s]', authors[letter_index]):
				modified_authors += authors[letter_index].lower()
		
		# Split on " And " (scholarly output)
		if 'And' in modified_authors.split(' '):
			author_list = modified_authors.split(' And ')
		
		# Add names in abbreviated format to output string
		for name in author_list:
			sub_name_list = name.split(' ')
			output_str += sub_name_list[0] + ', '
			for sub_name in sub_name_list[1:]:
				output_str += sub_name[0] + '., '
	# METAPUB OUTPUT ['Lustig, PA', 'Mueller, H', ...]
	elif type(authors) == list:
		for name in authors:
			for sub_name in name.split(' '):
				# abbreviated first name(s)
				if sub_name.isupper():
					for char in sub_name:
						output_str += char + '., '
				# surname
				else:
					output_str += sub_name + '., '
	#Remove last '.,'
	output_str = output_str[:-2]
	return output_str


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


def create_normalized_reference(article_dict: Dict) -> str:
	'''This function takes a dictionary with information about a publication (as returned by
	get_info_by_DOI() or scholarly_request()) and returns a normalized reference string.'''
	reference_str = ''
	# Add authors
	reference_str += get_normalized_author_list(article_dict['authors']) + ', '
	# If the journal name is known: Create something with the pattern
	# #Smith, J et al, J. Odd Results, 1968, 10, 1020-30
	if 'journal' in article_dict.keys():
		reference_str += normalize_title(article_dict['journal'], only_if_homogeneous=False) + ', '
		reference_str += article_dict['year'] + ', '
		if 'volume' in article_dict.keys():
			reference_str += article_dict['volume'] + ', '
		if 'pages' in article_dict.keys():
			reference_str += article_dict['pages'].replace('--', '-')
	else:
		reference_str += normalize_title(article_dict['title']) + ', '
		reference_str += article_dict['year']
	return reference_str


def get_structured_reference(unstructured_publication_ID: str) -> Dict:
	'''This function takes a string that contains a reference to a publication.
	It uses
	- metapub (PubMed API)
	- scholarly (Google Scholar API)
	to request more information and returns a Dict that contains
	all gathered information about the publication in a structured format.'''
	DOI = contains_DOI(unstructured_publication_ID)
	if DOI:
		article_dict = get_info_by_DOI(DOI)
	# If no DOI is available, start a scholarly request with the given string
	else:
		article_dict = scholarly_request(unstructured_publication_ID)
	#print(article_dict)
	if article_dict:
		print(article_dict)
		normalized_reference = create_normalized_reference(article_dict)
		return normalized_reference
	else:
		print('Unable to retrieve information based on: ' + unstructured_publication_ID)
		
	
	


if __name__ == '__main__':
	if len(sys.argv) == 2:
		get_structured_reference(sys.argv[1])
	else:
		print('Usage: ' + sys.argv[0] + 'unstructured_publication_ID')
