# Dear Maria, I am sorry that I bothered you during your time off. This is not important and can wait. I had misunderstood you on Wednesday and had not looked in your calendar. Do not worry about this nonsense here until the 24th. Have a nice time and enjoy your holiday!

# citation_normalisation
The goal of this repository is to create a tool that creates a normalised citation output based on any identifier that directs to a publication. The idea is to gather information using different freely available APIs.

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
- Retrieval of information via metapub (in the current stable version, the part of the code that is retrieving information from metapub is commented out)
- Retrieval of information via Scholarly
- Normalisation of Scholarly with two different output formats (depending on what information is given)

## TO DO:
- Combination of multiple outputs. Workflow I want: First try metapub. If all necessary information is retrieved, normalise output, done. Otherwise: Look for missing information via Scholarly.
- Proper proxy use for Scholarly. I already get blocked while testing. If we want to use Scholarly in big batches, this might become a problem. But the developers have implemented the option to use proxies. Unfortunately, right now, this returns a lot of errors and does not want to work (yet).
- Implement a proper output format for book citations
