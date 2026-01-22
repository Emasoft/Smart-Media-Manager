from smart_media_manager.format_rules import match_rule


def test_match_rule_png():
    rule = match_rule(
        extension=".png",
        libmagic=["image/png"],
        puremagic=["png"],
        pyfsig=["png image"],
    )
    assert rule is not None
    assert rule.rule_id == "R-IMG-002"
    assert rule.action == "import"


def test_match_rule_psd_unknown_defaults_to_convert():
    rule = match_rule(
        extension=".psd",
        libmagic=["application/photoshop"],
        puremagic=["psd"],
        pyfsig=["adobe photoshop image"],
        psd_color_mode="unknown",
    )
    assert rule is not None
    assert rule.rule_id == "R-IMG-009"
    assert rule.action == "convert_to_tiff"  # PSD non-RGB → TIFF for Photos compatibility


def test_match_rule_accepts_dotted_puremagic_extension():
    rule = match_rule(extension=".png", libmagic=["image/png"], puremagic=[".png"])
    assert rule is not None
    assert rule.rule_id == "R-IMG-002"
