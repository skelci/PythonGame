import hashlib

def get_random_num(seed, value_to_hash, min=0.0, max=1.0):
    try:
        combined_string = f"{seed}:{str(value_to_hash)}"
        input_bytes = combined_string.encode('utf-8')
    except Exception as e:
        print(f"Error encoding value for hashing: {e}")
        return min 

    hash_object = hashlib.sha256(input_bytes)
    digest_bytes = hash_object.digest()

    hash_int = int.from_bytes(digest_bytes, byteorder='big')

    num_bits = hash_object.digest_size * 8
    max_hash_value_plus_1 = 2**num_bits
    normalized_float = hash_int / max_hash_value_plus_1

    # Scale the normalized float to the desired range
    random_num = min + (normalized_float * (max - min))
    return random_num