from lxml import etree
from xmldiff import main, formatting

diff = main.diff_files('19.xml', '18.xml')
print(diff)
