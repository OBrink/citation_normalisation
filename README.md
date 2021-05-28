# citation_normalisation
## Note: This repository is a contruction site! In general, things should work and are tested but at this stage, I cannot guarantee anything.

The goal of this repository is to create a tool that creates a normalised citation output based on any identifier that refers to a publication. The idea is to gather information using different freely available APIs.

# Usage:

```
import citation_normalisation as cn

# COCONUT Examples
test_list = [
    '10.7164/antibiotics.33.463',
    'Kluepfel,J. Antibiotics 25,(1972),109',
    'Ratnayake,J.Nat.Prod.,71,(2008),403',
    'Probst,Helvetica Chimica Acta,64,(1981),2056'
    'Braz Filho,Phytochem.,19,(1980),2003'
]

references = []
for test_ID in test_list:
    reference = cn.get_structured_reference(test_ID)
    references.append(reference)
    
# Print exemplary dict
for key in references[0].keys():
    print(key + ' - ' + str(references[1][key]))
> title - MYRIOCIN, A NEW ANTIFUNGAL ANTIBIOTIC FROM MYRIOCOCCUM ALBOMYCES
> DOI - 10.7164/antibiotics.25.109
> issue - 2
> volume - 25
> year - 1972
> journal - The Journal of Antibiotics
> authors - ['Kluepfel, D.', 'Bagli, J.', 'Baker, H.', 'Charest, M.', 'Kudelski, A.', 'Sehgal, S., N.', 'Vézina, C.']
  
for reference_dict in references:
    reference_str = cn.create_normalized_reference_str(reference_dict)
    print(reference_str)
    
> Anke, T., Kupka, J., Schramm, G., Steglich, W., The Journal of Antibiotics, 1980, 33 - DOI: 10.7164/antibiotics.33.463
> Kluepfel, D., Bagli, J., Baker, H., Charest, M., Kudelski, A., Sehgal, S., N., Vézina, C., The Journal of Antibiotics, 1972, 25 - DOI: 10.7164/antibiotics.25.109
> Ratnayake, R., Fremlin, L., J., Lacey, E., Gill, J., H., Capon, R., J., Journal of Natural Products, 2008, 71 - DOI: 10.1021/np070589g
> Probst, A., Tamm, C., Helvetica Chimica Acta, 1981, 64 - DOI: 10.1002/hlca.19810640710
> Filho, R., B., De Moraes, M., P., Gottlieb, O., R., Phytochemistry, 1980, 19 - DOI: 10.1016/0031-9422(80)83022-6

```
## What works:
Workflow:

    - Detect DOI:
        - Retrieval of information via Metapub or Crossref with DOI    
    - Detect PMID (only works if the input only is the PMID, RegEx for any number would be too unspecific and dangerous.)
        - Retrieval of information via Metapub with PMID
    - No success with DOI/PMID:
        - Retrieval of information via Crossref with given keyword
    - Emergency solution if Metapub and Crossref have failed: 
        - Retrieval of inforamtion via Scholarly (problematic due to CAPTCHAs by Google) with given keyword
    - In general: 
        - If API requests fail, sleep three seconds, then try again (20 times)
    
    - After successful information retrieval:
        - Normalisation of author names (format and upper-/lowercase spelling) in all outputs --> ['Mustermann, M.', 'Musterfrau, L., H.']
        - Normalisation of publication dict keys

## TO DO:
- [Get around Google Scholar CAPTCHAS? --> This might not be trivial.]
- [Maybe replace scholarly with WOS API (not freely accessible, so not ideal)]
- Implement a proper output format for book citations
- Check if less 'sleeping' time after timeouts causes problems (right now, it can take forever)
- Fix odd behavior of author name normalization for Scholarly Output
- Perform some sort of validation that the retrieved reference is truly the right reference
