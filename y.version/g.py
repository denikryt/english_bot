from encoding_tools import TheSoCalledGreatEncoder

encoder = TheSoCalledGreatEncoder()
encoder.load_str('Ö')
encoder.encode('utf-8')

encoded_string = encoder.encoded_data
print(encoded_string)

