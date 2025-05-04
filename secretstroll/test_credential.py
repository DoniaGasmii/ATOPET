from credential import (generate_key, sign, verify,
                        create_issue_request, sign_issue_request, obtain_credential,
                        create_disclosure_proof, verify_disclosure_proof)

def test_correct_signature():
    """ Expected message signature workflow works """
    attribute_list = ["gym", "restaurant", "cafe", "username"]
    sk, pk = generate_key(attribute_list)

    messages = [b"testgym", b"testrestaurant", b"testcafe", b"testusername"]
    signature = sign(sk, messages)

    assert verify(pk, signature, messages)


def test_incorrect_signature():
    """ Verification of message signature from an unrelated verifier fails """
    attribute_list = ["gym", "restaurant", "cafe", "username"]
    sk1, pk1 = generate_key(attribute_list) # sign with this one
    sk2, pk2 = generate_key(attribute_list) # verify with this one, should give False

    messages = [b"testgym", b"testrestaurant", b"testcafe", b"testusername"]
    signature = sign(sk1, messages)

    assert not verify(pk2, signature, messages)


def test_correct_credential():
    """ Expected credential workflow works """
    attribute_list = ["private_key", "restaurant", "gym", "cafe"]
    sk, pk = generate_key(attribute_list)

    user_attributes = {
        "private_key": 1234
    }
    request, t = create_issue_request(pk, user_attributes)

    issuer_attributes = {
        "restaurant": 1, # Restaurant subscription: True
        "gym": 0, # Gym subscription: False
        "cafe": 1, # Cafe subscription: True
    }
    blind_signature = sign_issue_request(sk, pk, request, issuer_attributes)

    # disjoint* union of attributes
    attributes = user_attributes | issuer_attributes
    credential = obtain_credential(pk, blind_signature, t, attributes)

    # showing
    hidden_attributes = ["private_key", "gym", "cafe"] # only showing restaurant subscription
    disclosure_proof = create_disclosure_proof(pk, credential, hidden_attributes, b"")

    assert verify_disclosure_proof(pk, disclosure_proof, b"", attribute_list)

def test_incorrect_credential():
    """ A user cannot show their credential successfully to a verifier that isn't related to the issuer """
    attribute_list = ["private_key", "restaurant", "gym", "cafe"]
    sk1, pk1 = generate_key(attribute_list)
    sk2, pk2 = generate_key(attribute_list)

    user_attributes = {
        "private_key": 1234
    }
    request, t = create_issue_request(pk1, user_attributes)

    issuer_attributes = {
        "restaurant": 1, # Restaurant subscription: True
        "gym": 0, # Gym subscription: False
        "cafe": 1, # Cafe subscription: True
    }
    blind_signature = sign_issue_request(sk1, pk1, request, issuer_attributes)

    # disjoint* union of attributes
    attributes = user_attributes | issuer_attributes
    credential = obtain_credential(pk1, blind_signature, t, attributes)

    # showing
    hidden_attributes = ["private_key", "gym", "cafe"] # only showing restaurant subscription
    disclosure_proof = create_disclosure_proof(pk1, credential, hidden_attributes, b"")

    # checks with another public key, as if verifier was not related to issuer
    assert not verify_disclosure_proof(pk2, disclosure_proof, b"", attribute_list)

def test_malicious_attribute():
    """ A user can't modify an issuer-defined attribute """
    attribute_list = ["private_key", "restaurant", "gym", "cafe"]
    sk, pk = generate_key(attribute_list)

    user_attributes = {
        "private_key": 1234
    }
    request, t = create_issue_request(pk, user_attributes)

    issuer_attributes = {
        "restaurant": 1, # Restaurant subscription: True
        "gym": 0, # Gym subscription: False
        "cafe": 1, # Cafe subscription: True
    }
    blind_signature = sign_issue_request(sk, pk, request, issuer_attributes)

    # disjoint* union of attributes
    attributes = user_attributes | issuer_attributes
    attributes["gym"] = 1 # User tries to get a gym POI subscription for free
    credential = obtain_credential(pk, blind_signature, t, attributes)

    # showing
    hidden_attributes = ["private_key", "gym", "cafe"] # only showing restaurant subscription

    message = b"SIGNED MESSAGE"
    disclosure_proof = create_disclosure_proof(pk, credential, hidden_attributes, message)

    assert not verify_disclosure_proof(pk, disclosure_proof, message, attribute_list)

def test_different_message():
    """ Expected credential workflow works """
    attribute_list = ["private_key", "restaurant", "gym", "cafe"]
    sk, pk = generate_key(attribute_list)

    user_attributes = {
        "private_key": 1234
    }
    request, t = create_issue_request(pk, user_attributes)

    issuer_attributes = {
        "restaurant": 1, # Restaurant subscription: True
        "gym": 0, # Gym subscription: False
        "cafe": 1, # Cafe subscription: True
    }
    blind_signature = sign_issue_request(sk, pk, request, issuer_attributes)

    # disjoint* union of attributes
    attributes = user_attributes | issuer_attributes
    credential = obtain_credential(pk, blind_signature, t, attributes)

    # showing
    hidden_attributes = ["private_key", "gym", "cafe"] # only showing restaurant subscription
    signed_message = b"THIS IS SIGNED"
    unsigned_message = b"THIS IS NOT SIGNED"
    disclosure_proof = create_disclosure_proof(pk, credential, hidden_attributes, signed_message)

    assert not verify_disclosure_proof(pk, disclosure_proof, unsigned_message, attribute_list)