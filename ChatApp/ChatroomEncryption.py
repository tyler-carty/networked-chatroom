import random

random_shift = random.randint(1,26)

key = 'abcdefghijklmnopqrstuvwxyz0123456789'


def encryption(shift, to_encrypt):

    """
    Encrypt the string and return the encrypted result
    """

    # Empty string to start with
    result = ''

    # For each character in the string
    for j in str(to_encrypt):
        # Try to shift the value
        try:
            i = (key.index(j) + int(shift)) % 36
            result += key[i]
        # Otherwise, just add the unshifted value
        except ValueError:
            result += j

    # Return the encrypted string
    return result


def decryption(shift, to_decrypt):

    """
        Decrypt the string and return the plain text result
    """

    # Empty string to start with
    result = ''

    # For each character in the string
    for j in str(to_decrypt):
        # Try to shift the values back
        try:
            i = (key.index(j) - int(shift)) % 36
            result += key[i]
        # Otherwise, just add the unshifted value
        except ValueError:
            result += j

    # Return the plain text
    return result
