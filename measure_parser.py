from datetime import datetime

import requests
import json
import xlsxwriter
from bs4 import BeautifulSoup, NavigableString

url = "https://www.nyu.edu/about/policies-guidelines-compliance/policies-and-guidelines/data-and-system-security-measures.html"

title = "title"
measures = "measures"


def main():

    res = requests.get(url)
    html = res.text


    timestamp_raw = str(datetime.now()).replace(" ", "_")
    timestamp = timestamp_raw[:timestamp_raw.find(".")]

    workbook = xlsxwriter.Workbook("measure_workbook_" + timestamp + ".xlsx")

    measure_types = [
        "A. Basic System Security Measures",
        "B. Intermediate System Security Measures",
        "C. Advanced System Security Measures",
        "D. Data Handling Security Measures",
    ]

    parser = BeautifulSoup(html, "html.parser")

    for type in measure_types:
        excel_write_measures(workbook, type.split(" ")[1], parser, type)

    workbook.close()

    pass


'''
The method below arbitrarily takes the highest level groups of measures and creates
-an excel sheet such that each column represents a flattened list of all measures within that group

Using one of the main measure types "A. Basic System Security Measures", which has a group
- "password protection" (which contain measures), a column is created with
- "password protection" as the header and with all measures under it

Again, displaying the objects in such a format is arbitrary, and
- if the format requires change, the edit this function or create a similar one so it
- contains a for-loop that iterates through the measure groups differently

Use the @pretty_json function to print json @os_to_list function for debugging
- e.g.:
- print(pretty_json(ol_to_list(BeautifulSoup(requests.get(url).text, "html.parser").find(lambda tag : tag.string == "A. Basic System Security Measures" ).parent.ol)))
'''

# @measure_type: The highest level of measures on the website
def excel_write_measures(workbook, sheet, parser, measure_type, measure_tag="h2"):

    if (len(sheet) > 31):
        sheet = sheet[:28]
        sheet += "..."

    measures_sheet = workbook.add_worksheet(sheet)

    subtype_filter = lambda tag : tag.string == measure_type and tag.name == measure_tag
    measure_subtypes = parser.find(subtype_filter).parent.ol

    subtypes_as_json = ol_to_list(measure_subtypes)

    # Every subtype is a column mapped with column name == subtype name
    for (col, subtype) in enumerate(subtypes_as_json):

        measures_sheet.write(0, col, subtype[title])
        all_measures_for_subtype = get_measures_from_json(subtype)

        for (row, measure) in enumerate(all_measures_for_subtype):
            measures_sheet.write(row + 1, col, measure)

    pass



# assumption is every child in list_tag is either:
# <li> <b/><ol/> text </li>, in which case, turn the pair <b/><ol/> into an entry,
# or <li> <ol/> </li>, in which case, turn the ol into a list,
# or <li> text </li>, in which case, return the text
def ol_to_list(root):
    # When calling on child.ol (li.ol), return { title: li.b, value: (list from li.ol || string) }
    # What's left is to append that object to list and return list
    if root is not None:
        this_list = []

        for li in root.children:
            if (li.name is not None):

                item = None

                has_title = li.b is not None
                has_sublist = li.ol is not None

                alphanum_only = lambda string : "".join([c for c in string if c.isalnum() or c.isspace()])

                if (has_title and has_sublist):
                    
                    item = {
                        title: alphanum_only(li.b.string).strip(),
                        measures: ol_to_list(li.ol)
                    }
                    # unstructured descriptions make parsing ambiguous; in this case, treating them as part of the title;
                    unstructured_description = "".join([string for string in li.contents if isinstance(string, NavigableString)])
                    item[title] += unstructured_description

                elif (has_title):
                    non_title_text = ""
                    if (not has_sublist):
                        non_title_text += "".join([(tag.string if tag.string else str(tag)) for tag in li.children if tag.name != "b"])
                        non_title_text = alphanum_only(non_title_text).strip()
                    item = {
                        title: alphanum_only(li.b.string).strip(),
                        measures: non_title_text
                    }

                elif (has_sublist):
                    item = ol_to_list(li.ol)

                else:
                    item = li.get_text()

                this_list.append(item)

        return this_list



'''
When traversing the structure, the measures field can be in one of three forms:
measures: [{...}]
measures: ["..."]
measures: "..."
'''

# @input: dom element in range of @parse_measures
# @output flat list of all measures that are sub-elements of that element
def get_measures_from_json(root):

    # When calling on children of root, return collection of all measures of children
    # What's left is to append measures of root to measures of child

    if (isinstance(root, dict)):
        return get_measures_from_json(root[measures])
    elif (isinstance(root, list)):
        list_measures = []
        for child in root:
            list_measures.extend(get_measures_from_json(child))
        return list_measures
    else:
        return [root]

def pretty_json(dict):
    return json.dumps(dict, indent=4)

if __name__ == "__main__":
    main()
    pass