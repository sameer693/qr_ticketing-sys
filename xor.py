key='5244215082696420'
hash='05a8d86ce4'
ans='saikikusuo'
def xor_strings(s, t):
    """XOR two strings together"""
    return ''.join(map(chr, [ord(a) ^ ord(b) + ord('a') for a, b in zip(s, t)]))

def symmetric_encryption(key, hash):
    """Perform symmetric encryption using XOR operation"""
    #hash to base 8 from base 16
    hash = int(hash, 16)
    hash = oct(hash)
    return xor_strings(key, hash)

key = 'â±úüÿúâääø'
#convert key to base 16
key = int(key, 8)
print(key)

hash = '05a8d86ce4'
encrypted_data = symmetric_encryption(key, hash)
print(encrypted_data)