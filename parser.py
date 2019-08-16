import requests
from bs4 import BeautifulSoup, NavigableString
import json

url = "https://www.nyu.edu/about/policies-guidelines-compliance/policies-and-guidelines/data-and-system-security-measures.html"

def main():

    res = requests.get(url)
    html = res.text

    parser = BeautifulSoup(html, 'html.parser')

    # Print children for each child of parser.head
    # print([tag.contents for tag in parser.head.children if tag.name is not None])

    # locating the list associated to the title
    #print_tree(get_measures(parser, "D. Data Handling Security Measures").parent.ol)
    ol_data = get_measures(parser, "D. Data Handling Security Measures").parent.ol
    print(json.dumps(ol_to_list(ol_data), indent=4))

    pass

def get_measures(root, title, name="h2"):
    return root.find(lambda tag : tag.string == title and tag.name == name)

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
                        "title": alphanum_only(li.b.string).strip(),
                        "value": ol_to_list(li.ol)
                    }
                    # unstructured descriptions make parsing ambiguous, so treat them as part of the title;
                    # -none of them are meaningful at the moment, as they are all followed by more descriptive lists
                    unstructured_description = "".join([string for string in li.contents if isinstance(string, NavigableString)])
                    item["title"] += unstructured_description

                elif (has_title):
                    non_title_text = ""
                    if (not has_sublist):
                        non_title_text += "".join([(tag.string if tag.string else str(tag)) for tag in li.children if tag.name != "b"])
                        non_title_text = alphanum_only(non_title_text).strip()
                    item = {
                        "title": alphanum_only(li.b.string).strip(),
                        "value": non_title_text
                    }

                elif (has_sublist):
                    item = ol_to_list(li.ol)

                else:
                    item = li.get_text()

                this_list.append(item)

        return this_list

def print_tree(root, depth=0):
    # When calling on child, if child contains an ol, return child as list
    # What's left is to
    if (root is None):
        pass
    else:
        print(" " * depth, "|", root.name)

        for li in root.children:
            if (li.name is not None):
                print_tree(li, depth + 1)
            pass

if __name__ == "__main__":
    main()
    pass