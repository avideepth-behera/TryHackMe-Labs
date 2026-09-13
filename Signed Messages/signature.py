import hashlib
from sympy import nextprime
from Crypto.PublicKey import RSA
from Crypto.Signature import pss
from Crypto.Hash import SHA256

# Define the target parameters
user_identifier = b"admin"
payload = b"MESSAGE"

# --- STEP 1: Predictable Prime Derivation ---
base_seed = user_identifier + b"_lovenote_2026_valentine"

# Calculate the first prime
hash_val_p = hashlib.sha256(base_seed).hexdigest()
prime_one = nextprime(int(hash_val_p, 16))

# Calculate the second prime
hash_val_q = hashlib.sha256(base_seed + b"pki").hexdigest()
prime_two = nextprime(int(hash_val_q, 16))

# --- STEP 2: Rebuild the RSA Key ---
modulus = prime_one * prime_two
pub_exp = 65537

totient = (prime_one - 1) * (prime_two - 1)
priv_exp = pow(pub_exp, -1, totient)

forged_rsa_key = RSA.construct(
    (modulus, pub_exp, priv_exp, prime_one, prime_two)
)

# --- STEP 3: Handle the PSS Padding ---
modulus_bits = forged_rsa_key.size_in_bits()
encoded_message_len = (modulus_bits - 1 + 7) // 8

hash_obj = SHA256.new(payload)
hash_byte_len = hash_obj.digest_size

available_salt_space = encoded_message_len - hash_byte_len - 2

# --- STEP 4: Sign and Output ---
pss_signer = pss.new(
    forged_rsa_key,
    salt_bytes=available_salt_space
)

final_sig = pss_signer.sign(hash_obj)

print(f"Sender Username: {user_identifier.decode()}")
print(f"Message Content: {payload.decode()}")
print(f"Hex Signature:\n{final_sig.hex()}")