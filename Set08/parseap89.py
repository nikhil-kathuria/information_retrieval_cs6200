import re
from glob import glob

def parsedocs():
    # Define local variables
    doclist = []
    intext = False
    interimline = ""
    keymap = {}
    # Read all the files in glob
    # add /ap' + '*'
    for filename in glob('../Set01/AP_DATA/ap89_collection/ap' + '*'):
        openfile = open(filename)
        # Read each line from the input file
        for line in openfile:
            # Strip new line char and spaces
            line = line.strip()
            # Append the line of text
            if intext:
                if not re.match('</TEXT>', line):
                    interimline = interimline + " " + line
            # Check for the Docno closing tag
            if re.search('</DOCNO>', line):
                # Extract the docno out of document
                docno = (line.split('</DOCNO>')[0]).split('<DOCNO>')[1].strip()
                doclist.append(docno)
                # Flush the docno value and interimline to hash table
                text = interimline.strip()
                keymap[docno] = interimline.strip()

                # Set interimline to empty string
                interimline = ""
            # Check for start text tag
            elif re.match('<TEXT>', line):
                intext = True
            elif re.match('</TEXT>', line):
                intext = False
            elif re.match('</DOC>', line):
                # Flush the docno value and interimline to hash table
                text = interimline.strip()
                keymap[docno] = interimline.strip()
        print filename

    return keymap
if __name__ == '__main__':
    parsedocs()