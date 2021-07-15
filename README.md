# citation_normalisation
## Note: This repository is a contruction site! In general, things should work and are tested but at this stage, I cannot guarantee anything.

The goal of this repository is to create a tool that creates a normalised citation output based on any identifier that refers to a publication. The idea is to gather information using different freely available APIs.

# Usage:

```
import citation_normalisation as cn

# COCONUT Examples
test_list = ['Morvan-Bertrand,Physiol Plant,111,(2001),225',
             '20512739', 
             '10.1021/ol502216j']

references = []
for test_ID in test_list:
    print(cn.get_final_dict_from_ref_str)
    
> {'Morvan-Bertrand,Physiol Plant,111,(2001),225': {'reference': 'Morvan-Bertrand et al., Physiologia Plantarum, 2001, 111 (2), 225', 
                                                    'DOI': '10.1034/j.1399-3054.2001.1110214.x', 
                                                    'PMID': None}}
> {'20512739': {'reference': 'Sheu et al., J Environ Sci Health B, 2010, 45 (5), 478',
                'DOI': '10.1080/03601231003800347', 
                'PMID': '20512739'}}
> {'10.1021/ol502216j': {'reference': 'Grudniewska et al., Organic Letters, 2014, 16 (18), 4695', 
                         'DOI': '10.1021/ol502216j', 
                         'PMID': None}}
  

```
## What works:
Workflow:

    - Detect DOI:
        - Retrieval of information via Metapub or Crossref with DOI    
    - Detect PMID (only works if the input only is the PMID, RegEx for any number would be too unspecific and dangerous.)
        - Retrieval of information via Metapub with PMID
    - No success with DOI/PMID:
        - Retrieval of information via Crossref with given keyword
        - String query based retrieval is only accepted if all of the information is also found in parsed input string
    


