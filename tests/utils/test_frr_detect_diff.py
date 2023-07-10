import _utils.frr_detect_diff as UTIL_MOD

##
# Tests setup
##


def _get_config(filename):
    test_path = "tests/utils/data/frr_detect_diff"
    with open(
        f"{test_path}/{filename}",
        encoding="utf-8",
    ) as fd:
        config = fd.read()

    return config


##
# Tests
##


def test_list_changed_objects__no_changes():
    """Test list_changed_objects without diff."""
    reference_config = _get_config("reference_config.txt")
    candidate_config = _get_config("candidate_no_changes.txt")

    changes = UTIL_MOD.list_changed_objects(reference_config, candidate_config)

    assert not changes


def test_list_changed_objects__no_changes():
    """Test list_changed_objects with diff on some objects."""
    reference_config = _get_config("reference_config.txt")
    candidate_config = _get_config("candidate_changes.txt")

    changes = UTIL_MOD.list_changed_objects(reference_config, candidate_config)
    assert changes == {
        "route_maps": ["RM-CLOS-IN"],
        "ipv4_prefix_lists": ["PF-DEFAULT"],
        "community_lists": ["CL-CLOS_SERVER"],
    }
