import errno
import json
import os
import requests
from scrapy import Selector
from urllib.parse import parse_qs
from urllib.parse import urlparse
import urllib.request

# Function to create an output file as a dict
# c = content to write, f = path + filename to write to
def create_outputfile(c, f):
    if not os.path.exists(os.path.dirname(f)):
        try:
            os.makedirs(os.path.dirname(f))
        except OSError as oserror:
            if oserror.errno != errno.EEXIST:
                raise
    with open(f, 'a') as convert_file:
        convert_file.write(c)

# Output directory path
OUTPUT_DIR = '/path/to/your/working/folder/omnibusarchiv_downloader/'

# Max Range as per omnibusarchiv.de
MAX_RANGE = 3368

# Standard pagination size as per omnibusarchiv.de
ITEMS_PER_PAGE = 14

# Starting pagination at 0
current_slice = 0

# Counting total
total_count = 0

while current_slice <= MAX_RANGE:

    # Building URL for current slice / page
    current_page_url = "http://www.omnibusarchiv.de/cgi-bin/baseportal.pl?htx=/Busse/Busse_Jahr&localparams=1&range={},{}".format(current_slice, ITEMS_PER_PAGE)

    # Printing current page URL
    print("Accessing page {}".format(current_page_url))

    # Requesting DOM of current page
    print("Requesting DOM of page {}".format(current_slice))
    r_detail = requests.get(current_page_url)
    response = Selector(text=r_detail.text)

    # Re-Init current_bus for current page
    current_bus = 1

    # Current slice download path for images
    current_slice_image_path = 'images_slice_{}'.format(1 if (current_slice == 0) else int((current_slice / ITEMS_PER_PAGE))+1)

    path = os.path.join(OUTPUT_DIR, current_slice_image_path)

    # Create current image slice directory
    try:
        os.makedirs(path, exist_ok=True)
        print('Directory {} created successfully'.format(current_slice_image_path))
    except OSError as error:
        print('Directory {} cannot be created'.format(current_slice_image_path))

    # Starting here, we now have the first ITEMS_PER_PAGE number of buses and need to parse them
    for current_bus in range(1, ITEMS_PER_PAGE + 1):

        # Increase total count
        total_count += 1

        current_xpath = "//html//body//center//table//tr//td[2]//table[4]//tr//td[2]//table//tr//td//table//tr[" + str(
            current_bus + 1) + "]"

        bus_fragment = response.xpath(current_xpath)
        print("Overall #{}: slice {}, bus {} of {}".format(total_count, current_slice, current_bus, ITEMS_PER_PAGE))

        year_selector = bus_fragment.xpath('td//font//font//text()')
        year = year_selector.get()

        bustype_selector = bus_fragment.xpath('td[2]//font//font//text()')
        bustype = bustype_selector.get()

        detail_selector = bus_fragment.xpath('td[3]//font//font//a//@href')
        detail_url = detail_selector.get()

        image_selector = bus_fragment.xpath('td[3]//font//font//a//img//@src')
        bus_image = image_selector.get()

        manufacturer_selector = bus_fragment.xpath('td[4]//font//font//text()')
        manufacturer = manufacturer_selector.get()

        parsed_url = urlparse(detail_url)
        id = parse_qs(parsed_url.query)['Id'][0]

        # Base bus objects are parsed, now on to the detail page parsing
        r_detail = requests.get(detail_url)
        detail_response = Selector(text=r_detail.text)

        details = detail_response.xpath('//html//body//center//table//tr//td[2]//table[3]//tr//td[2]//table//tr//td//table')

        archivenumber_selector = details.xpath('tr[2]//td[2]//font//font//text()')
        archivenumber = archivenumber_selector.get()

        country_selector = details.xpath('tr[7]//td[2]//font//font//text()')
        country = country_selector.get()

        info_selector = details.xpath('tr[8]//td[2]//font//font//text()')
        info = info_selector.getall()

        # Download current bus image, extract filename and download it when it exists
        if bus_image is None or len(bus_image) == 0:
            image_filename = '(None)'
        else:
            bus_image = bus_image.replace('\\', '/')
            image_filename = bus_image.split("/")[-1]

            # Adding information about user agent
            opener = urllib.request.build_opener()

            # Adding referer
            opener.addheaders = [('Referer', detail_url)]
            urllib.request.install_opener(opener)

            # Get image
            urllib.request.urlretrieve(bus_image, current_slice_image_path + '/' + image_filename)

        # Creating temporary dictionary of current bus
        temp = {
            'id': int(id),
            'year': int(year),
            'manufacturer': manufacturer,
            'bus_type': bustype,
            'image': current_slice_image_path + '/' + image_filename,
            'archive_number': archivenumber,
            'country': country,
            'info': info,
            'source_url': detail_url,
        }

        # Convert dictionary to JSON object
        temp = json.dumps(temp)

        # Appending JSON object to file
        create_outputfile(temp, OUTPUT_DIR + 'output_downloader.json')

        # Appending comma and newline to delimit between bus objects
        create_outputfile(',\n', OUTPUT_DIR + 'output_downloader.json')

    # End of FOR LOOP

    # Increase slice size by ITEMS_PER_PAGE to parse next page in while loop
    current_slice += ITEMS_PER_PAGE

# END OF WHILE LOOP
