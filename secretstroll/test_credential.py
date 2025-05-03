from credential import (generate_key, sign, verify,
                        create_issue_request, sign_issue_request, obtain_credential,
                        create_disclosure_proof, verify_disclosure_proof)

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
    blind_signature = sign_issue_request(sk, pk, request, issuer_attributes)

    # disjoint* union of attributes
    attributes = user_attributes | issuer_attributes
    credential = obtain_credential(pk, blind_signature, t, attributes)

    # showing
    hidden_attributes = [0, 2, 3] # only showing restaurant subscription
    disclosure_proof = create_disclosure_proof(pk, credential, hidden_attributes)

    assert verify_disclosure_proof(pk, disclosure_proof)

def test_incorrect_credential():
    attribute_list = [b"private_key", b"restaurant", b"gym", b"cafe"]
    pk1, sk1 = generate_key(attribute_list)
    pk2, sk2 = generate_key(attribute_list)

    user_attributes = {
        0: 1234
    }
    request, t = create_issue_request(pk1, user_attributes)

    issuer_attributes = {
        1: 1, # Restaurant subscription: True
        2: 0, # Gym subscription: False
        3: 1, # Cafe subscription: True
    }
    blind_signature = sign_issue_request(sk1, pk1, request, issuer_attributes)

    # disjoint* union of attributes
    attributes = user_attributes | issuer_attributes
    credential = obtain_credential(pk1, blind_signature, t, attributes)

    # showing
    hidden_attributes = [0, 2, 3] # only showing restaurant subscription
    disclosure_proof = create_disclosure_proof(pk1, credential, hidden_attributes)

    # checks with another public key, as if verifier was not related to issuer
    assert not verify_disclosure_proof(pk2, disclosure_proof)