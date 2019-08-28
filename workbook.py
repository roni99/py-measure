import json
import xlsxwriter

from datetime import datetime

def main():

    timestamp_raw = str(datetime.now()).replace(" ", "_").replace(":", "-")
    timestamp = timestamp_raw[:timestamp_raw.find(".")]

    workbook = xlsxwriter.Workbook("output/measure_workbook_" + timestamp + ".xlsx")

    file_measures = open("measures.json", "r")
    measures = json.load(file_measures)
    file_measures.close()

    # print(json.dumps(get_measures_from_json(measures), indent=4)) # get all measures

    '''
    Edit the for-loop below to change the format of the resulting excel file
    
    As-is, the loop will create a sheet for every level of measure type (i.e.: Basic, Moderate, High, Data)
    - and for each sub-type within that measure type, a column represents a flattened list of measures
    - from that sub-type
    '''

    for measure_type in measures:

        current_sheet = measure_type["title"].split(" ")[1]
        worksheet = workbook.add_worksheet(current_sheet)

        for (col, subtype) in enumerate(measure_type["measures"]):

            worksheet.write(0, col, subtype["title"])
            all_subtype_measures = get_measures_from_json(subtype)

            for (row, measure) in enumerate(all_subtype_measures):
                worksheet.write(row + 1, col, measure)


    workbook.close()

    pass

'''
When traversing the structure, the measures field can be in one of three format
There are three forms because those forms each map to a format in the website

measures: [{...}]
measures: ["..."]
measures: "..."

(Critical) A measure that *is a* string is a real measure that is to eventually be compared against;
- a measure that *is a* list is only a data structure that contains real measures somewhere within it
'''

# @input: dom element in range of @parse_measures
# @output flat list of all measures that are sub-elements of that element
def get_measures_from_json(root):

    # When calling on children of root, return collection of all measures of children
    # What's left is to append measures of root to measures of child

    if (isinstance(root, dict)):
        return get_measures_from_json(root["measures"])
    elif (isinstance(root, list)):
        list_measures = []
        for child in root:
            list_measures.extend(get_measures_from_json(child))
        return list_measures
    else:
        return [root]

if __name__ == "__main__":
    main()
    pass