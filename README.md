<h1 align="center">
  <img src="static/jir_thief-banner.png" alt="jir-thief" width="400px"></a>
  <br>
</h1>
<p align="center">
<a href="https://twitter.com/antman1p"><img src="https://img.shields.io/twitter/follow/antman1p.svg?logo=twitter"></a>
</p>

# Jir-thief
This Module will connect to Jira's API using an access token, export to a word .doc, and download the Jira issues
that the target has access to. It allows you to use a dictionary/keyword search file to search all files in the target
Jira for potentially sensitive data. It will output exfiltrated DOCs to the ./loot directory
## Dependencies
`pip install requests`
## Warning!!!  
Using the provided keyword list will produce a MASS of results, take a LONG time to search and download, and will send a LOT of API requests.  You might consider starting with a smaller list.
## Usage
```
python3 jir_thief.py [-h] -j <TARGET URL> -u <Target Username> -p <API ACCESS TOKEN> -d <DICTIONARY FILE PATH> [-a] "<UA STRING>"


arguments:
	-j <TARGET JIRA URL>, --url <TARGET JIRA URL>
		The URL of target Jira account
	-u <TARGET JIRA ACCOUNT USERNAME>, --user <TARGET USERNAME>
		The username of target Jira account
	-p <TARGET JIRA ACCOUNT API ACCESS TOKEN>, --accesstoken <TARGET JIRA ACCOUNT API ACCESS TOKEN>
		The API Access Token of target Jira account
	-d <DICTIONARY FILE PATH>, --dict <DICTIONARY FILE PATH>
		Path to the dictionary file.
		You can use the provided dictionary, per example: "-d ./dictionaries/secrets-keywords.txt"

optional arguments:
	-a "<DESIRED UA STRING>", --user-agent "<DESIRED UA STRING>"
		The User-Agent string you wish to send in the http request.
		You can use the latest chrome for MacOS for example: -a "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
		Default is "python-requests/2.25.1"

	-h, --help
		show this help message and exit
```
## TODO
- Threading
- Logging
- Map keyword searches to downloaded files
