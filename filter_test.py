import HTMLParser
import tests.car

p = HTMLParser.HTMLParser(file_name='tests/cars2.html', config_html='tests/filter_config.html')
filtered_elements = p.get_filtered_elements()
print("FILTERED ELEMENTS:\n\n")
for e in filtered_elements:
    print(e)