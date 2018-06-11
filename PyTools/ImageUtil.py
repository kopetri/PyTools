#import flickrapi
import urllib.request
import json
import numpy as np
import cv2
import os
import PyTools.Viz as vis

"""
globals
"""
apiKey = 'fd8ef0d537bed445d7502e7d8a36b580'
secret = 'f1c9b30b3b24430a'
#flickr = flickrapi.FlickrAPI(api_key=apiKey, secret=secret, format='parsed-json')

'''
api_key = u'9df1fb7d63d5d63952a93814b46e04b9'
api_secret = u'ead6328a16f5a8ea'
'''


def generate_patches(output_dir, patch_size=(512, 512), step_size=32, number_of_images=500):
    patch_number = 0
    while True:
        image = random_image(min_size=(1024, 1024), max_size=(4000, 4000))
        for (x, y, window) in sliding_window(image, stepSize=step_size, windowSize=patch_size):
            # if the window does not meet our desired window size, ignore it
            if window.shape[0] != patch_size[0] or window.shape[1] != patch_size[1]:
                continue
            print("storing patch " + str(patch_number))
            cv2.imwrite(output_dir + '/' + str(patch_number) + '.jpg', window)
            patch_number = patch_number + 1
            if len(os.listdir(output_dir)) >= number_of_images:
                return


def save_images(keyword, output_dir, noi=10):
    photos = flickr.walk(text=keyword,
                         tag_mode='all',
                         tags=keyword,
                         extras='url_c',
                         sort="relevance",
                         per_page=100)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    i = 0
    for photo in photos:
        url = photo.get('url_c')
        if not (url is None):
            img = get_image(url)
            cv2.imwrite(os.path.join(output_dir, str(i) + '.jpg'), img)
            print('stored image ' + str(i))
            i = i + 1
            if i >= noi:
                return


def extract_patches(input_dir='images', output_dir='patches', winW=128, winH=128):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    patch = 0
    i = 0
    for file in os.listdir(input_dir):
        print("processing image " + str(i) + " out of " + str(len(os.listdir(input_dir))))
        i = i + 1
        image = cv2.imread(os.path.join(input_dir, file), cv2.IMREAD_COLOR)
        for (x, y, window) in sliding_window(image, stepSize=128, windowSize=(winW, winH)):
            # if the window does not meet our desired window size, ignore it
            if window.shape[0] != winH or window.shape[1] != winW:
                continue
            cv2.imwrite(os.path.join(output_dir, str(patch) + '.jpg'), window)
            patch = patch + 1


def add_background(foreground, background):
    # Read the images
    ret, alpha = cv2.threshold(foreground, 0, 255, cv2.THRESH_BINARY)

    # Convert uint8 to float
    foreground = foreground.astype(float)
    background = background.astype(float)

    # Normalize the alpha mask to keep intensity between 0 and 1
    alpha = alpha.astype(float) / 255
    foreground = foreground.astype(float) / 255
    background = background.astype(float) / 255

    # Multiply the foreground with the alpha matte
    foreground = cv2.multiply(alpha, foreground)

    # Multiply the background with ( 1 - alpha )
    background = cv2.multiply(1.0 - alpha, background)

    # Add the masked foreground and background.
    outImage = cv2.add(foreground, background)
    return outImage


def background(data_dir, background_dir):
    per_image_repetitions = 3
    for dir in os.listdir(data_dir):
        if os.path.isdir(os.path.join(data_dir, dir)):
            for file in os.listdir(os.path.join(data_dir, dir)):
                indices = np.random.randint(len(os.listdir(background_dir)),
                                            size=per_image_repetitions)
                for t in range(0, per_image_repetitions, 1):
                    fileNumber = indices[t]
                    background = cv2.imread(os.path.join(background_dir, str(fileNumber) + '.jpg'), cv2.IMREAD_COLOR)
                    foreground = cv2.imread(os.path.join(data_dir, dir, file), cv2.IMREAD_COLOR)
                    merged = add_background(foreground, background)
                    # cv2.imshow('merged', merged)
                    # cv2.waitKey(0)
                    merged = merged * 255
                    cv2.imwrite(os.path.join(data_dir, dir, file[:-4] + '-' + str(t) + '.jpg'), merged)


def get_image(url):
    """
    :param url: source url of image
    :return: image data as numpy array
    """
    return cv2.imdecode(np.asarray(bytearray(urllib.request.urlopen(url).read()), dtype="uint8"), cv2.IMREAD_COLOR)


