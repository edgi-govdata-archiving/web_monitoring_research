 [![Code of Conduct](https://img.shields.io/badge/%E2%9D%A4-code%20of%20conduct-blue.svg?style=flat)](https://github.com/edgi-govdata-archiving/overview/blob/master/CONDUCT.md)

# Visualizing Changes to US Federal Environmental Agency Websites, 2016-2020
The data and scripts stored in this repo support a paper accepted at _PLOS One_. A pre-print version is available from SocArxiv: https://osf.io/preprints/socarxiv/6vsjc/

From the abstract:
Websites have become the primary means by which the US federal government communicates about its operations and presents information for public consumption, but the alteration or even wholesale removal of critical information from those sites is often entirely legal and done without the public’s awareness. Relative to paper records, websites enable governments to shape public understanding in quick, scalable, and permissible ways. At the same time, website access and content changes leave digital traces that can be tracked by civil society in order to hold governments to account. During the Trump administration, website changes indicative of climate change denial made evident the need for civil society organizations to develop new tools for tracking online government information sources. We in the Environmental Data & Governance Initiative (EDGI) prototyped how five data visualization techniques can be used to document and analyze changes to government websites. As an illustration, we examine a large sample of websites of US federal environmental agencies between 2016 and 2020. We show how: 1) the use of the term “climate change” decreased by an estimated 38%; 2) access to as much as 20% of the Environmental Protection Agency’s website was removed; 3) changes were made more to Cabinet agencies’ websites and to highly visible pages. In formulating ways to visualize and assess the alteration of websites, our study lays important groundwork for both systematically tracking changes and holding officials more accountable for their digital practices. Our techniques enable researchers and watchdog groups alike to operate at the scale necessary to understand the breadth of impact an administration can have on the online face of government. 

# Default branch - 'main'
The 'master' branch is no longer the repo's primary branch in line with EDGI's policy decided here: https://github.com/edgi-govdata-archiving/overview/issues/241

> If someone has a local clone, they can update their locals like this:
```
$ git checkout master
$ git branch -m master main
$ git fetch
$ git branch --unset-upstream
$ git branch -u origin/main
$ git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
```
> The above steps accomplish:
> - Go to the master branch
> - Rename master to main locally
> - Get the latest commits from the server
> - Remove the link to origin/master
> - Add a link to origin/main
> - Update the default branch to be origin/main

(From @jywarren at Public Lab: https://github.com/publiclab/plots2/issues/8077)

---

## License & Copyright

Copyright (C) <year> Environmental Data and Governance Initiative (EDGI)
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.0.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

See the [`LICENSE`](/LICENSE) file for details.