"""Detect a change in FRR config for specfic objects.

Supported:
- route-maps
- prefix-lists
- community-list

It won't expose the change, nor provide the command to solve the diff.

This script will be removed when FRR developers will finish the development of Northbound API.
"""

import re
from collections import defaultdict


def __virtual__():
    return __grains__.get("nos") == "sonic"


def _get_indentation_level(line):
    nb_leading_spaces = len(line) - len(line.lstrip())
    return nb_leading_spaces


def _group_config_per_object(config):
    """Group all config line per objects (one per route-map for instance)."""
    objects = {}
    previous_object = set()
    indentation_previous_object = 0

    for line in config.split("\n"):
        stripped_line = line.lstrip()

        if stripped_line == "!":
            continue

        current_indentation = _get_indentation_level(line)

        if current_indentation > indentation_previous_object:
            previous_object.add(stripped_line)
        else:
            objects[stripped_line] = set()
            previous_object = objects[stripped_line]
            indentation_previous_object = current_indentation

    return objects


def _filter_objects(config):
    """Keep supported objects only."""
    regex_mapping = {
        "route_maps": r"route-map (\S+).*",
        "ipv4_prefix_lists": r"ip prefix-list (\S+).*",
        "ipv6_prefix_lists": r"ipv6 prefix-list (\S+).*",
        "community_lists": r"bgp community-list \S+ (\S+).*",
    }
    objects = {
        "route_maps": {},
        "ipv4_prefix_lists": {},
        "ipv6_prefix_lists": {},
        "community_lists": {},
    }

    for key, value in config.items():
        for object_type, regex in regex_mapping.items():
            matches = re.match(regex, key)
            if not matches:
                continue

            if matches.group(1) not in objects[object_type]:
                objects[object_type][matches.group(1)] = []

            if value:
                objects[object_type][matches.group(1)].append(value)
            else:
                objects[object_type][matches.group(1)].append(key)

    return objects


def get_objects(config):
    """Get all objects from config."""
    groups = _group_config_per_object(config)
    objects = _filter_objects(groups)

    return objects


def list_changed_objects(reference_config, candidate_changes):
    """List all objects which differ between reference config and candidate changes.

    This only checks if candidate changes would change the reference configuration.

    Supports only:
    - route-maps
    - prefix-lists
    - community-lists
    """
    reference_objects = get_objects(reference_config)
    candidate_objects = get_objects(candidate_changes)

    detected_diff = defaultdict(list)
    for section, objects in candidate_objects.items():
        for name, statements in objects.items():
            if statements != reference_objects.get(section, {}).get(name):
                detected_diff[section].append(name)

    return dict(detected_diff)


def is_different(reference_config, candidate_changes):
    """Check if there are difference detected between conf and candidate changes.

    Supports only:
    - route-maps
    - prefix-lists
    - community-lists
    """
    detected_diff = list_changed_objects(reference_config, candidate_changes)

    is_config_different = any((section for section in detected_diff.values()))

    return is_config_different
