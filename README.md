# citation_normalisation
The goal of this repository is to create a tool that creates a normalised citation output based on any identifier that refers to a publication. The idea is to gather information using different freely available APIs.

# Usage:

```
import citation_normalisation as cn

test_list = [
    'Rajan OCSR review',
    'Rajan Sorokina Brinkhaus',
    '10.7164/antibiotics.33.463',
    'Kluepfel,J. Antibiotics 25,(1972),109',
    'Actinoids, Transactinoids Holleman',
]

references = []
for test_ID in test_list:
    reference = cn.get_structured_reference(test_ID)
    references.append(reference)
    
for reference in references:
    print(reference)
    
> Rajan, K., Brinkhaus, H., O., Zielesny, A., Steinbeck, C., Journal of Cheminformatics, 2020, 12, 1-13
> Rajan, K., Brinkhaus, H., O., Sorokina, M., Zielesny, A., Steinbeck, C., Journal of Cheminformatics, 2021, 13, 1-9
> Anke, T., Kupka, J., Schramm, G., Steglich, W., The Journal of Antibiotics, 1980, 33, 463-467
> Kluepfel, D., Bagli, J., Baker, H., Charest, M., Kudelski, A., Sehgal, S., N., Vezina, C., The Journal of Antibiotics, 1972, 25, 109-115
> Holleman, A., F., Wiberg, E., Wiberg, N., Inorganic chemistry. Vol. 2. Subgroup elements, lanthanoids, actinoids, transactinoids. 103, 2017
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
    
    - After successful information retrieval:
        - Normalisation of author names (format and upper-/lowercase spelling) in all outputs --> ['Mustermann, M.', 'Musterfrau, L., H.']
        - Normalisation of publication dict keys

## TO DO:
- Get around Google Scholar CAPTCHAS? --> This might not be trivial. 
- Maybe replace scholarly with WOS API (not freely accessible, so not ideal)
- Implement a proper output format for book citations
