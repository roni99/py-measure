import requests
import json
from bs4 import BeautifulSoup, NavigableString

url = "https://www.nyu.edu/about/policies-guidelines-compliance/policies-and-guidelines/data-and-system-security-measures.html"

title = "title"
measures = "measures"


def main():

    res = requests.get(url)
    html = res.text

    measure_types = [
        "A. Basic System Security Measures",
        "B. Intermediate System Security Measures",
        "C. Advanced System Security Measures",
        "D. Data Handling Security Measures",
    ]

    parser = BeautifulSoup(html, "html.parser")

    # all_measures is a list so the structure of the resulting json matches the structure of the website exactly
    all_measures = []

    # For every level of measures (basic, moderate, etc.) store all sub-measures as objects into the all_measures list
    for type in measure_types:
        filter_subtype = lambda tag: tag.string == type and tag.name == "h2"
        ol_subtypes = parser.find(filter_subtype).parent.ol
        json_subtypes = ol_to_list(ol_subtypes)
        all_measures.append({
            title: type,
            measures: json_subtypes
        })

    print(json.dumps(all_measures, indent=2))

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
                    # unstructured descriptions make parsing ambiguous; in this case, treating them as part of the title
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


if __name__ == "__main__":
    main()
    pass