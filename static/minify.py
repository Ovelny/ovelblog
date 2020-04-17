# -*- coding: utf-8 -*-
import sys
import requests

try:
    css_file = sys.argv[1]
except:
    print("Missing input file")
    sys.exit()

# Grab the file contents
with open(css_file, 'r') as c:
    css = c.read()

# Pack it, ship it    
payload = {'input': css}
url = 'https://cssminifier.com/raw'
print("Requesting mini-me of {}. . .".format(c.name))
r = requests.post(url, payload)

# Write out minified version
minified = css_file.rstrip('.css')+'.min.css'
with open(minified, 'w') as m:
    m.write(r.text)

print("Minification complete. See {}".format(m.name))