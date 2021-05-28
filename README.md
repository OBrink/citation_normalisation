# Dear Maria, I am sorry that I bothered you during your time off. This is not important and can wait. I had misunderstood you on Wednesday and had not looked in your calendar. Do not worry about this nonsense here until the 25th. Have a nice time and enjoy your holiday!

# Update 21/05/2021: Maybe let me try to do it via the Web of Science API on Tuesday and let's then meet at Wednesday. I think I have wasted too much time on trying to make it work with Scholarly as Google Scholar tries to block automated scraping. First, we need to use proxies to keep changing our IP, but that works. The main problem is that Google Scholar uses CAPTCHAs. This will make it impossible to process big batches of data.

# citation_normalisation
The goal of this repository is to create a tool that creates a normalised citation output based on any identifier that directs to a publication. The idea is to gather information using different freely available APIs.

# Usage:

```
import citation_normalisation as cn

# These exemplary results are just based on scholarly requests.
# Metapub also works by now but only with a DOI.

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
- Retrieval of information via metapub
- if that does not work: Retrieval of information via Scholarly
- Normalisation of Scholarly with two different output formats (depending on what information is given)
- Using TOR for Scholarly to keep changing identity to avoid getting blocked

## TO DO:
- Get around Google Scholar CAPTCHAS? --> This might not be trivial. 
- Replace scholarly with WOS API
- Implement a proper output format for book citations
- I am not really happy with some of the Metapub output (eg. journal name "J Cheminform")