def search_image_v2(text, count, output_dir):
    extras = 'url_sq,url_t,url_s,url_q,url_m,url_n,url_z,url_c,url_l,url_o'
    result = flickr.photos.search(text=text, per_page='100', extras=extras)
    photos = result['photos']['photo']
    n = 0
    for photo in photos:
        if n >= count:
            return
        url = ''
        if 'url_t' in photo:
            url = photo['url_t']
        if 'url_s' in photo:
            url = photo['url_s']
        if 'url_sq' in photo:
            url = photo['url_sq']
        if 'url_o' in photo:
            url = photo['url_o']
        if 'url_m' in photo:
            url = photo['url_m']
        if 'url_n' in photo:
            url = photo['url_n']
        if 'url_z' in photo:
            url = photo['url_z']
        if 'url_q' in photo:
            url = photo['url_q']
        if 'url_l' in photo:
            url = photo['url_l']
        if 'url_c' in photo:
            url = photo['url_c']
        if url:
            image = get_image(url)
            cv2.imwrite(os.path.join(output_dir, str(n) + '.jpg'), image)
            n = n + 1


def write_png_as_jpg(img_path):
    """
    :param img_path: path of image
    :return: None
    Writes the image as jpg image
    """
    cv2.imwrite(img_path.replace('.png', '.jpg'), cv2.imread(img_path, cv2.IMREAD_COLOR))


def random_image(resize=False, min_size=(512, 512), max_size=(1024, 1024)):
    """
    :param resize:
    :param min_size:
    :param max_size:
    :return: a random image from splashbase.co
    """
    splashbase_rest_interface = 'http://www.splashbase.co/api/v1/images/random'
    result = urllib.request.urlopen(splashbase_rest_interface).read()
    json_result = json.loads(result)
    image = get_image(json_result['url'])
    while image is None:
        print(json_result['url'] + "\n no image loaded")
        result = urllib.request.urlopen(splashbase_rest_interface).read()
        json_result = json.loads(result)
        image = get_image(json_result['url'])
    if resize:
        (width, height) = (image.shape[0], image.shape[1])
        width = max(min_size[0], min(width, max_size[0]))
        height = max(min_size[1], min(height, max_size[1]))
        return cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)
    else:
        return image


def search_image_urls(text, max=50, verbose=True):
    """
    :param text: search query for flickr api
    :param max: maximum number of images
    :param verbose: print progress
    :return: list of urls
    """
    extras = 'url_c, url_l, url_o'
    page = 1
    urls = []
    while True:
        json_result = flickr.photos.search(text=text, per_page=100, extras=extras, page=page)
        photos = json_result['photos']['photo']
        for photo in photos:
            url = ''
            if 'url_o' in photo:
                url = photo['url_o']
            if 'url_l' in photo:
                url = photo['url_l']
            if 'url_c' in photo:
                url = photo['url_c']
            if url:
                urls.append(url)
                if verbose:
                    bar = vis.visualize_progress(val=len(urls), max_val=max, description="images found.", bar_width=30)
                    print(bar)
                if len(urls) >= max:
                    return urls
        page = page + 1


def is_power_of_two(number):
    """
    :param number: number to test
    :return: True => if number is the power of two, False else
    """
    half = number / 2.0
    while half >= 1.0 and not half == 1.0:
        half = half / 2.0
    return half == 1.0


def get_next_power_of_two(number):
    """
    :param number: input number
    :return: the next value which is the power of two and greater than number
    """
    pot = 2
    while pot < number:
        pot = pot * 2
    return pot


def image_from_url(url):
    """
    :param url: source of image
    :return: array of image data
    """
    url_response = urllib.request.urlopen(url)
    img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
    img = cv2.imdecode(img_array, -1)
    return img


def make_square(image, min_size=1024):
    """
    :param image: input iamge
    :param min_size: minimal size
    :return: retuns a squared version of the input image without skewing it
    """
    x = image.shape[0]
    y = image.shape[1]
    size = max(min_size, x, y)
    if not is_power_of_two(size):
        size = get_next_power_of_two(size)
    if not x == size or not y == size:
        border_v = int((size - y) / 2.0)
        border_x = int((size - x) / 2.0)
        new_im = cv2.copyMakeBorder(image, border_x, border_x, border_v, border_v, cv2.BORDER_CONSTANT)
        new_im = cv2.resize(new_im, (size, size), interpolation=cv2.INTER_CUBIC)
        return new_im
    else:
        return image


def store_images_from_url(urls, output_dir, verbose=True):
    """
    :param urls: list of urls
    :param output_dir: destination directory for storing images
    :param verbose: print progress
    :return:
    """
    n = 0
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    for url in urls:
        img = image_from_url(url)
        cv2.imwrite(os.path.join(output_dir, str(n) + '.jpg'), img)
        n = n + 1
        if verbose:
            bar = vis.visualize_progress(n, len(urls), 'images stored.', 20)
            print(bar)


def download_images(search_term, number_of_images, output_dir):
    """
    :param search_term: 
    :param number_of_images:
    :param output_dir:
    :return:
    """
    urls = search_image_urls(text=search_term, max=number_of_images)
    store_images_from_url(urls=urls, output_dir=output_dir)
