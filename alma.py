### Import Statements ###
import urllib.request
import re
import xml.etree.ElementTree as ET
import http.client
import urllib.parse
import time
from datetime import datetime




### Variables ###
api_base = "https://api-eu.hosted.exlibrisgroup.com"
api_key = input("Enter an API key: ")




### Headers ###
headers = {}
authorization_header = "apikey " + api_key
headers["Authorization"] = authorization_header




### HTTP Method Functions ###
def getUrl(url):
    req = urllib.request.Request(url=url, data=None, headers=headers, method='GET')
    try:
        get = urllib.request.urlopen(req)
        text = get.read()
        text_string = text.decode('utf8')
        return text_string
    except Exception as e:
        print(str(e))
        error_text = e.read()
        error_text_string = error_text.decode('utf8')
        return error_text_string 

def putUrl(url, xml_in_bytes):
    headers['Content-Type'] = 'application/xml'
    req = urllib.request.Request(url=url, data=xml_in_bytes, headers=headers, method='PUT')
    try:
        put = urllib.request.urlopen(req)
        print(put.status)
        print(put.reason)
    except Exception as e:
        print(str(e))
        print(e.read())

def postUrl(url, xml_in_bytes):
    headers['Content-Type'] = 'application/xml'
    req = urllib.request.Request(url=url, data=xml_in_bytes, headers=headers, method='POST')
    try:
        post = urllib.request.urlopen(req)
        print(str(post.status) + " " + post.reason)
    except Exception as e:
        print(str(e))
        print(e.read())

def deleteUrl(url):
    req = urllib.request.Request(url=url, data=None, headers=headers, method='DELETE')
    try:
        delete = urllib.request.urlopen(req)
        print(str(delete.status) + " " + delete.reason)
    except Exception as e:
        print(str(e))
        print(e.read())




### Other Internal Functions ###
def getRowset(text_string):
    root = ET.fromstring(text_string)
    res = root.find('QueryResult')
    res2 = res.find('ResultXml')
    rowset = res2.find('{urn:schemas-microsoft-com:xml-analysis:rowset}rowset')
    rowset_string = ET.tostring(rowset, encoding="unicode")
    return rowset_string

def getToken(text_string):
    text_string = text_string.replace("\n", "")
    text_string = text_string.replace("\r", "")
    pattern = re.search(r'<ResumptionToken>(.*?)</ResumptionToken>', text_string)
    token = pattern.group(1)
    token = "token=" + token
    return token

def isFinished(text_string):
    pattern = re.search(r'<IsFinished>(.*?)</IsFinished>', text_string)
    finished = pattern.group(1)
    if finished == "true":
        return True
    else:
        return False

def sendUpdate(setid, membersxml):
    api_query = "/almaws/v1/conf/sets/" + setid + "?op=add_members"
    url = api_base + api_query
    postUrl(url, membersxml):

### Acquisitions functions ###
def get_vendor(code):
    code = urllib.parse.quote(code)
    api_query = "/almaws/v1/acq/vendors/" + code
    url = api_base + api_query
    result = getUrl(url)
    return result
   
### Resource related functions ###
def get_marc_subfields(field, subfield_code):
    subfields = []
    for subfield in field:
        if subfield.attrib['code'] == subfield_code:
            subfields.append(subfield.text)
    return subfields

def get_marc_fields(bib, tag, **inds):
    try:
        ind1 = inds['ind1']
    except:
        ind1 = ''
    try:
        ind2 = inds['ind2']
    except:
        ind2 = ''
    root = ET.fromstring(bib)
    record = root.find('record')
    match_list = []
    if tag in ['LDR', 'leader']:
        leader = record.find('leader')
        match_list.append(leader)
        return leader
    for el in record:
        if el.tag not in ['controlfield', 'datafield']:
            continue
        match = False
        if el.attrib['tag'] == tag:
            match = True
            if len(ind1) > 0:
                if el.attrib['ind1'] != ind1:
                    match = False
            if len(ind2) > 0:
                if el.attrib['ind2'] != ind2:
                    match = False
        if match:
            match_list.append(el)
    return match_list       

