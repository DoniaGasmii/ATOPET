from credential import generate_key, sign, verify

def test_correct_signature():
    attribute_list = ["gym", "restaurant", "cafe", "username"]
    pk, sk = generate_key(attribute_list)

    messages = [b"testgym", b"testrestaurant", b"testcafe", b"testusername"]
    signature = sign(sk, messages)

    assert verify(pk, signature, messages)

def test_incorrect_signature():
    attribute_list = ["gym", "restaurant", "cafe", "username"]
    pk1, sk1 = generate_key(attribute_list) # sign with this one
    pk2, sk2 = generate_key(attribute_list) # verify with this one, should give False

    messages = [b"testgym", b"testrestaurant", b"testcafe", b"testusername"]
    signature = sign(sk1, messages)

    assert not verify(pk2, signature, messages)