import requests
from astropy.io import fits

def load_display_img():
    img_name='TOI+3799-01_Rc_120sec_2022-03-07_182739.fit'

    img_url='https://randommiscfiles.s3.us-west-1.amazonaws.com/TOI+3799-01_Rc_120sec_2022-03-07_182739.fit'

    # save img
    img_data = requests.get(img_url).content
    with open(img_name, 'wb') as handler:
        handler.write(img_data)

    # open with astropy
    hdul = fits.open(img_url)
    hdul.info()


def main():
    load_display_img()


if __name__ == '__main__':
    main()
