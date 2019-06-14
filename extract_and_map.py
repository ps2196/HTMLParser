import HTMLParser
import tests.car

p = HTMLParser.HTMLParser(file_name='tests/cars.html', config_html='tests/extract_and_map_cfg.html')
filtered_elements = p.get_filtered_elements()
col = p.deserialize_elements(filtered_elements)

print("FILTERED ELEMENTS:\n\n")
for e in filtered_elements:
    print(e)

print('Deserailized objects:')
for i in col:
    print(i)