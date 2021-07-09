import sys
from pymongo import MongoClient
import pandas as pd

def main():
    # Set paths and load DB client
    mongoPort = sys.argv[1]
    mongoDatabase = sys.argv[2]
    client = MongoClient("localhost:{}".format(mongoPort))
    db = client[mongoDatabase]

    # Load dict that maps every old reference string to dict containing a normalised reference string,
    # a DOI and a PMID (if they are not given, these keys refer to None)
    # Example of entry in references:
    #'Ito,Chem. Pharm. Bull.,37,(1989),819': {'reference': 'Ito, Chemical and Pharmaceutical Bulletin, 1989, 37 (3), 819', 
    #                                         'DOI': '10.1248/cpb.37.819', 
    #                                         'PMID': None}
    with open('COCONUT_reference_dict.json', 'r') as references:
        references = eval(references.read())

    # MARIA - I don't know how exactly it works in COCONUT
    # We need to retrieve the original reference str in COCONUT (does not matter if it is a DOI, a PMID or something else)
    # Then, the old reference str then must be used as a key to get the new data from the loaded dict
    # I tried to do it as in your example.
    # The question now is what to do when we have a reference str AND a DOI or a PMID
    # In the csv file you have sent me, the reference is saved under the keyword "citationDOI".
    # Hence, I assume that this is where you save the normal reference str
    # I have now solved this by merging them in one str (see below)

    collection = db.uniqueNaturalProduct.aggregate([{'$project': {'_id': 0, 'coconut_id': 1, 'citationDOI': 1}}])
    allnp = pd.DataFrame(list(collection))

    for index, row in allnp.iterrows():
        coconut_id = row['coconut_id'] # str
        old_refs = eval(row["citationDOI"]) # List[str]
        new_refs = []
        # Go through all old references and replace them with the new reference (if it exists)
        for old_ref in old_refs:
            if old_ref in references.keys():
                new_ref = references[old_ref]['reference']
                for DOIPMID in ['DOI', 'PMID']:
                    # If they are given: Add DOI and/or PMID
                    if references[old_ref][DOIPMID]:
                        new_ref += '; {}'.format(DOIPMID, references[old_ref][DOIPMID])
                new_refs.append(new_ref)
            # If no new data has been retrieved for the old reference:    
            else:
                new_refs.append(old_ref)

        # Replace old reference list with modified reference list 
        db.uniqueNaturalProduct.update_one({'coconut_id': coconut_id}, {"$set": {"citationDOI": new_refs}})

    print("The old references have been replaced.")

if __name__ == '__main__':
    if len(sys.argv) == 4:
        main()
    else:
        print('Usage: python {} mongoPort_PATH mongoDatabase_PATH reference_map_JSON'.format(sys.argv[0]))



