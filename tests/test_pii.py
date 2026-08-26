"""PII masker: each pattern kind masks, clean text is untouched, mapping restores."""
import pii


def test_card_number_masked():
    masked, mapping = pii.mask("moja karta 4111 1111 1111 1111 zostala obciazona dwa razy")
    assert "4111" not in masked
    assert "<CARD_1>" in masked
    assert mapping["<CARD_1>"] == "4111 1111 1111 1111"


def test_iban_masked():
    masked, mapping = pii.mask("wyplata na PL61109010140000071219812874 nie doszla")
    assert "PL61" not in masked
    assert "<IBAN_1>" in masked


def test_pesel_masked_as_pesel_not_phone():
    # 11 digits could also match the phone pattern; PESEL must win by order.
    masked, mapping = pii.mask("mój pesel 90010112345, sprawdźcie konto")
    assert "<PESEL_1>" in masked
    assert "90010112345" not in masked


def test_phone_and_email_masked():
    masked, mapping = pii.mask("call me at +48 601 123 456 or mail jan.kowalski@firma.pl")
    assert "<PHONE_1>" in masked
    assert "<EMAIL_1>" in masked
    assert "601" not in masked
    assert "firma.pl" not in masked


def test_clean_text_unchanged():
    text = "jak zrobić zwrot płatności?"
    masked, mapping = pii.mask(text)
    assert masked == text
    assert mapping == {}


def test_mapping_restores_originals():
    text = "karta 4111 1111 1111 1111, mail jan@firma.pl"
    masked, mapping = pii.mask(text)
    restored = masked
    for token, original in mapping.items():
        restored = restored.replace(token, original)
    assert "4111 1111 1111 1111" in restored
    assert "jan@firma.pl" in restored
