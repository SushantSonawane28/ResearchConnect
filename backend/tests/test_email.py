from app.alert_rules import qualifies
from app.email_service import build_match_email


def _build(with_email=True):
    other = {"name": "Dr. Sharma", "organization": "Alpha Institute", "department": "Computer Engineering",
             "domain": "Healthcare AI"}
    if with_email:
        other["email"] = "sharma@alpha.edu"
    return build_match_email("Kunal", other, 87.4, ["3 shared topics/skills: nlp, python, healthcare"],
                             ["nlp", "python", "healthcare"], ["Medical document extraction"], "http://app")


def test_email_contains_details_and_reasons():
    subject, text, html = _build()
    assert "87%" in subject and "Dr. Sharma" in subject
    assert "Alpha Institute" in text and "Healthcare AI" in text
    assert "3 shared topics/skills" in text and "Medical document extraction" in text
    assert "sharma@alpha.edu" in text and "sharma@alpha.edu" in html


def test_email_hides_address_without_consent():
    _, text, html = _build(with_email=False)
    assert "@" not in text.split("Contact:")[1].split("\n")[0]
    assert "sharma@alpha.edu" not in html


def test_html_is_escaped():
    other = {"name": "<script>x</script>", "organization": "A", "department": "", "domain": ""}
    _, _, html = build_match_email("K", other, 50, ["r"], [], [], "http://app")
    assert "<script>" not in html


def test_qualifies_rules():
    s = {"hybrid": 0.35}
    assert qualifies(s, False, 0.30)
    assert not qualifies({"hybrid": 0.20}, False, 0.30)
    assert qualifies({"hybrid": 0.16}, True, 0.30)        # same domain: half threshold
    assert not qualifies({"hybrid": 0.10}, True, 0.30)
