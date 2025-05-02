from credential import generate_key, sign, verify, create_issue_request, sign_issue_request

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


def test_correct_credential():
    attribute_list = [b"private_key", b"restaurant", b"gym", b"cafe"]
    pk, sk = generate_key(attribute_list)

    user_attributes = {
        0: 1234
    }
    request, t = create_issue_request(pk, user_attributes)

    issuer_attributes = {
        1: 1, # Restaurant subscription: True
        2: 0, # Gym subscription: False
        3: 1, # Cafe subscription: True
    }
    sign_issue_request(sk, pk, request, issuer_attributes)
    
    assert True