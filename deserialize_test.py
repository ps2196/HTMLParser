import HTMLParser
import tests.car

p = HTMLParser.HTMLParser(file_name='tests/cars.html', config_html='tests/map_config.html')
col = p.deserialize()
print('Deserailized objects:')
for i in col:
    print(i)