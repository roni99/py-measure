import requests
from bs4 import BeautifulSoup
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

# assumption is every child in list_tag is either an li containing a b and an ol or an li containing a b
def ol_to_list(root):
    # When calling on child.ol (li.ol), return { title: li.b, value: (list || string) }
    # What's left is to append all to list and return
    if root is not None:
        this_list = []

        for li in root.children:
            if (li.name is not None):
                item = dict()

                has_title = li.b is not None

                item["title"] = li.b.string if has_title else str(len(this_list))

                has_sublist = li.ol is not None
                non_title_strings = ""
                if (not has_sublist):
                    non_title_strings += "".join([(tag.string if tag.string else str(tag)) for tag in li.children if tag.name != "b"])
                    non_title_strings = "".join([c for c in non_title_strings if c.isalnum() or c.isspace()])

                item["value"] = ol_to_list(li.ol) if has_sublist else non_title_strings
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