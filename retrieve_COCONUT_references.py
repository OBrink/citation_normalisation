import sys
import os
from typing import Tuple, List, Dict
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
import citation_normalisation as cn
import reference_parser as rp


def read_COCONUT_references(coconut_references_csv_path: str) -> List[str]:
    '''This function reads a csv file with 2 columns ('coconut_id', 'citationDOI') at coconut_references_csv_path.
    It returns a list unique reference str.'''

    # Read data from file
    coconut_references = pd.read_csv(os.path.normpath(coconut_references_csv_path))
    unstructured_references = coconut_references['citationDOI']
    
    # Filter non-unique references and "NA"
    unique_references = []
    for ref_list in unstructured_references:
        for ref in eval(ref_list):
            if ref not in unique_references:
                if ref != 'NA':
                    unique_references.append(ref)
    return unique_references

def retrieve_reference_data(reference: str) -> None:
    '''This function takes a reference str, retrieves information about it from MetaPub or Crossref
    and writes the retrieved information into a file. It returns None.'''
    
    # In case this script needs to be restarted due to timeout or whatever reason:
    # Do not retrieve data that already has been retrieved.
    
    if os.path.exists('COCONUT_reference_retrieval_raw_output.tsv'):
        with open('COCONUT_reference_retrieval_raw_output.tsv', 'r') as output:
            lines = output.readlines()
            already_retrieved_refs = [line.split('\t')[0] for line in lines]
    else:
        already_retrieved_refs = []

    # Retrieve information from MetaPub or Crossref       
    if reference not in already_retrieved_refs:
        print('Retrieving ref N° {}: {}'.format(len(already_retrieved_refs), reference))
        ref_dict = cn.retrieve_info_MetaPub_Crossref(reference, only_DOI_PMID=False)
        with open('COCONUT_reference_retrieval_raw_output.tsv', 'a') as output:
            output.write(reference + "\t" + str(ref_dict) + "\n")
        return None

def retrieval_coordination(coconut_references_csv_path: str) -> None:
    '''
    This function is responsible for the coordination of
    - Reading the original COCONUT references
    - Retrieving information about the publications (parallelised)
    - Saving the retrieved information in a csv file
    '''
    # Read data from file
    references = read_COCONUT_references(coconut_references_csv_path)
    # Run information retrieval
    with ThreadPool(35) as pool:
        _ = pool.map(retrieve_reference_data, references)
    print('Finished information retrieval.')


def read_false_retrieved_references(coconut_references_csv_path: str) -> List[Dict]:
    '''
    This function reads the retrieved dicts which have been falsified in the reference
    confirmation procedure. It returns a list of parsed reference Dicts.
    '''
    # Load all retrieved keyword-query-based reference dicts
    keyword_based_dicts = []
    with open('./retrieved_dicts_filtered.csv') as filtered_retrieved_dicts:
        for entry in filtered_retrieved_dicts.readlines():
            query_type, retrieved_dict = entry.split(', ', 1)
            if query_type == 'KEYWORD':
                keyword_based_dicts.append(eval(retrieved_dict))
    # Check which reference dicts do not contain valid information
    parser = rp.reference_parser()
    falsified_reference_dicts = []
    for retrieved_dict in keyword_based_dicts:
        norm_keyword_dict = cn.normalize_crossref_dict(retrieved_dict)
        if norm_keyword_dict:
            parsed_info = parser(norm_keyword_dict['query_str'])
            if parsed_info:
                # If a reference can be confirmed as in the reference str: Good.
                if cn.is_same_publication(parsed_info, norm_keyword_dict):
                    pass
                # If a reference can be identified as one of the known books: Good.
                elif "harborne" in norm_keyword_dict['query_str'].lower():
                    pass
                # Retrieved info does not overlap with parsed info and does not refer to known book: Bad.
                else:
                    parsed_info['query_str'] = norm_keyword_dict['query_str']
                    falsified_reference_dicts.append(parsed_info)
    return falsified_reference_dicts


def detailed_retrieve_reference_data(reference: str) -> None:
    '''This function takes a reference str, retrieves information about it from Crossref
    and writes the retrieved information into a file. It returns None.
    _____________________________________
    Difference between this function and retrieve_reference_data():
    Only Crossref, confirmation of retrieved information is done during retrieval,
    first 200 entries in Crossref are searched for a match instead of just taking the 
    first one.'''
    
    # In case this script needs to be restarted due to timeout or whatever reason:
    # Do not retrieve data that already has been retrieved.
    
    if os.path.exists('COCONUT_reference_second_retrieval_raw_output.tsv'):
        with open('COCONUT_reference_second_retrieval_raw_output.tsv', 'r') as output:
            lines = output.readlines()
            already_retrieved_refs = [line.split('\t')[0] for line in lines]
    else:
        already_retrieved_refs = []

    # Retrieve information from MetaPub or Crossref       
    if reference['query_str'] not in already_retrieved_refs:
        print('Retrieving ref N° {}: {}'.format(len(already_retrieved_refs), reference))
        ref_dict = cn.crossrefAPI_improved_query(reference)
        with open('COCONUT_reference_second_retrieval_raw_output.tsv', 'a') as output:
            output.write(reference['query_str'] + "\t" + str(ref_dict) + "\n")
        return None


def second_retrieval_coordination(coconut_references_csv_path: str) -> None:
    '''
    This function is responsible for the coordination of
    - Reading the filtered retrieved references after the first retrieval
    - Retrieving information about the publications (parallelised)
    - Saving the retrieved information in a csv file
    '''
    # Read data from file
    references = read_false_retrieved_references(coconut_references_csv_path)
    # Run information retrieval
    with ThreadPool(35) as pool:
        _ = pool.map(detailed_retrieve_reference_data, references)
    print('Finished information retrieval.')


if __name__ == '__main__':
    if len(sys.argv) == 2:
        second_retrieval_coordination(sys.argv[1])
    else:
        print('Usage: ' + sys.argv[0] + 'coconut_reference_file')