def get_single_bib(mms, *args):
    if len(args) > 0:
        expand = "?expand=" + args[0]
    else:
        expand = ""
    api_query = "/almaws/v1/bibs/" + mms + expand
    url = api_base + api_query
    result = getUrl(url)
    return result

def update_bib(mms_id, xml_in_bytes): ## Returns nothing, but updates bib
    api_query = "/almaws/v1/bibs/" + mms_id
    url = api_base + api_query
    putUrl(url, xml_in_bytes)

def get_holdings_list(mms_id):
    errorfile = open('get_holdings_list.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/bibs/" + mms_id + "/holdings"
    url = api_base + api_query
    result = getUrl(url)
    return result

def get_holding(mms_id, hol_id):
    errorfile = open('get_holding.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/bibs/" + mms_id + "/holdings/" + hol_id
    url = api_base + api_query
    print(url)
    result = getUrl(url)
    return result

def update_holding(mms_id, hol_id, xml_in_bytes): ## Returns nothing, but updates bib
    api_query = "/almaws/v1/bibs/" + mms_id + "/holdings/" + hol_id
    url = api_base + api_query
    putUrl(url)

def create_holding(mms_id, xml_in_bytes): ## Returns nothing, but creates holding
    api_query = "/almaws/v1/bibs/" + mms_id + "/holdings/"
    url = api_base + api_query
    postUrl(url, xml_in_bytes)

def get_portfolio_list(mmsid): ## Returns xml string of the portfolios for that bib
    errorfile = open('get_portfolio_list.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/bibs/" + mmsid + "/portfolios"
    url = api_base + api_query
    print(url)
    result = getUrl(url)
    return result

def get_portfolio(mmsid, pid):
    errorfile = open('get_portfolio.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/bibs/" + mmsid + "/portfolios/" + pid
    url = api_base + api_query
    print(url)
    result = getUrl(url)
    return result

def update_portfolio(bib_id, pid, xml_in_bytes): ## Returns nothing, but updates portfolio
    api_query = "/almaws/v1/bibs/" + bib_id + "/portfolios/" + pid
    url = api_base + api_query
    putUrl(url, xml_in_bytes)

def create_portfolio(bib_id, xml_in_bytes): ## Returns nothing, but creates portfolio
    api_query = "/almaws/v1/bibs/" + bib_id + "/portfolios/"
    url = api_base + api_query
    postUrl(url, xml_in_bytes)

def get_items_list(mms_id, hol_id):
    errorfile = open('get_items_list.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/bibs/" + mms_id + "/holdings/" + hol_id + "/items"
    url = api_base + api_query
    print(url)
    result = getUrl(url)
    return result

def get_item(bib_id, hol_id, item_id):
    errorfile = open('get_item.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/bibs/" + bib_id + "/holdings/" + hol_id + "/items/" + item_id
    url = api_base + api_query
    print(url)
    result = getUrl(url)
    return result

def get_item_label(barcode):
    errorfile = open('get_item_label.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/items?view=label&item_barcode=" + barcode
    url = api_base + api_query
    print(url)
    result = getUrl(url)
    return result

def update_item(bib_id, hol_id, item_id, xml_in_bytes): ## Returns nothing, but updates item
    api_query = "/almaws/v1/bibs/" + bib_id + "/holdings/" + hol_id + "/items/" + item_id
    url = api_base + api_query
    putUrl(url, xml_in_bytes)

def delete_item(bib_id, hol_id, item_id, override): ## Returns nothing, but deletes item
    api_query = "/almaws/v1/bibs/" + bib_id + "/holdings/" + hol_id + "/items/" + item_id + "?override=" + override
    url = api_base + api_query
    deleteUrl(url)

def create_item(mms_id, holding_id, xml_in_bytes): ## Returns nothing, but creates item
    api_query = "/almaws/v1/bibs/" + mms_id + "/holdings/" + holding_id + "/items"
    url = api_base + api_query
    postUrl(url, xml_in_bytes)




### Admin related functions
def get_set_members(set_id):
    errorfile = open('get_set_members.error', 'a+', encoding='utf8', errors='ignore')
    offset = 0
    limit = 100
    member_list = []
    running = True
    while running:
        api_query = "/almaws/v1/conf/sets/" + set_id + "/members?limit=" + str(limit) + "&offset=" + str(offset)
        url = api_base + api_query
        print(url)
        result = getUrl(url)
        count = 0
        root = ET.fromstring(result)
        for child in root:
            member_list.append(child)
            count = count + 1
        if count == limit:
            offset = offset + limit
        else:
            running = False
    return_string = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><members total_record_count="' + str(offset + count) + '">'
    for member in member_list:
        return_string = return_string + ET.tostring(member, encoding='unicode')
    return_string = return_string + "</members>"
    return return_string


def get_set_member_id_list(set_id):
    # Helper function starts here #
    def get_set_member_id_list_helper(set_id, offset):
        limit = 100
        running = True
        while running:
            api_query = "/almaws/v1/conf/sets/" + set_id + "/members?limit=" + str(limit) + "&offset=" + str(offset)
            url = api_base + api_query
            print(url)
            result = getUrl(url)
            count = 0
            root = ET.fromstring(result)
            members = root.findall('member')
            for member in members:
                mid = member.find('id').text
                if mid not in set_members_id_list:
                    set_members_id_list.append(mid)
                count = count + 1
            if count == limit:
                offset = offset + limit
            else:
                running = False
    # Helper function ends here #
    set_members_id_list = []
    offset = 0
    running = True
    while running:
        try:
            get_set_member_id_list_helper(set_id, offset)
            running = False
        except:
            offset = len(set_members_id_list)
    return set_members_id_list

def update_set(setid, newmembers_list): ## Returns nothing but updates a set. Make sure set is of same type as input ID.
    count = 0
    membersxml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><set><members>'
    for newmember in newmembers_list:
        membersxml = membersxml + '<member link="string"><id>' + newmember + '</id></member>'
        count = count + 1
        if count % 100 == 0:
            membersxml = membersxml + '</members></set>'
            sendUpdate(setid, membersxml)
            membersxml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><set><members>'
    if count % 100 != 0:
        membersxml = membersxml + '</members></set>'
        sendUpdate(setid, membersxml)

def get_all_rs_partners():
    api_query = "/almaws/v1/partners?limit="
    limit = "100"
    offset_string = "&offset="
    offset_value = 0
    running = True
    partners_string = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><partners>'
    while running:
        url = api_base + api_query + limit + offset_string + str(offset_value)
        print(url)
        text_string = getUrl(url)
        root = ET.fromstring(text_string)
        partner_list = root.findall('partner')
        for partner in partner_list:
            partners_string = partners_string + ET.tostring(partner, encoding="unicode") + "\n"
        offset_value = offset_value + len(partner_list)
        total_partners = int(root.attrib['total_record_count'])
        if total_partners <= offset_value:
            running = False
    partners_string = partners_string + "</partners>"
    outfile = open("partners.xml", "w", encoding="utf8", errors="ignore")
    outfile.write(partners_string)
    outfile.close()
    return partners_string

def update_rs_partner(partner_code, xml_in_bytes):
    api_query = "/almaws/v1/partners/" + partner_code
    url = api_base + api_query
    putUrl(url, xml_in_bytes)

def get_code_table(code_table):
    api_query = "/almaws/v1/conf/code-tables/" + code_table
    url = api_base + api_query
    print(url)
    result = getUrl(url)
    return result



### Acquistions related functions ###
def get_poline(pol_id):
    errorfile = open('get_poline.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/acq/po-lines/" + pol_id
    url = api_base + api_query
    print(url)
    try:
        result = getUrl(url)
    except:
        errorfile.write("No record found: " + pol_id + "\n")
        print("No record found: " + pol_id)
        result = ""
    return result

def update_poline(pol_id, xml_in_bytes):
    api_query = "/almaws/v1/acq/po-lines/" + pol_id
    url = api_base + api_query
    putUrl(url, xml_in_bytes)

def create_poline(xml_in_bytes):
    api_query = "/almaws/v1/acq/po-lines/"
    url = api_base + api_query
    req = urllib.request.Request(url=url, data=xml_in_bytes, headers={'Content-Type': 'application/xml'}, method='POST')
    postUrl(url, xml_in_bytes)




### User related functions
def get_user_list():
    errorfile = open('get_user_list.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/users?limit=100"
    offset = "&offset="
    user_list = []
    benchmark = -1
    while len(user_list) > benchmark:
        print(len(user_list))
        benchmark = len(user_list)
        count = str(len(user_list))
        url = api_base + api_query + offset + count
        print(url)
        result = getUrl(url)
        root = ET.fromstring(result)
        users = root.findall('user')
        for user in users:
            try:
                u = user.attrib['link']
                u = u.replace("https://api-eu.hosted.exlibrisgroup.com/almaws/v1/users/", "")
                if u not in user_list:
                    user_list.append(u)
            except:
                print(user.attrib)
    return user_list

def get_user_loans(user_id):
    # Note that it is limited to 100 loans. Would need to repeat queries 
    errorfile = open('get_user_loans.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/users/" + user_id + "/loans?limit=100"
    url = api_base + api_query
    print(url)
    result = getUrl(url)
    return result

def update_item_loan(user_id, loan_id, item_loan_xml):
    api_query = "/almaws/v1/users/" + user_id + "/loans/" + loan_id
    url = api_base + api_query
    new_item_loan = ET.tostring(item_loan_xml)
    putUrl(url, new_item_loan)

def change_loan_due_dates(user_id, due_date):
    ## Give due_Date in the format: 2021-03-27T23:59:00Z
    print("\n" + user_id + "\n")
    errorfile = open('change_loan_due_dates.error', 'a+', encoding='utf8', errors='ignore')
    user_loans = get_user_loans(user_id)
    root = ET.fromstring(user_loans)
    for child in root:
        item_loan = child
        for child in item_loan:
            if child.tag == "loan_id":
                loan_id = child.text
                print(loan_id)
            elif child.tag == "due_date":
                child.text = due_date
        new_item_loan = ET.tostring(item_loan)
        #print(ET.tostring(item_loan, 'utf8'))
        api_query = "/almaws/v1/users/" + user_id + "/loans/" + loan_id
        url = api_base + api_query
        putUrl(url, new_item_loan)

def get_user_fines(user_id):
    errorfile = open('get_user_fines.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/users/" + user_id + "/fees"
    url = api_base + api_query
    print(url)
    result = getUrl(url)
    return result

def get_user_requests(user_id):
    errorfile = open('get_user_requests.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/users/" + user_id + "/requests"
    url = api_base + api_query
    print(url)
    result = getUrl(url)
    return result

def get_user_request(user_id, request_id):
    errorfile = open('get_user_requests.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/users/" + user_id + "/requests/" + request_id
    url = api_base + api_query
    print(url)
    result = getUrl(url)
    return result 

def get_user_record(user_id):
    errorfile = open('get_user_record.error', 'a+', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/users/" + user_id
    url = api_base + api_query
    print(url)
    result = getUrl(url)
    return result

def update_user(user_id, xml_in_bytes):
    api_query = "/almaws/v1/users/" + user_id
    url = api_base + api_query
    putUrl(url, xml_in_bytes)

def delete_user(user_id, latest_expiry_date):
    benchmark_date = datetime.strptime(latest_expiry_date, '%Y%m%d')
    logfile = open('delete_user.log', 'a+', encoding='utf8', errors='ignore')
    loans = get_user_loans(user_id)
    root = ET.fromstring(loans)
    loans = root.attrib['total_record_count']
    fines = get_user_fines(user_id)
    root = ET.fromstring(fines)
    fines = root.attrib['total_record_count']
    user = get_user_record(user_id)
    root = ET.fromstring(user)
    for child in root:
        if child.tag == "expiry_date":
            expiry_string = child.text
    expiry_date = datetime.strptime(expiry_string, '%Y-%m-%dZ')
    print(expiry_string)
    print(user_id + ":  " + loans + " loans, " + fines + " fines, expiry date: " + expiry_string)
    logfile.write(user_id + ":  " + loans + " loans, " + fines + " fines, expiry date: " + expiry_string + "\n")
    if loans == "0" and fines == "0":
        if expiry_date <= benchmark_date:
            print("Delete " + user_id)
            logfile.write("Delete " + user_id + "\n")
            api_query = "/almaws/v1/users/" + user_id
            url = api_base + api_query
            deleteUrl(url)

def delete_title_request(bib_id, req_id, reasonCode, notifyBoolean):
    ## The notifyBoolean should be a string - "true" or "false".
    ## The reasonCode can be selected from the list at: alma.get_code_table("RequestCancellationreasons")
    ## I tend to use "CannotBeFulfilled" as a default
    api_query = "/almaws/v1/bibs/" + bib_id + "/requests/" + req_id + "?reason=" + reasonCode + "&notify_user=" + notifyBoolean
    url = api_base + api_query
    deleteUrl(url)




### Analytics functions ###

def get_report(path): ## Returns nothing, but creates a "report.xml" file.
    ## path variable must begin "path="
    count = 1
    print(count)
    errorfile = open('get_report.error', 'a+', encoding='utf8', errors='ignore')
    tempfile1 = open('get_report.temp1', 'w', encoding='utf8', errors='ignore')
    tempfile2 = open('get_report.temp2', 'w', encoding='utf8', errors='ignore')
    api_query = "/almaws/v1/analytics/reports?"
    limit = "&limit=1000"
    url = api_base + api_query + path + limit
    resume = False
    print(url)
    try:
        text_string = getUrl(url)
        tempfile1.write(text_string)
        resume = not isFinished(text_string)
        if resume:
            token = getToken(text_string)
    except Exception as e:
        print(str(e))
        errorfile.write("Error getting: " + url + "\n")
    while resume:
        count = count + 1
        print(count)
        url = api_base + api_query + token
        print(url)
        try:
            text_string = getUrl(url)
            resume = not isFinished(text_string)
            print(resume)
            rowset = getRowset(text_string)
            tempfile2.write(rowset)
        except Exception as e:
            print(str(e))
            errorfile.write("Error getting: " + url + "\n")
            resume = False
    tempfile1.close()
    tempfile2.close()
    tempfile1 = open('get_report.temp1', 'r', encoding='utf8', errors='ignore')
    tempfile2 = open('get_report.temp2', 'r', encoding='utf8', errors='ignore')
    outfile = open('report.xml', 'w', encoding='utf8', errors='ignore')
    temp1 = tempfile1.read()
    temp1 = temp1.replace("\r", "")
    temp1 = temp1.replace("\n", "NEWLINEMARKER")
    pattern = re.match(r'^(.*?)(</rowset.*)', temp1)
    start = pattern.group(1)
    start = re.sub(r'<ResumptionToken>.*?</ResumptionToken>', '', start)
    start = re.sub(r'<IsFinished>.*?</IsFinished>', '', start)
    while " NEWLINEMARKER" in start:
        start = start.replace(" NEWLINEMARKER", "NEWLINEMARKER")
    while "NEWLINEMARKERNEWLINEMARKER" in start:
        start = start.replace("NEWLINEMARKERNEWLINEMARKER", "NEWLINEMARKER")
    end = pattern.group(2)
    start = start.replace("NEWLINEMARKER", "\n")
    end = end.replace("NEWLINEMARKER", "\n")
    outfile.write(start)
    for line in tempfile2:
        line = line.replace("\r", "")
        line = line.replace("<rowset>", "")
        line = line.replace("</rowset>", "")
        while " \n" in line:
            line = line.replace(" \n", "\n")
        line = re.sub(r'^\n', '', line)
        outfile.write(line)
    outfile.write(end)
    tempfile1.close()
    tempfile2.close()
    outfile.close()


### Functions for processing XML ###

def get_column_headings(root): ## Returns a dict of column headings and names
    urn = "{urn:schemas-microsoft-com:xml-analysis:rowset}"
    xsd = "{http://www.w3.org/2001/XMLSchema}"
    sawsql = "{urn:saw-sql}"
    element_list = root.iter(xsd + "element")
    column_dict = {}
    for element in element_list:
        column_dict[element.attrib["name"]] = element.attrib[sawsql + "columnHeading"]
    return column_dict

def get_rows(root): ## Returns a list of all the rows in a report
    row_list = root.iter("{urn:schemas-microsoft-com:xml-analysis:rowset}Row")
    return row_list

def get_column(col, row): ## Returns a specified column for a row
    column = row.find("{urn:schemas-microsoft-com:xml-analysis:rowset}" + col)
    try:
        column = column.text
    except:
        column = ""
    return column
