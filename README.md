# :oncoming_bus: Downloader for the contents of the Omnibusarchiv.de omnibus database :bus:
I wanted to create a local copy of the contents of the omnibus database from omnibusarchiv.de since the site was not being actively cared for. I had asked the webmaster and he replied back that he did let go of that project. In order to preserve that information for myself – I do not intend to distribute or provide the contents of that database – I started to hack together a script which would do the work for me. This is the repository for that script.

## About me
Hi, I am Chris :wave:, I am by no means a developer but I know my way around some of the basics and put together the following script.

## Warning :heavy_exclamation_mark:
This code is probably awful both in terms of its structure and also my 'coding style'. I did not set out to write the perfect code, I was just looking for something that did the work it was supposed to do!

Although the omnibusarchiv.de website provides that database publicly, I urge you to be cautious with the content provided as some portions of it, especially the images, may very well be copyrighted!

## Noteworthy details

I initially set out to working with Scrapy as it made sense to me to use something that is being widelay used for scraping and downloading data. The websites code is very old, does not use any CSS and therefore I had to fall back to using `xpath` instead of css selectors.
As I had trouble getting the details of `xpath` working in conjunction with Scrapy and after some tinkering decided to go ahead with coding everything by myself.
I ended up still using the `Selector` sub-module from `scrapy` hence the details for the virtual environment I set up:

```
python -m venv /path/to/my/new/virtual/environment
source venv/bin/activate
pip install scrapy
```

I have tried to document the code a bit inline so I will not provide any additional documentation here.

When the script is finished with parsing all the pages – yes, it supports pagination and you could even configure the pagination size – it will fail when reaching the final entry. I did not care to code an exception for that case so just be aware that it is not exiting gracefully.

That error was

```
Traceback (most recent call last):
  File "main.py", line 93, in <module>
    id = parse_qs(parsed_url.query)['Id'][0]
KeyError: 'Id'
```
